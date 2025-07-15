from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from app.models.user_models import UserData
from app.models.portfolio_models import OptimizedPortfolio
from app.models.ai_insights_models import PortfolioAnalysis, MarketSentiment

class FinancialPlanRequest(BaseModel):
    user_name: str
    current_savings: Optional[float] = 0
    annual_income: Optional[float] = 0
    investment_goals: Optional[str] = ""

class FinancialPlanResponse(BaseModel):
    user_data: UserData
    pages: List[str]
    # The portfolio message will be constructed on the frontend,
    # but we send the raw data needed.
    # We can send the optimized_portfolio directly if it exists.
    optimized_portfolio: Optional[Union[OptimizedPortfolio, Dict[str, Any]]] = None
    portfolio_analysis: Optional[Union[PortfolioAnalysis, Dict[str, Any]]] = None
    message: Optional[str] = None # For errors or simple status messages
    error: Optional[str] = None

class InitialWelcomeDataResponse(BaseModel):
    user_data: Dict[str, Any] # Similar to dcc.Store initial data
    base_pages: List[str]
    # Add any other initial data needed for the welcome page, like market insights if static 