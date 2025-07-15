from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.services.news_service import NewsService
from app.services.ai_service import AIService
from app.models.news_models import MarketNewsResponse, NewsArticle, NewsSource
from app.models.ai_insights_models import MarketSentiment

router = APIRouter()

@router.get("/market", response_model=MarketNewsResponse)
async def get_market_news_endpoint(
    limit: int = 10, 
    news_service: NewsService = Depends(NewsService)
):
    """Fetches general market news articles."""
    try:
        articles = news_service.get_market_news(limit=limit)
        return MarketNewsResponse(articles=articles)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Failed to fetch market news: {str(e)}")

@router.get("/sentiment", response_model=MarketSentiment)
async def get_market_sentiment_endpoint(
    news_service: NewsService = Depends(NewsService),
    ai_service: AIService = Depends(AIService)
):
    """Fetches latest market news and provides AI-driven sentiment analysis."""
    try:
        # Fetch a small number of recent news items for sentiment analysis
        articles_for_sentiment = news_service.get_market_news(limit=5) 
        
        # The AIService.get_market_sentiment expects a list of dicts
        raw_sentiment = ai_service.get_market_sentiment(articles_for_sentiment)
        return MarketSentiment(**raw_sentiment)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Failed to get market sentiment: {str(e)}") 