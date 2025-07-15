from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import ast # For converting string list from get_additional_pages if it still returns that

from app.models.welcome_models import FinancialPlanRequest, FinancialPlanResponse, InitialWelcomeDataResponse
from app.models.user_models import UserData, UserDataCreate
from app.models.portfolio_models import OptimizedPortfolio, OptimizedHolding
from app.models.ai_insights_models import PortfolioAnalysis, MarketSentiment
from app.services.ai_service import AIService
from app.services.news_service import NewsService
from app.services.custom_investment_agent_service import get_additional_pages as get_additional_pages_service
from app.services.database_service import insert_optimized_portfolio_db

router = APIRouter()

# Define the base pages that should always be present.
# This was in dash_app.py globally
BASE_PAGES = ["Welcome", "Portfolio Dashboard", "News Tracker", "Live Trades"]

@router.get("/initial_data", response_model=InitialWelcomeDataResponse)
async def get_initial_welcome_data():
    """Provides initial data for the Welcome page, similar to dcc.Store initial values."""
    initial_user_data = {
        'user_id': '',
        'investment_goals': '',
        'amount': None, # Or 0, depending on how frontend handles it
        'income': None, # Or 0
        'custom_portfolio': {}
    }
    return InitialWelcomeDataResponse(user_data=initial_user_data, base_pages=BASE_PAGES)


@router.post("/financial_plan", response_model=FinancialPlanResponse)
async def create_financial_plan(
    request_data: FinancialPlanRequest,
    ai_service: AIService = Depends(AIService) # Dependency injection for AI service
):
    """
    Handles the submission of the user's financial information and goals,
    generates an optimized portfolio, and suggests additional pages.
    """
    user_name = request_data.user_name
    current_savings = request_data.current_savings
    annual_income = request_data.annual_income
    investment_goals = request_data.investment_goals

    if not user_name:
        raise HTTPException(status_code=400, detail="User name is required.")

    user_data_dict = {
        "user_id": user_name,
        "investment_goals": investment_goals,
        "amount": current_savings if current_savings is not None else 0,
        "income": annual_income if annual_income is not None else 0,
        "custom_portfolio": None # Will be populated if successful
    }

    pages = BASE_PAGES[:]
    if investment_goals:
        try:
            # The get_additional_pages_service might return a list of strings directly
            # or a string representation of a list like before.
            # For now, assuming it returns list[str]
            additional_pages_list = get_additional_pages_service(investment_goals, BASE_PAGES)
            if isinstance(additional_pages_list, str):
                # If it's still a string like '["Page1", "Page2"]'
                additional_pages = ast.literal_eval(additional_pages_list)
            elif isinstance(additional_pages_list, list):
                additional_pages = additional_pages_list
            else:
                additional_pages = [] # Default to empty if unexpected type
            
            pages.extend([p for p in additional_pages if p not in pages])
        except (ValueError, SyntaxError) as e:
            print(f"Error processing additional pages from investment_goals: {e}")
            # Keep pages as base_pages if error
    
    output_message = "Please provide investment goals to generate a plan."
    optimized_portfolio_response: Optional[OptimizedPortfolio] = None
    portfolio_analysis_response: Optional[PortfolioAnalysis] = None
    
    if investment_goals:
        try:
            # 1. Optimize Portfolio using AI Service
            # The AIService.optimize_portfolio mock currently returns a dict.
            # We need to parse it into our Pydantic models.
            raw_optimized_portfolio = ai_service.optimize_portfolio({}, investment_goals) # current_portfolio is empty for new plan

            if not raw_optimized_portfolio or not raw_optimized_portfolio.get("optimized_holdings"):
                user_data_dict["custom_portfolio"] = OptimizedPortfolio(optimized_holdings=[])
                return FinancialPlanResponse(
                    user_data=UserData(**user_data_dict),
                    pages=pages,
                    error="No portfolio holdings were generated. Please try again."
                )

            # Convert raw holdings to Pydantic model instances
            holdings_models = [
                OptimizedHolding(**h) for h in raw_optimized_portfolio.get("optimized_holdings", [])
            ]
            optimized_portfolio_response = OptimizedPortfolio(optimized_holdings=holdings_models)
            
            # Store as dict to avoid validation issues
            user_data_dict["custom_portfolio"] = optimized_portfolio_response.model_dump()

            # 2. Get AI Insights (after portfolio is confirmed)
            try:
                # Portfolio Analysis
                raw_portfolio_analysis = ai_service.get_portfolio_insights(raw_optimized_portfolio)
                portfolio_analysis_response = PortfolioAnalysis(**raw_portfolio_analysis)

                # Market Sentiment - REMOVED from here
                # market_news = news_service.get_market_news(limit=5)
                # raw_market_sentiment = ai_service.get_market_sentiment(market_news)
                # market_sentiment_response = MarketSentiment(**raw_market_sentiment)
            except Exception as e:
                print(f"Error generating AI insights: {e}")
                # Non-critical, so we can proceed without insights if they fail

            # 3. Insert into Database
            try:
                insert_optimized_portfolio_db(
                    optimized_portfolio_data=raw_optimized_portfolio, # The service expects a dict
                    user_id=user_name,
                    amount=user_data_dict['amount'],
                    income=user_data_dict['income']
                )
                print("Optimized portfolio and client data inserted into the database.")
                output_message = "Your portfolio has been saved and is ready for detailed analysis!"
            except Exception as e:
                print(f"Error inserting optimized portfolio into DB: {e}")
                # Decide if this is a critical failure or if we can proceed without DB save
                return FinancialPlanResponse(
                    user_data=UserData(**user_data_dict), # Return data even if DB fails for now
                    pages=pages,
                    optimized_portfolio=optimized_portfolio_response,
                    portfolio_analysis=portfolio_analysis_response, 
                    error=f"Database error: {str(e)}. Portfolio generated but not saved."
                )

        except Exception as e:
            print(f"Error in processing financial plan: {e}")
            user_data_dict["custom_portfolio"] = OptimizedPortfolio(optimized_holdings=[])
            return FinancialPlanResponse(
                user_data=UserData(**user_data_dict),
                pages=pages,
                error=f"Error Creating Financial Plan: {str(e)}"
            )
    
    # Construct the final UserData Pydantic model
    final_user_data = UserData(**user_data_dict)

    # Convert to dictionaries to avoid validation errors
    optimized_portfolio_dict = optimized_portfolio_response.model_dump() if optimized_portfolio_response else None
    portfolio_analysis_dict = portfolio_analysis_response.model_dump() if portfolio_analysis_response else None

    return FinancialPlanResponse(
        user_data=final_user_data,
        pages=pages,
        optimized_portfolio=optimized_portfolio_dict,
        portfolio_analysis=portfolio_analysis_dict, 
        message=output_message if not optimized_portfolio_response else None
    ) 