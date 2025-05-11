from backend.operations.operation_utils import load_sentence_transformer, load_transformer
from backend.transferObjects.eventTransferObjects import StepState, LogLevels

from backend.transferObjects.visualization import PlotlyViz, MultiVisualization
from backend.types.config import Config
from backend.types.frontendNotifier import FrontendNotifier
from backend.types.operation import StepOperation
from backend.types.payload import Payload


class TextDataset:
    """Empty shell - real implementation moved to compute_embeddings()"""
    pass


class BertTopicOperation(StepOperation):
    """
    Operation class for BERTopic modeling with optional verbose progress reporting.
    """

    def initialize(self, config: Config, notifier: FrontendNotifier):
        """Delayed imports for BERTopic core functionality"""
        super().initialize(config, notifier)

        # Lazy-load heavy dependencies
        notifier.log("Importing BERTopic dependencies...", LogLevels.INFO)
        notifier.log("This may take a while...", LogLevels.WARN)
        from bertopic import BERTopic
        from bertopic.vectorizers import ClassTfidfTransformer

        notifier.log("Done.", LogLevels.INFO)


        # Common configurations
        self.config = config
        self.input_column = config.get("input column", "text")
        self.output_column = config.get("output columns prefix", "topic_")
        self.language = config["topic modeling"]["language"]

        if self.language == "german":
            from spacy.lang.de.stop_words import STOP_WORDS
        else:
            from spacy.lang.en.stop_words import STOP_WORDS



        self.cluster_size = config["topic modeling"]["min_cluster_size"]
        self.vectorizer_config = config["topic modeling"]["vectorizer"].get_values()
        self.use_verbose = config["topic modeling"].get("Use verbose progress reporting", False)

        notifier.log("Initializing models...", LogLevels.INFO)
        ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

        notifier.log("Loading BERTopic embedding model from internal storage...", LogLevels.INFO)

        # Load from local cache, inject into pipeline
        emb_model = load_sentence_transformer("all-MiniLM-L6-v2")

        self.topic_model = BERTopic(
            embedding_model=emb_model,
            language=self.language,
            min_topic_size=self.cluster_size,
            ctfidf_model=ctfidf_model
        )

        from sklearn.feature_extraction.text import CountVectorizer
        if self.vectorizer_config:
            self.topic_model.vectorizer_model = CountVectorizer(stop_words=list(STOP_WORDS), **self.vectorizer_config)
        else:
            self.topic_model.vectorizer_model = CountVectorizer(stop_words=list(STOP_WORDS))

        if self.use_verbose:
            self._init_verbose_mode(notifier)

    def _init_verbose_mode(self, notifier):
        """Delayed imports for verbose mode components"""
        from transformers import DistilBertModel, DistilBertTokenizer
        import torch

        notifier.log("Verbose progress reporting enabled", LogLevels.INFO)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        notifier.log(f"Initializing DistilBERT model and tokenizer for {self.language}...", LogLevels.INFO)

        self.tokenizer, self.embedding_model = load_transformer(
            "distilbert-base-multilingual-cased"
        )

        if torch.cuda.device_count() > 1:
            notifier.log(f"Using {torch.cuda.device_count()} GPUs", LogLevels.INFO)
            self.embedding_model = torch.nn.DataParallel(self.embedding_model)

        self.embedding_model.to(self.device).eval()
        self.batch_size = self.config["topic modeling"].get("batch_size", 64)

    def compute_embeddings(self, texts, notifier):
        """Delayed imports for embedding computation"""
        import numpy as np
        import torch
        from torch.utils.data import DataLoader
        from torch.cuda.amp import autocast

        # Define dataset class here to defer torch imports
        class TextDataset(torch.utils.data.Dataset):
            def __init__(self, texts, tokenizer, max_length=512):
                self.texts = texts
                self.tokenizer = tokenizer
                self.max_length = max_length

            def __len__(self): return len(self.texts)

            def __getitem__(self, idx):
                return self.tokenizer(
                    self.texts[idx],
                    padding='max_length',
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors='pt'
                )

        notifier.log("Starting embedding creation...", LogLevels.INFO)
        notifier.sendStatus(StepState.RUNNING, progress=10)

        dataset = TextDataset(texts, self.tokenizer)
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=4,
            pin_memory=True,
            prefetch_factor=2,
            persistent_workers=True
        )

        embeddings = []
        total_batches = len(dataloader)
        for i, batch in enumerate(dataloader, 1):
            with torch.no_grad():
                with autocast():  # Enable mixed precision
                    input_ids = batch['input_ids'].squeeze(1).to(self.device, non_blocking=True)
                    attention_mask = batch['attention_mask'].squeeze(1).to(self.device, non_blocking=True)
                    outputs = self.embedding_model(input_ids=input_ids, attention_mask=attention_mask)

                    # Compute mean of the last hidden state as sentence embeddings
                    last_hidden_state = outputs.last_hidden_state
                    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
                    masked_hidden_state = last_hidden_state * mask
                    summed = torch.sum(masked_hidden_state, dim=1)
                    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
                    mean_embeddings = summed / counts
                    embeddings.append(mean_embeddings.cpu().numpy())

            # Update progress
            progress = 10 + (i / total_batches) * 30  # Embedding takes from 10% to 40%
            notifier.sendStatus(StepState.RUNNING, progress=int(progress))

        embeddings = np.vstack(embeddings)
        notifier.sendStatus(StepState.RUNNING, progress=40)
        notifier.log("Embedding creation completed.", LogLevels.INFO)
        return embeddings

    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
        """Delayed pandas import"""
        import pandas as pd

        try:
            data: pd.DataFrame = payload.data

            # Check if input column exists
            if self.input_column not in data.columns:
                notifier.log(f"Column '{self.input_column}' not found in input data.", LogLevels.ERROR)
                return StepState.FAILED

            # Check if input column is empty
            if data[self.input_column].empty:
                notifier.log(f"Input column '{self.input_column}' is empty. Cannot perform topic modeling.",
                             LogLevels.ERROR)
                return StepState.FAILED

            texts = data[self.input_column].tolist()

            notifier.log("Starting BERTopic modeling process...", LogLevels.INFO)
            notifier.sendStatus(StepState.RUNNING, progress=0)

            if self.use_verbose:
                # Verbose Mode: Manual Embedding Creation
                embeddings = self.compute_embeddings(texts, notifier)

                # Fitting BERTopic with precomputed embeddings
                notifier.log("Fitting BERTopic model to embeddings...", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=40)
                self.topic_model.fit(texts, embeddings=embeddings)
                notifier.log("BERTopic model fitting completed.", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=60)

                # Transforming data with embeddings
                notifier.log("Transforming data to assign topics...", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=70)
                topics, probs = self.topic_model.transform(texts, embeddings=embeddings)
                notifier.log("Topic assignment completed.", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=85)
            else:
                # Original Mode: Standard BERTopic Workflow
                # Fitting BERTopic
                notifier.log("Fitting BERTopic model to data...", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=10)
                self.topic_model.fit(texts)
                notifier.log("BERTopic model fitting completed.", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=50)

                # Transforming data
                notifier.log("Transforming data to assign topics...", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=70)
                topics, probs = self.topic_model.transform(texts)
                notifier.log("Topic assignment completed.", LogLevels.INFO)
                notifier.sendStatus(StepState.RUNNING, progress=85)

            # Post-processing: Logging and Visualization
            topic_freq = self.topic_model.get_topic_freq()

            # Log the number of topics found
            num_topics = len(topic_freq)
            notifier.log(f"Number of topics generated: {num_topics}", LogLevels.INFO)

            # Check if any topics were generated
            if num_topics == 0:
                notifier.log("No topics were generated. Adjust types or check input data.", LogLevels.ERROR)
                return StepState.FAILED

            # Add results to the DataFrame
            data[f"{self.output_column}id"] = topics
            data[f"{self.output_column}words"] = [
                ", ".join([word for word, _ in self.topic_model.get_topic(topic)]) if topic != -1 else "N/A"
                for topic in topics
            ]

            # Determine the number of topics to visualize
            top_n = min(10, num_topics)
            notifier.log(f"Visualizing top {top_n} topics.", LogLevels.INFO)
            notifier.sendStatus(StepState.RUNNING, progress=90)

            # Prepare visualizations
            bar_chart = self.topic_model.visualize_barchart(top_n_topics=top_n)
            hierarchy = self.topic_model.visualize_hierarchy()
            heatmap = self.topic_model.visualize_heatmap()

            # Add Plotly visualizations to the payload
            multi_viz = MultiVisualization(
                [PlotlyViz(bar_chart), PlotlyViz(hierarchy), PlotlyViz(heatmap)],
                render_type="tabbed",
                tab_names=["Bar Chart", "Hierarchy", "Heatmap"]
            )
            payload.addVisualization(multi_viz)

            # Update payload data
            payload.data = data
            notifier.sendStatus(StepState.RUNNING, progress=100)
            notifier.log("BERTopic modeling completed successfully.", LogLevels.INFO)
            return StepState.SUCCESS

        except Exception as e:
            notifier.log(f"Error: {str(e)}", LogLevels.ERROR)
            return StepState.FAILED