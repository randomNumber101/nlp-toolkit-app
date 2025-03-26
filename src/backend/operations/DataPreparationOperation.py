
from collections import Counter

from backend.generaltypes import ParallelizableTextOperation, Config, FrontendNotifier, Payload
from backend.operations.operation_utils import load_spacy_model_on_demand
from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import HTMLViz


class DataPreparationOperation(ParallelizableTextOperation):

    def initialize(self, config: Config, notifier: FrontendNotifier):
        super().initialize(config, notifier)
        language = self.config["remove stopwords"]["language"]
        self.nlp = load_spacy_model_on_demand(language, notifier)
        self.do_stopwords = config["remove stopwords"]["activate"]
        self.do_lowercase = config["lowercase"]
        self.do_no_ascii = config["remove non-ascii"]
        notifier.log("Data Preparation Operation initialized!")



    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str) -> str:

        stopword_counter = Counter()

        # Remove stopwords (and count those removed) if requested.
        if self.do_stopwords:
            doc = self.nlp(text)
            filtered_tokens = []
            for token in doc:
                if token.is_stop:
                    stopword_counter[token.text.lower()] += 1
                else:
                    filtered_tokens.append(token.text)
            text = ' '.join(filtered_tokens)

        # Combine lowercasing and ASCII removal in one pass.
        if self.do_lowercase or self.do_no_ascii:
            new_chars = []
            for c in text:
                # Lowercase if enabled.
                new_char = c.lower() if self.do_lowercase else c
                # Remove non-ASCII characters if enabled.
                if self.do_no_ascii and ord(new_char) >= 128:
                    continue
                new_chars.append(new_char)
            text = ''.join(new_chars)

        # Prepare a visually improved HTML visualization for stopword removal.
        top_stopwords = stopword_counter.most_common(10)
        stats_html = """
        <div style="
              font-family: Arial, sans-serif;
              padding: 20px;
              border: 1px solid #ccc;
              background: #fefefe;
              box-shadow: 0 4px 8px rgba(0,0,0,0.1);
              border-radius: 8px;
              max-width: 600px;
              margin: 0 auto;">
            <h4 style="text-align: center; color: #333; margin-bottom: 16px;">Stopwords Removed</h4>
            <div style="display: flex; justify-content: center;">
                <ul style="list-style: none; padding: 0; margin: 0;">
        """
        for word, count in top_stopwords:
            stats_html += f"<li style='margin: 4px 0;'><span style='color: #4caf50; font-weight: bold;'>{word}</span>: {count}</li>"
        stats_html += """
                </ul>
            </div>
        </div>
        """

        payload.addVisualization(HTMLViz(stats_html))
        notifier.sendStatus(StepState.SUCCESS, progress=100.0)
        return text
