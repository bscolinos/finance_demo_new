from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict
import datetime

class NewsSource(BaseModel):
    id: Optional[str] = None
    name: str

class NewsArticle(BaseModel):
    source: NewsSource
    author: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: HttpUrl
    urlToImage: Optional[HttpUrl] = None
    publishedAt: datetime.datetime
    content: Optional[str] = None

    class Config:
        orm_mode = True

class MarketNewsResponse(BaseModel):
    articles: List[NewsArticle] 