# backend/operations/sentiment_analysis_operation.py

import spacy
from collections import Counter
from transformers import pipeline

from backend.generaltypes import ParallelizableTextOperation, Config, FrontendNotifier, Payload
from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import HTMLViz


class SentimentAnalysisOperation(ParallelizableTextOperation):

    def initialize(self, config: Config):
        super().initialize(config)
        self.do_sentiment = config["sentiment analysis"]["activate"]
        self.language = config["sentiment analysis"]["language"]
        if self.do_sentiment:
            if self.language == "en":
                self.sentiment_pipeline = pipeline("sentiment-analysis",
                                                   model="distilbert-base-uncased-finetuned-sst-2-english")
            elif self.language == "de":
                self.sentiment_pipeline = pipeline("sentiment-analysis", model="oliverguhr/german-sentiment-bert")
            else:
                raise ValueError("Unsupported language for sentiment analysis.")

    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str) -> str:
        try:
            if self.do_sentiment:
                result = self.sentiment_pipeline(text)[0]
                label = result['label']
                score = round(result['score'], 4)

                stats_html = f"""
                <div style="font-family: Arial, sans-serif; padding: 10px;">
                    <h4 style="color: #333; text-align: center;">Sentiment Analysis Result</h4>
                    <p><strong>Label:</strong> {label}</p>
                    <p><strong>Score:</strong> {score}</p>
                </div>
                """

                payload.addVisualization(HTMLViz(stats_html))

            notifier.sendStatus(StepState.SUCCESS, progress=100.0)
            return text

        except Exception as e:
            notifier.log(f"Error in sentiment analysis: {e}", LogLevels.ERROR)
            notifier.sendStatus(StepState.FAILED, progress=100.0)
            return text
