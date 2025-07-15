from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import datetime

class OptimizedHoldingBase(BaseModel):
    symbol: str
    quantity: float
    target_allocation: float

class OptimizedHoldingCreate(OptimizedHoldingBase):
    pass

class OptimizedHolding(OptimizedHoldingBase):
    # If you store an ID from the database or have other fields, add them here
    # id: Optional[int] = None 

    class Config:
        orm_mode = True # This allows the model to be created from ORM objects

class OptimizedPortfolioBase(BaseModel):
    optimized_holdings: Optional[List[OptimizedHolding]] = []
    # Add other fields from the Dash app's 'custom_portfolio' if needed
    # e.g., summary: Optional[str] = None

class OptimizedPortfolioCreate(OptimizedPortfolioBase):
    pass

class OptimizedPortfolio(OptimizedPortfolioBase):
    # If you store an ID from the database or have other fields, add them here
    # id: Optional[int] = None
    pass 

# ---- Models for Portfolio Dashboard ----

class Position(BaseModel):
    symbol: str
    quantity: float

class HoldingPerformance(BaseModel):
    symbol: str
    quantity: float
    value: float
    daily_change: float # Can be absolute or percentage, clarify based on usage
    daily_change_percent: float # Added for clarity

class PortfolioMetricValues(BaseModel):
    total_value: float
    daily_return: float # Percentage
    ytd_return: float # Percentage

class RiskMetricValues(BaseModel):
    volatility: float
    sharpe_ratio: float
    diversification_score: float
    risk_assessment: str
    recommendations: List[str]

class PortfolioAllocationDataPoint(BaseModel):
    label: str # e.g., stock symbol
    value: float # e.g., monetary value or percentage

class PortfolioChartDataPoint(BaseModel):
    timestamp: str  # ISO format string that JavaScript can parse with new Date()
    value: float

class PortfolioDashboardData(BaseModel):
    # For Portfolio Summary section (Allocation Chart + Risk Analysis)
    allocation_chart_data: Optional[List[PortfolioAllocationDataPoint]] = None
    risk_metrics: Optional[RiskMetricValues] = None
    
    # For Performance Charts section
    performance_chart_data: Optional[List[PortfolioChartDataPoint]] = None
    
    # For Holdings Table & Metrics Cards
    holdings_performance: Optional[List[HoldingPerformance]] = None
    portfolio_summary_metrics: Optional[PortfolioMetricValues] = None
    
    # Placeholders for currently static/mocked sections from Dash
    # quick_actions: Optional[List[Dict[str, str]]] = None # e.g. [{"label": "Rebalance", "action_id": "rebalance"}]
    # market_summary: Optional[Dict[str, str]] = None # e.g. {"sp500": "+0.5%", "nasdaq": "+0.2%"}
    
    user_has_portfolio: bool = False
    message: Optional[str] = None # For errors or info like "No portfolio found" 