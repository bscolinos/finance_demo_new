from pydantic import BaseModel
from typing import List, Optional

class PortfolioAnalysis(BaseModel):
    summary: str = "No summary available."
    risks: List[str] = []
    opportunities: List[str] = []
    recommendations: List[str] = []

class MarketSentiment(BaseModel):
    overall_sentiment: str = "neutral"
    confidence: float = 0.0
    key_factors: List[str] = []
    market_outlook: str = "No outlook available." 