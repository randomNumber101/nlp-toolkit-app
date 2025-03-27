import re
from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import HTMLViz
from backend.types.config import Config
from backend.types.frontendNotifier import FrontendNotifier
from backend.types.operation import ParallelizableOperation
from backend.types.payload import Payload


class WordListScanOperation(ParallelizableOperation):
    def initialize(self, config: Config, notifier: FrontendNotifier):
        self.config = config
        # Get the input column (default is "text")

        self.input_column = self.config.get("input column", "text")

        # Get the word lists configuration
        word_lists_config = self.config.get("Word lists", [])
        self.active_word_lists = {}

        # Process each word list: only include active ones
        for wl in word_lists_config:
            active = wl.get("active", True)
            if not active:
                continue
            list_name = wl.get("name", "unnamed")
            words_config = wl.get("list of words", [])
            patterns = []
            for entry in words_config:
                word = entry.get("word", "")
                is_regex = entry.get("is regex", False)
                if not word:
                    continue
                try:
                    if is_regex:
                        # Compile the provided regex pattern
                        pattern = re.compile(word, re.IGNORECASE)
                    else:
                        # For plain words, use word boundaries for whole-word matching
                        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    patterns.append(pattern)
                except Exception as e:
                    notifier.log(f"Error compiling pattern '{word}' in word list '{list_name}': {e}", LogLevels.ERROR)
            self.active_word_lists[list_name] = patterns

        notifier.log("Word List Scan Operation initialized successfully.", LogLevels.INFO)

    def getColumnNames(self):
        # Each active word list will create an output column with its name.
        return list(self.active_word_lists.keys())

    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str):
        # If there is no valid text, return 0 matches for each active word list.
        if not text or not isinstance(text, str):
            notifier.sendStatus(StepState.SUCCESS, progress=100)
            return {name: 0 for name in self.active_word_lists.keys()}

        total_lists = len(self.active_word_lists)
        result = {}
        current = 0

        # For each active word list, scan the text and count matches.
        for list_name, patterns in self.active_word_lists.items():
            count = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                count += len(matches)
            result[list_name] = count
            current += 1
            # Report progress based on the number of word lists processed.
            progress = int((current / total_lists) * 100)
            notifier.sendStatus(StepState.RUNNING, progress=progress)

        # Build an HTML visualization to display the scan results.
        if len(text) > 300:
            text = text[:300] + "..."

        viz_html = f"""
        <div style="border:1px solid #ddd; border-radius: 4px; padding: 10px; margin: 10px 0; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 5px 0; color: #333;">Word List Scan</h4>
            <p style="margin: 5px 0;"><strong>Input Text:</strong> {text}</p>
            {''.join([f'<p style="margin: 5px 0;"><strong>{name}:</strong> {count} matches</p>' for name, count in result.items()])}
        </div>
        """
        payload.addVisualization(HTMLViz(viz_html))
        notifier.sendStatus(StepState.SUCCESS, progress=100)
        return list(count for name, count in result.items())
