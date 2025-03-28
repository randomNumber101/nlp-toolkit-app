from collections import Counter

from backend.operations.operation_utils import load_spacy_model_on_demand
from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import HTMLViz
from backend.types.config import Config
from backend.types.frontendNotifier import FrontendNotifier
from backend.types.operation import ParallelizableTextOperation
from backend.types.payload import Payload


class KeywordExtractionOperation(ParallelizableTextOperation):

    def initialize(self, config: Config, notifier: FrontendNotifier):
        self.config = config
        # Get input and output column names from the configuration
        self.input_column = self.config.get("input column", "text")
        self.output_column = self.config.get("output column", "keywords")

        # Get keyword extraction specific settings
        extraction_config = self.config.get("keyword extraction", {})
        self.num_keywords = extraction_config.get("num_keywords", 5)
        self.language_model = extraction_config.get("language_model", "en_core_web_sm")

        # Load the spaCy language model (download if necessary)
        self.nlp = load_spacy_model_on_demand(self.language_model, notifier)
        notifier.log("Keyword Extraction Operation initialized successfully.", LogLevels.INFO)

    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str) -> str:
        if not text or not isinstance(text, str):
            notifier.sendStatus(StepState.SUCCESS, progress=100)
            return ""

        # Process the text with spaCy.
        doc = self.nlp(text)

        # Consider only alphabetic tokens that are not stopwords.
        tokens = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]

        # Count token frequencies.
        token_counts = Counter(tokens)

        # Get the most common tokens as keywords.
        most_common = token_counts.most_common(self.num_keywords)
        keywords = [word for word, _ in most_common]

        # Create an HTML visualization for this cell.
        visual_html = f"""
        <div style="border:1px solid #ddd; border-radius: 4px; padding: 10px; margin: 10px 0; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 5px 0; color: #333;">Keyword Extraction</h4>
            <p style="margin: 5px 0;"><strong>Input Text:</strong> {text}</p>
            <p style="margin: 5px 0;"><strong>Extracted Keywords:</strong> {", ".join(keywords)}</p>
        </div>
        """
        payload.addVisualization(HTMLViz(visual_html))

        # Send a success status after processing the cell.
        notifier.sendStatus(StepState.SUCCESS, progress=100)

        # Return the keywords as a comma-separated string.
        return ", ".join(keywords)
