from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.services.stock_service import StockService
from app.utils.data_utils import calculate_portfolio_metrics
from app.models.portfolio_models import (
    PortfolioDashboardData,
    Position, 
    HoldingPerformance,
    PortfolioMetricValues,
    RiskMetricValues,
    PortfolioAllocationDataPoint,
    PortfolioChartDataPoint
)
from app.models.user_models import UserData # May not be needed directly here, but good for context

router = APIRouter()

@router.get("/dashboard/{user_id}", response_model=PortfolioDashboardData)
async def get_portfolio_dashboard(
    user_id: str,
    stock_service: StockService = Depends(StockService)
):
    """Provides all necessary data for the portfolio dashboard."""
    
    positions: List[Position] = stock_service.get_optimized_positions(user_id)

    if not positions:
        return PortfolioDashboardData(
            user_has_portfolio=False,
            message="No optimized portfolio found for this user. Please create one on the Welcome page."
        )

    try:
        # 1. Get Holdings Performance (also includes total_value needed for allocation chart)
        # This returns a dict like {"holdings": [...], "total_value": X, ...}
        performance_data_raw = stock_service.get_portfolio_performance(positions)
        
        # Ensure Pydantic models for holdings performance
        holdings_perf_models: List[HoldingPerformance] = [
            HoldingPerformance(**hp) for hp in performance_data_raw.get("holdings", [])
        ]

        # 2. Calculate Overall Portfolio Metrics and Risk Metrics
        # calculate_portfolio_metrics expects the raw performance_data_raw dict
        all_metrics = calculate_portfolio_metrics(performance_data_raw)
        
        portfolio_summary_metrics_model = PortfolioMetricValues(**all_metrics["portfolio_summary_metrics"])
        risk_metrics_model = RiskMetricValues(**all_metrics["risk_metrics"])

        # 3. Prepare Allocation Chart Data (from holdings_performance)
        allocation_chart_data_list: List[PortfolioAllocationDataPoint] = []
        if portfolio_summary_metrics_model.total_value > 0:
            for hp in holdings_perf_models:
                allocation_chart_data_list.append(
                    PortfolioAllocationDataPoint(label=hp.symbol, value=hp.value)
                )
        
        # 4. Get Portfolio Performance Chart Data (Time-series)
        # This returns a list of dicts like {"timestamp": datetime, "value": float}
        chart_data_raw = stock_service.get_portfolio_chart_data(positions)
        print(f"Raw chart data received in router: {chart_data_raw[:2] if chart_data_raw else 'None'}")
        print(f"Raw chart data type: {type(chart_data_raw)}")
        print(f"Raw chart data length: {len(chart_data_raw)}")

        try:
            performance_chart_data_list: List[PortfolioChartDataPoint] = [
                PortfolioChartDataPoint(timestamp=item['timestamp'], value=item['value']) 
                for item in chart_data_raw
            ]
            print(f"Converted performance chart data count: {len(performance_chart_data_list)}")
            if performance_chart_data_list:
                print(f"First chart point: {performance_chart_data_list[0]}")
        except Exception as e:
            print(f"Error converting chart data: {e}")
            # Fallback to empty list if conversion fails
            performance_chart_data_list = []

        return PortfolioDashboardData(
            user_has_portfolio=True,
            allocation_chart_data=allocation_chart_data_list,
            risk_metrics=risk_metrics_model,
            performance_chart_data=performance_chart_data_list,
            holdings_performance=holdings_perf_models,
            portfolio_summary_metrics=portfolio_summary_metrics_model
        )

    except Exception as e:
        print(f"Error generating portfolio dashboard for user {user_id}: {e}")
        # Log the full error e
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating the portfolio dashboard: {str(e)}"
        ) 