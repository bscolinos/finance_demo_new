from typing import Dict, List
from app.db.database import get_db_connection
from app.models.portfolio_models import OptimizedHoldingCreate
from app.models.user_models import ClientInfo

def insert_optimized_portfolio_db(optimized_portfolio_data: Dict, user_id: str, amount: float = 0, income: float = 0):
    """
    Inserts optimized portfolio positions into SingleStore.
    Also inserts/updates client information including savings amount and income.
    The input `optimized_portfolio_data` is expected to be a dict like {"optimized_holdings": [...]}
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            # Clear previous optimizations for this user
            try:
                cursor.execute("DELETE FROM optimized_portfolio WHERE user_id = %s", (user_id,))
            except Exception as e:
                print(f"Error deleting from optimized_portfolio: {e}") # Consider logging framework
                # Depending on requirements, may want to raise or handle differently

            insert_query = '''
            INSERT INTO optimized_portfolio (user_id, symbol, quantity, target_allocation)
            VALUES (%s, %s, %s, %s);
            '''
            holdings_to_insert = optimized_portfolio_data.get("optimized_holdings", [])
            if not holdings_to_insert:
                print(f"No holdings to insert for user {user_id}")
            
            for holding_data in holdings_to_insert:
                # Ensure data matches OptimizedHoldingCreate model implicitly or explicitly validate
                # For now, assuming keys match: symbol, quantity, target_allocation
                holding = OptimizedHoldingCreate(**holding_data) # Validate structure
                data_tuple = (
                    user_id,
                    holding.symbol,
                    holding.quantity,
                    holding.target_allocation
                )
                try:
                    cursor.execute(insert_query, data_tuple)
                except Exception as e:
                    print(f"Error inserting holding {holding.symbol} for user {user_id}: {e}")
                    # Continue or raise?

            # Insert or update client information
            client_query = '''
            INSERT INTO clients (user_id, amount, income)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE amount = VALUES(amount), income = VALUES(income);
            ''' 
            # Using VALUES() for ON DUPLICATE KEY UPDATE is often preferred
            client_data = ClientInfo(user_id=user_id, amount=amount, income=income)
            try:
                cursor.execute(client_query, (client_data.user_id, client_data.amount, client_data.income))
            except Exception as e:
                print(f"Error inserting/updating client data for user {user_id}: {e}")

            connection.commit() 