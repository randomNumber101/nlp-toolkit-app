import webview
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
from transformers import DistilBertModel, DistilBertTokenizer
import torch
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.generaltypes import StepOperation, Payload, FrontendNotifier, Config
from backend.transferObjects.visualization import HTMLViz, SimpleTextViz, PlotlyViz, MultiVisualization


class TextDataset(Dataset):
    """
    Dataset class for handling text data during embedding creation.
    Only used in verbose mode.
    """
    def __init__(self, texts, tokenizer, max_length=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.tokenizer(
            self.texts[idx],
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )


class BertTopicOperation(StepOperation):
    """
    Operation class for BERTopic modeling with optional verbose progress reporting.
    """

    def initialize(self, config: Config, notifier: FrontendNotifier):
        """
        Initializes the BertTopicOperation with configurations.

        Args:
            config (Config): Configuration object containing parameters.
            notifier (FrontendNotifier): Notifier for logging and progress updates.
        """
        super(BertTopicOperation, self).initialize(config, notifier)

        # Common configurations
        self.input_column = config.get("input column", "text")
        self.output_column = config.get("output column", "topic")
        self.language = config["topic modeling"]["language"]
        self.cluster_size = config["topic modeling"]["min_cluster_size"]
        self.vectorizer_config = config["topic modeling"]["vectorizer"]
        self.use_verbose = config["topic modeling"].get("Use verbose progress reporting", False)

        # Initialize BERTopic (common to both modes)
        self.topic_model = BERTopic(language=self.language, min_topic_size=self.cluster_size)
        if self.vectorizer_config:
            self.topic_model.vectorizer_model = CountVectorizer(**self.vectorizer_config)

        if self.use_verbose:
            # Verbose Mode Initializations
            notifier.log("Verbose progress reporting is enabled.", LogLevels.INFO)
            notifier.log("BERTopic will use manual embedding creation with DistilBERT.", LogLevels.INFO)
            notifier.log("This mode will provide more progress updates during the operation but will be much slower.", LogLevels.WARN)
            notifier.log("For faster operation, disable verbose mode in the configuration.", LogLevels.INFO)

            # Initialize device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            notifier.log(f"Using device: {self.device}", LogLevels.INFO)

            # Initialize DistilBERT tokenizer and model for embeddings
            notifier.log(f"Initializing DistilBERT model and tokenizer for {self.language}...", LogLevels.INFO)
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-multilingual-cased')
            self.embedding_model = DistilBertModel.from_pretrained('distilbert-base-multilingual-cased')

            # Utilize multiple GPUs if available
            if torch.cuda.device_count() > 1:
                notifier.log(f"Multiple GPUs detected: {torch.cuda.device_count()}. Using DataParallel.", LogLevels.INFO)
                self.embedding_model = torch.nn.DataParallel(self.embedding_model)

            self.embedding_model.to(self.device)
            self.embedding_model.eval()

            # Set batch size (can be adjusted based on hardware)
            self.batch_size = config["topic modeling"].get("batch_size", 64)
        else:
            # Original Mode Initializations
            notifier.log("Verbose progress reporting is disabled. Using original BERTopic workflow.", LogLevels.INFO)
            notifier.log("BERTopic will use the default workflow for topic modeling.", LogLevels.INFO)
            notifier.log("This mode may be faster but will not provide detailed progress updates.", LogLevels.WARN)
            notifier.log("This operation is quite heavy and may take a while to complete. Do not wonder.", LogLevels.WARN)


    def compute_embeddings(self, texts, notifier):
        """
        Manually compute BERT embeddings with progress updates.

        Args:
            texts (list): List of text documents.
            notifier (FrontendNotifier): Notifier for logging and progress updates.

        Returns:
            np.ndarray: Array of embeddings.
        """
        notifier.log("Starting embedding creation... (This may take a while)", LogLevels.INFO)
        notifier.sendStatus(StepState.RUNNING, progress=10)

        # Create dataset and dataloader with multi-core support
        dataset = TextDataset(texts, self.tokenizer)
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=8,  # Adjust based on CPU cores
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
            notifier.log(f"Processed batch {i}/{total_batches} for embeddings.", LogLevels.DEBUG)

        embeddings = np.vstack(embeddings)
        notifier.sendStatus(StepState.RUNNING, progress=40)
        notifier.log("Embedding creation completed.", LogLevels.INFO)
        return embeddings

    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
        """
        Executes the BERTopic operation based on the configuration.

        Args:
            payload (Payload): Payload containing data.
            notifier (FrontendNotifier): Notifier for logging and progress updates.

        Returns:
            StepState: Result state of the operation.
        """
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
                notifier.log("No topics were generated. Adjust parameters or check input data.", LogLevels.ERROR)
                return StepState.FAILED

            # Add results to the DataFrame
            data[f"{self.output_column}_id"] = topics
            data[f"{self.output_column}_words"] = [
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
            notifier.log(f"Error during BERTopic modeling: {str(e)}", LogLevels.ERROR)
            return StepState.FAILED
