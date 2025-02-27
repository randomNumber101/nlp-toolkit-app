# backend/operations/sentiment_analysis_operation.py
from abc import ABC

import spacy
from collections import Counter
from transformers import pipeline

from backend.generaltypes import ParallelizableTextOperation, Config, FrontendNotifier, Payload, ParallelizableOperation
from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.transferObjects.visualization import HTMLViz

import en_core_web_md
import de_core_news_md


class SentimentAnalysisOperation(ParallelizableOperation, ABC):

    def initialize(self, config: Config, notifier: FrontendNotifier):
        super().initialize(config, notifier)
        self.text_sample_size = 400
        self.language = config["sentiment analysis"]["language"]

        self.output_prefix = config["sentiment analysis"].get("output columns prefix", "sentiment_")

        notifier.log("Initializing Sentiment Analysis Operation for language " + self.language, LogLevels.INFO)
        notifier.log("When using this operation the first time, it might take a while downloading the according model...", LogLevels.WARN)
        if self.language == "en":
            self.sentiment_pipeline = pipeline("sentiment-analysis",
                                               model="distilbert-base-uncased-finetuned-sst-2-english")
        elif self.language == "de":
            self.sentiment_pipeline = pipeline("sentiment-analysis", model="oliverguhr/german-sentiment-bert")
        else:
            raise ValueError("Unsupported language for sentiment analysis.")
        notifier.log("Sentiment Analysis Operation initialized successfully. ", LogLevels.INFO)

    def getColumnNames(self) -> list:
        return [self.output_prefix + "label", self.output_prefix + "score"]

    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str):
        try:
            result = self.sentiment_pipeline(text, padding=True, truncation=True)[0]
            label = result['label']
            score = round(result['score'], 4)

            # Sample text logic
            text_sample = text if len(text) <= self.text_sample_size else text[:self.text_sample_size] + "..."

            # Styling based on label
            label_color = "#52c41a" if label == "POSITIVE" else "#f5222d"

            stats_html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; border-radius: 8px; background: #f9f9f9; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h4 style="color: #333; text-align: center; margin-bottom: 20px;">Sentiment Analysis Result</h4>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #fff; border-radius: 6px; border: 1px solid #ddd;">
                    <div style="flex: 1; margin-right: 10px;">
                        <p style="margin: 0; color: #555;"><strong>Text:</strong></p>
                        <p style="margin: 0; color: #333; font-style: italic;">"{text_sample}"</p>
                    </div>
                    <div style="text-align: center; flex: 0 0 100px;">
                        <p style="margin: 0; font-size: 14px; color: #555;"><strong>Label:</strong></p>
                        <p style="margin: 5px 0; font-size: 16px; font-weight: bold; color: {label_color};">{label}</p>
                    </div>
                    <div style="text-align: center; flex: 0 0 100px;">
                        <p style="margin: 0; font-size: 14px; color: #555;"><strong>Score:</strong></p>
                        <p style="margin: 5px 0; font-size: 16px; font-weight: bold; color: #1890ff;">{score}</p>
                    </div>
                </div>
            </div>
            """

            payload.addVisualization(HTMLViz(stats_html))
            notifier.sendStatus(StepState.SUCCESS, progress=100.0)
            return label, score


        except Exception as e:
            notifier.log(f"Error in sentiment analysis: {e}", LogLevels.ERROR)
            notifier.sendStatus(StepState.FAILED, progress=100.0)
            return None
