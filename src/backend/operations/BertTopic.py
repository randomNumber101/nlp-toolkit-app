import webview
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.generaltypes import StepOperation, Payload, FrontendNotifier, Config
from backend.transferObjects.visualization import HTMLViz, SimpleTextViz, PlotlyViz, MultiVisualization


class BertTopicOperation(StepOperation):

    def initialize(self, config: Config):
        self.input_column = config.get("input column", "text")
        self.output_column = config.get("output column", "topic")
        self.language = config["topic modeling"]["language"]
        self.cluster_size = config["topic modeling"]["min_cluster_size"]
        self.vectorizer_config = config["topic modeling"]["vectorizer"]

        # Initialize BERTopic
        self.topic_model = BERTopic(language=self.language, min_topic_size=self.cluster_size)
        if self.vectorizer_config:
            self.topic_model.vectorizer_model = CountVectorizer(**self.vectorizer_config)

    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
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

            notifier.log("Analyzing topics. This might take some time...", LogLevels.INFO)
            notifier.sendStatus(StepState.RUNNING, progress=5)

            # Fit BERTopic model
            topics, probs = self.topic_model.fit_transform(data[self.input_column].tolist())
            notifier.log(f"Topics generated: {list(zip(topics, probs))}", LogLevels.DEBUG)
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

            # Prepare visualization
            fig = self.topic_model.visualize_barchart(top_n_topics=top_n)
            # Generate Plotly visualizations
            bar_chart = self.topic_model.visualize_barchart(top_n_topics=10)
            hierarchy = self.topic_model.visualize_hierarchy()
            heatmap = self.topic_model.visualize_heatmap()

            # Add Plotly visualizations to the payload

            multi = MultiVisualization(
                [PlotlyViz(bar_chart), PlotlyViz(hierarchy), PlotlyViz(heatmap)],
                render_type="tabbed",
                tab_names=["Bar Chart", "Hierarchy", "Heatmap"]
            )

            payload.addVisualization(multi)

            # Update payload data
            payload.data = data
            notifier.log("BERTopic modeling completed successfully.", LogLevels.INFO)
            return StepState.SUCCESS

        except Exception as e:
            notifier.log(f"Error during BERTopic modeling: {str(e)}", LogLevels.ERROR)
            return StepState.FAILED




