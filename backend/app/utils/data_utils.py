from typing import Dict, List, Any
import random # For mock data generation
import numpy as np # For calculations if needed, though mock may not require it

# Placeholder for format_currency and format_percentage if needed by other parts, 
# though for API usually raw numbers are better.
# def format_currency(value): return f"${value:,.2f}"
# def format_percentage(value): return f"{value:.2f}%"

def calculate_portfolio_metrics(performance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Calculates various portfolio metrics based on performance data.
    The `performance_data` is expected to be the output of StockService.get_portfolio_performance.
    Output structure based on `dash_app.py` callbacks `update_portfolio_analysis` and `update_portfolio_data`.
    """
    holdings = performance_data.get("holdings", [])
    total_value = performance_data.get("total_value", 0)
    
    # --- Overall Portfolio Summary Metrics ---
    # Mock daily return for the whole portfolio
    daily_return_percent = 0
    if total_value > 0:
        # Sum of individual daily changes / yesterday's total value (approximate)
        total_daily_absolute_change = sum(h.get('daily_change', 0) for h in holdings)
        # Approximate yesterday's value. For a more accurate calculation, historical data is needed.
        yesterdays_total_value = total_value - total_daily_absolute_change 
        if yesterdays_total_value != 0:
            daily_return_percent = (total_daily_absolute_change / yesterdays_total_value) * 100
        else: # if portfolio started from 0 yesterday
             daily_return_percent = float('inf') if total_daily_absolute_change > 0 else 0

    ytd_return_percent = random.uniform(-5, 15) # Mock YTD return

    portfolio_summary_metrics = {
        "total_value": total_value,
        "daily_return": round(daily_return_percent, 2),
        "ytd_return": round(ytd_return_percent, 2)
    }

    # --- Risk Metrics ---
    # These are highly dependent on actual stock data and financial calculations.
    # The mocks here are very simplistic.
    num_holdings = len(holdings)
    volatility = random.uniform(5, 25) # Mock annual volatility %
    sharpe_ratio = random.uniform(0.5, 2.5) 
    
    # Simple diversification score: 1 for >5 stocks, 0.5 for 2-5, 0.1 for 1 stock.
    if num_holdings > 5:
        diversification_score = random.uniform(0.7, 1.0)
    elif num_holdings >= 2:
        diversification_score = random.uniform(0.4, 0.7)
    elif num_holdings == 1:
        diversification_score = random.uniform(0.1, 0.4)
    else:
        diversification_score = 0.0

    risk_assessment = "Moderate Risk"
    if diversification_score < 0.3 or volatility > 20:
        risk_assessment = "Higher Risk"
    elif diversification_score > 0.7 and volatility < 10:
        risk_assessment = "Lower Risk"

    recommendations = [
        "Regularly review your portfolio against your investment goals.",
        "Consider rebalancing if allocations drift significantly."
    ]
    if diversification_score < 0.5:
        recommendations.append("Consider diversifying across more assets or sectors.")

    risk_metrics_calculated = {
        "volatility": round(volatility, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "diversification_score": round(diversification_score, 2),
        "risk_assessment": risk_assessment,
        "recommendations": recommendations
    }

    return {
        "portfolio_summary_metrics": portfolio_summary_metrics,
        "risk_metrics": risk_metrics_calculated,
        "holdings_performance": holdings # Pass through for direct use if needed
    } 