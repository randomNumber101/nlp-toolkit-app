import spacy
from collections import Counter

from backend.generaltypes import ParallelizableTextOperation, Config, FrontendNotifier, Payload
from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import HTMLViz


class DataPreparationOperation(ParallelizableTextOperation):

    def initialize(self, config: Config):
        super().initialize(config)
        self.nlp = spacy.load(self.config["remove stopwords"]["language"])
        self.do_stopwords = config["remove stopwords"]["activate"]
        self.do_lowercase = config["lowercase"]
        self.do_no_ascii = config["remove non-ascii"]
        self.stopword_counter = Counter()


    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str) -> str:

        stats = Counter()
        if self.do_stopwords:
            doc = self.nlp(text)
            filtered_tokens = []
            for token in doc:
                if not token.is_stop:
                    filtered_tokens.append(token.text)
                else:
                    self.stopword_counter[token.text.lower()] += 1
            text = ' '.join(filtered_tokens)
            stats["stop_words_removed"] += len(doc) - len(filtered_tokens)

        # Convert text to lowercase
        if self.do_lowercase:
            original_upper = sum(1 for c1, c2 in zip(text, text.lower()) if c1.isupper() and c2.islower())
            text = text.lower()
            stats["text_lowercased"] += original_upper

        # Remove non-ASCII characters
        if self.do_no_ascii:
            cleaned_text = ''.join(c for c in text if ord(c) < 128)
            removed = len(text) - len(cleaned_text)
            text = cleaned_text
            stats["non_ascii_removed"] += removed

        # Prepare visualization for the current cell
        top_stopwords = self.stopword_counter.most_common(10)
        top_stopwords_html = "<ul>"
        for word, count in top_stopwords:
            top_stopwords_html += f"<li><strong>{word}:</strong> {count}</li>"
        top_stopwords_html += "</ul>"

        stats_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h4 style="color: #333; text-align: center;">Cell Data Preparation Statistics</h4>
            <ul style="list-style-type: none; padding: 0;">
                <li><strong>Stop Words Removed:</strong> {stats['stop_words_removed']}</li>
                <li><strong>Text Lowercased:</strong> {stats['text_lowercased']}</li>
                <li><strong>Non-ASCII Characters Removed:</strong> {stats['non_ascii_removed']}</li>
            </ul>
            <h5 style="color: #333;">Top 10 Most Occurring Stop Words</h5>
            {top_stopwords_html}
        </div>
        """

        # Add visualization to payload for the current cell
        payload.addVisualization(HTMLViz(stats_html))

        notifier.sendStatus(StepState.SUCCESS, progress=100.0)
        return text
