import time
import pandas as pd
import spacy
import unicodedata

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.generaltypes import StepOperation, Payload, FrontendNotifier, Config
from backend.transferObjects.visualization import SimpleTextViz, HTMLViz


## Needs to be registered in register.py

class DataPreparationOperation(StepOperation):

    def initialize(self, config: Config):
        self.config = config
        self.nlp = spacy.load(config["remove stopwords"]["language"])
        self.column = config["column"]

        self.do_stopwords = config["remove stopwords"]["activate"]
        self.do_lowercase = config["lowercase"]
        self.do_no_ascii = config["remove non-ascii"]

    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
        notifier.log("Data Preparation Operation starting!", LogLevels.INFO)
        start_time = time.time()

        data: pd.DataFrame = payload.data
        input_columns = self.config.get("input_columns", ["text"])

        # Initialize counters for visualization
        stats = {
            "stop_words_removed": 0,
            "text_lowercased": 0,
            "non_ascii_removed": 0
        }

        num_operations = int(self.do_stopwords) + int(self.do_lowercase) + int(self.do_no_ascii)
        total_steps = len(input_columns) * num_operations  # Assuming 3 operations per column
        current_step = 0

        for column in input_columns:
            if column not in data.columns:
                notifier.log(f"Column '{column}' not found in data. Skipping.", LogLevels.WARN)
                continue

            notifier.log(f"Processing column: {column}", LogLevels.INFO)

            # Remove stop words
            if self.do_stopwords:
                notifier.log(f"Removing stop words from column: {column}", LogLevels.INFO)
                data[column] = data[column].apply(self._remove_stop_words, args=(stats,))
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                notifier.sendStatus(StepState.RUNNING, progress)
                notifier.log(f"Progress: {progress}%", LogLevels.INFO)
                time.sleep(0.2)  # Simulate processing time

            # Convert text to lowercase
            if self.do_lowercase:
                notifier.log(f"Converting text to lowercase in column: {column}", LogLevels.INFO)
                data[column] = data[column].apply(self._to_lowercase, args=(stats,))
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                notifier.sendStatus(StepState.RUNNING, progress)
                notifier.log(f"Progress: {progress}%", LogLevels.INFO)
                time.sleep(0.2)

            # Remove non-ASCII characters
            if self.do_no_ascii:
                notifier.log(f"Removing non-ASCII characters from column: {column}", LogLevels.INFO)
                data[column] = data[column].apply(self._remove_non_ascii, args=(stats,))
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                notifier.sendStatus(StepState.RUNNING, progress)
                notifier.log(f"Progress: {progress}%", LogLevels.INFO)
                time.sleep(0.2)

        # Update the payload with the processed data
        payload.data = data

        # Prepare visualization statistics
        stats_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h3 style="color: #333; text-align: center;">Data Preparation Statistics</h3>
            <ul style="list-style-type: none; padding: 0;">
                <li><strong>Stop Words Removed:</strong> {stats['stop_words_removed']}</li>
                <li><strong>Text Lowercased:</strong> {stats['text_lowercased']}</li>
                <li><strong>Non-ASCII Characters Removed:</strong> {stats['non_ascii_removed']}</li>
            </ul>
        </div>
        """

        # Add visualization to payload
        payload.addVisualization(HTMLViz(stats_html))

        notifier.log("Data Preparation Operation completed successfully.", LogLevels.INFO)
        notifier.sendStatus(StepState.RUNNING, 100)
        end_time = time.time()
        notifier.log(f"Total processing time: {end_time - start_time:.2f} seconds", LogLevels.INFO)
        return StepState.SUCCESS

    def _remove_stop_words(self, text: str, stats: dict) -> str:
        doc = self.nlp(text)
        filtered_tokens = [token.text for token in doc if not token.is_stop]
        removed = len(doc) - len(filtered_tokens)
        stats["stop_words_removed"] += removed
        return ' '.join(filtered_tokens)

    def _to_lowercase(self, text: str, stats: dict) -> str:
        lower_text = text.lower()
        # Simple heuristic: count the number of characters that were uppercased
        original_upper = sum(1 for c1, c2 in zip(text, lower_text) if c1.isupper() and c2.islower())
        stats["text_lowercased"] += original_upper
        return lower_text

    def _remove_non_ascii(self, text: str, stats: dict) -> str:
        cleaned_text = ''.join(c for c in text if ord(c) < 128)
        removed = len(text) - len(cleaned_text)
        stats["non_ascii_removed"] += removed
        return cleaned_text
