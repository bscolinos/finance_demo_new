import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_returns(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily returns from price data"""
    returns = data['Close'].pct_change()
    return returns.fillna(0)

def calculate_portfolio_metrics(performance_data):
    """Calculate portfolio metrics from performance data."""
    total_value = performance_data.get('total_value', 0)
    daily_change = performance_data.get('daily_change', 0)
    
    # Calculate daily return percentage
    daily_return = 0
    if total_value > 0:
        daily_return = (daily_change / total_value) * 100
    
    ytd_return = daily_return * 20  # Just for demonstration
    
    # Calculate basic diversification score
    holdings = performance_data.get('holdings', [])
    diversification_score = 0
    if holdings:
        # Simple diversification score: 1 - (largest position percentage)
        max_value = max([h.get('value', 0) for h in holdings]) if holdings else 0
        diversification_score = 1 - (max_value / total_value if total_value > 0 else 0)
    
    return {
        'total_value': total_value,
        'daily_change': daily_change,
        'daily_return': daily_return,
        'ytd_return': ytd_return,
        'risk_metrics': {
            'diversification_score': diversification_score
        }
    }

def format_currency(value):
    """Format value as currency string."""
    if value >= 1000000:
        return f"${value/1000000:.2f}M"
    elif value >= 1000:
        return f"${value/1000:.2f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value):
    """Format value as percentage string."""
    return f"{value:.2f}%"
