from __future__ import annotations

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def score(text: str) -> float:
  """Return compound sentiment score in [-1, 1]."""
  return float(analyzer.polarity_scores(text)["compound"])
