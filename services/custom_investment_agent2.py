import os
from openai import OpenAI
from dotenv import load_dotenv
import singlestoredb as s2
import yfinance as yf
from services.stock_service import StockService

load_dotenv()

def get_additional_pages(investment_goals: str, current_pages: list) -> list:
    client = OpenAI(api_key=os.getenv("openai_api_key"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"""You are a financial advisor. Based on the following investment goals and current pages, 
                   return a list of additional pages that are relevant to the investment goals from the following list: ["College Savings Account", "529 Plan", "Crypto Investments", "Mortgage Planning", "Estate Planning", "Life Insurance"] 
                   Investment Goals: {investment_goals}
                   Current Pages: {current_pages}
                    It is imperative that you return your response like a python list [page1, page2, page3] with no other text.
                   """}]
    )

    return response.choices[0].message.content

def connect_to_db():
    config = {
        "host": os.getenv('host'),
        "port": os.getenv('port'),
        "user": os.getenv('user'),
        "password": os.getenv('password'),
        "database": os.getenv('database')
    }
    connection = s2.connect(**config)
    cursor = connection.cursor()
    return cursor

def calculate_portfolio_amount(user_id: str) -> float:
    """
    Calculates the total portfolio amount for a specific user using real-time stock prices.
    
    Args:
        user_id: The ID of the user whose portfolio should be calculated
        
    Returns:
        float: The total value of the user's portfolio
    """
    try:
        cursor = connect_to_db()
        
        # Query the optimized portfolio for the user
        query = "SELECT symbol, quantity FROM optimized_portfolio WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        portfolio_data = cursor.fetchall()
        cursor.close()
        
        # Create portfolio positions dictionary
        positions = {symbol: quantity for symbol, quantity in portfolio_data}
        
        # Use StockService to get portfolio performance with real-time prices
        stock_service = StockService()
        performance = stock_service.get_portfolio_performance(positions)
        
        # Return the total portfolio value
        return performance['total_value']
        
    except Exception as e:
        print(f"Error calculating portfolio amount: {e}")
        return 0.0

def calculate_affordable_house_price(user_id: str) -> dict:
    """
    Calculates how much house a user can afford based on their portfolio value.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        dict: Information about home affordability including maximum price,
              down payment, and monthly payment estimates
    """
    try:
        # Get the user's portfolio value
        portfolio_value = calculate_portfolio_amount(user_id)
        
        # Standard affordability calculations
        # Assume 20% of portfolio can be used for down payment
        down_payment = portfolio_value * 0.20
        
        # Current mortgage rates (would be better to fetch this dynamically)
        annual_interest_rate = 0.06  # 6%
        monthly_interest_rate = annual_interest_rate / 12
        loan_term_years = 30
        loan_term_months = loan_term_years * 12
        
        # Calculate maximum mortgage amount
        # Assume housing expense shouldn't exceed 28% of monthly income
        # Without income data, we'll estimate based on portfolio (rough approximation)
        # Assume annual income is ~30% of portfolio value
        estimated_annual_income = portfolio_value * 0.30
        estimated_monthly_income = estimated_annual_income / 12
        
        max_monthly_payment = estimated_monthly_income * 0.28
        
        # Mortgage formula: P = M * [(1 - (1 + r)^-n) / r]
        # Where P is principal, M is monthly payment, r is monthly interest rate, n is term in months
        # Solving for P given M
        if monthly_interest_rate > 0:
            mortgage_amount = max_monthly_payment * ((1 - (1 + monthly_interest_rate)**(-loan_term_months)) / monthly_interest_rate)
        else:
            mortgage_amount = max_monthly_payment * loan_term_months
        
        # Maximum house price = mortgage amount + down payment
        max_house_price = mortgage_amount + down_payment
        
        # Monthly payment calculation
        if down_payment < max_house_price:
            loan_amount = max_house_price - down_payment
            if monthly_interest_rate > 0:
                monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**loan_term_months) / ((1 + monthly_interest_rate)**loan_term_months - 1)
            else:
                monthly_payment = loan_amount / loan_term_months
        else:
            monthly_payment = 0  # If down payment covers entire house
            
        return {
            "portfolio_value": portfolio_value,
            "max_house_price": max_house_price,
            "down_payment": down_payment,
            "loan_amount": max_house_price - down_payment,
            "monthly_payment": monthly_payment,
            "loan_term_years": loan_term_years,
            "interest_rate": annual_interest_rate,
            "estimated_annual_income": estimated_annual_income
        }
        
    except Exception as e:
        print(f"Error calculating affordable house price: {e}")
        return {
            "error": str(e),
            "max_house_price": 0,
            "down_payment": 0,
            "monthly_payment": 0
        }

def loan_agent() -> str:
    client = OpenAI(api_key=os.getenv("openai_api_key"))
    cursor = connect_to_db()
    user_data = cursor.execute("SELECT * FROM user_data")
    
    # Get mortgage affordability information
    try:
        user_id = user_data[0][0]  # Assuming first column of first row is user_id
        home_affordability = calculate_affordable_house_price(user_id)
        affordability_info = f"""
        Based on your portfolio value of ${home_affordability['portfolio_value']:,.2f}, here's your home buying power:
        - Maximum home price: ${home_affordability['max_house_price']:,.2f}
        - Suggested down payment: ${home_affordability['down_payment']:,.2f}
        - Estimated monthly payment: ${home_affordability['monthly_payment']:,.2f}
        - Loan term: {home_affordability['loan_term_years']} years
        - Interest rate: {home_affordability['interest_rate']*100:.2f}%
        """
    except Exception as e:
        print(f"Error in home affordability calculation: {e}")
        affordability_info = "Home affordability information unavailable."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"""You are a financial advisor. Based on the following user data and home affordability analysis, 
                   provide mortgage and home buying advice.
                   
                   User Data: {user_data}
                   
                   Home Affordability Analysis:
                   {affordability_info}
                   
                   Provide personalized advice on:
                   1. Whether this is a good time for the user to buy a home
                   2. Suggestions for down payment and mortgage term
                   3. Any other financial considerations related to home buying
                   """}]
    )

    return response.choices[0].message.content