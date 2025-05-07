from transformers import pipeline
from crewai.tools import BaseTool
from typing import Type
from pydantic import PrivateAttr, BaseModel


class FinBERTSentimentAnalysisToolSchema(BaseModel):
    text: str


class FinBERTSentimentAnalysisTool(BaseTool):
    """A tool for analyzing sentiment using the FinBERT model."""
    name: str = "finbert_sentiment_analysis_tool"
    description: str = "A tool for analyzing sentiment using the FinBERT model."
    args_schema: Type[BaseModel] = FinBERTSentimentAnalysisToolSchema
    _classifier: pipeline = PrivateAttr()

    def __init__(self, **kwargs):
        """
        Initialize the FinBERT model as a private attribute to avoid Pydantic validation issues.
        """
        super().__init__(**kwargs)
        self._classifier = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

    def _run(self, text: str):
        """
        Analyzes sentiment of a given text.

        Args:
            text (str): The text to analyze.

        Returns:
            dict: A dictionary with sentiment analysis results.
        """
        try:
            result = self._classifier(text)
            sentiment = result[0]['label']
            score = round(result[0]['score'], 2)

            return {"sentiment": sentiment, "confidence": score}

        except Exception as e:
            return {"error": f"Error performing sentiment analysis: {str(e)}"}


if __name__ == "__main__":
    # Simple local test for FinBERTSentimentAnalysisTool
    tool_instance = FinBERTSentimentAnalysisTool()
    sample_text = "I love this product, it is absolutely fantastic!"
    response = tool_instance.run(text=sample_text)
    print("Sentiment Tool Response:", response)
