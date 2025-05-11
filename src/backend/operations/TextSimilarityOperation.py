from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import MultiVisualization, HTMLViz, SimpleTextViz

import time

from backend.types.config import Config
from backend.types.frontendNotifier import FrontendNotifier
from backend.types.operation import StepOperation
from backend.types.payload import Payload

from backend.operations.operation_utils import load_transformer

class TextSimilarityAnalysisOperation(StepOperation):
    def initialize(self, config: Config, notifier: FrontendNotifier):

        print("Importing TextSimilarity deps")
        import torch
        print("Done.")

        self.config = config
        # Read two input column names from the configuration.
        self.first_column = config.get("first text column", "text1")
        self.second_column = config.get("second text column", "text2")
        # Name of the output column to store similarity scores.
        self.output_column = config.get("output column", "similarity")

        # Transformer model types
        self.model_name = config.get("transformer model", "distilbert-base-uncased")
        notifier.log(f"Loading transformer model and tokenizer '{self.model_name}' for text similarity...",
                     LogLevels.INFO)
        self.tokenizer, self.model = load_transformer(model_name=self.model_name)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        notifier.log("Text Similarity Analysis Operation initialized using transformer model.", LogLevels.INFO)

    def compute_embedding(self, text: str):
        """Handle varying hidden sizes automatically"""
        from torch import no_grad, clamp

        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with no_grad():
            outputs = self.model(**inputs)

        # Unified pooling logic
        if hasattr(outputs, "last_hidden_state"):
            embeddings = outputs.last_hidden_state
        else:
            embeddings = outputs[0]  # Handle models without explicit last_hidden_state

        attention_mask = inputs["attention_mask"]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
        sum_embeddings = (embeddings * input_mask_expanded).sum(dim=1)
        sum_mask = clamp(input_mask_expanded.sum(dim=1), min=1e-9)
        return sum_embeddings / sum_mask

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not (isinstance(text1, str) and isinstance(text2, str)):
            return 0.0

        from torch import cosine_similarity

        emb1 = self.compute_embedding(text1)
        emb2 = self.compute_embedding(text2)

        # Remove unsqueeze(0) - embeddings already have batch dimension
        similarity = cosine_similarity(emb1, emb2, dim=1).item()  # <-- Fix here
        return similarity
    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
        try:
            data = payload.data
            total_rows = len(data)
            if total_rows == 0:
                notifier.log("Input data is empty.", LogLevels.ERROR)
                return StepState.FAILED

            # Ensure that both input columns exist.
            if self.first_column not in data.columns or self.second_column not in data.columns:
                notifier.log("One or both specified text columns do not exist in the data.", LogLevels.ERROR)
                return StepState.FAILED

            similarity_scores = []
            viz_rows_html = ""  # accumulate table rows for visualization

            for idx, row in data.iterrows():
                text1 = row[self.first_column]
                text2 = row[self.second_column]
                sim = self.compute_similarity(text1, text2)
                similarity_scores.append(sim)

                # Report progress and logging.
                progress = ((idx + 1) / total_rows) * 100
                notifier.sendStatus(StepState.RUNNING, progress=progress)
                notifier.log(f"Processed row {idx + 1}/{total_rows}: similarity = {sim:.3f}", LogLevels.DEBUG)

                # Build a snippet for the visualization.
                viz_rows_html += f"<tr><td>{text1}</td><td>{text2}</td><td>{sim:.3f}</td></tr>"
                time.sleep(0.01)  # simulate delay if needed

            # Store the computed similarity scores into the dataframe.
            data[self.output_column] = similarity_scores
            payload.data = data

            # Build a final HTML table as visualization (previewing first 5 rows).
            table_html = """
            <div style="font-family: Arial, sans-serif; padding: 20px;">
              <h3 style="text-align: center;">Text Similarity Analysis Results</h3>
              <table style="width: 100%; border-collapse: collapse;">
                <thead>
                  <tr>
                    <th style="border: 1px solid #ddd; padding: 8px;">First Text</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Second Text</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Similarity Score</th>
                  </tr>
                </thead>
                <tbody>
            """

            # Only use the first 5 rows for visualization.
            viz_rows = viz_rows_html.split("</tr>")[:5]
            for row_html in viz_rows:
                if row_html.strip():
                    table_html += row_html + "</tr>"
            table_html += """
                </tbody>
              </table>
            </div>
            """

            payload.addVisualization(HTMLViz(table_html))
            notifier.log("Text similarity analysis completed successfully.", LogLevels.INFO)
            notifier.sendStatus(StepState.SUCCESS, progress=100)
            return StepState.SUCCESS

        except Exception as e:
            notifier.log(f"Error during text similarity analysis: {str(e)}", LogLevels.ERROR)
            return StepState.FAILED
