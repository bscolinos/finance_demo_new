import pandas as pd
import os
import singlestoredb as s2
from dash import html, dcc
import dash_bootstrap_components as dbc
from services.stock_service import StockService
from utils.data_utils import format_currency, format_percentage, calculate_portfolio_metrics

def get_optimized_positions(user_id=None):
    """Fetch optimized portfolio positions from SingleStore."""
    config = {
        "host": os.getenv('host'),
        "port": os.getenv('port'),
        "user": os.getenv('user'),
        "password": os.getenv('password'),
        "database": os.getenv('database')
    }
    connection = s2.connect(**config)
    cursor = connection.cursor()
    
    if not user_id:
        cursor.close()
        connection.close()
        return {}

    try:
        query = "SELECT symbol, quantity FROM optimized_portfolio WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        print(results)
    except Exception as e:
        print(f"Error fetching optimized positions: {e}")
        return {}
    cursor.close()
    connection.close()

    positions = {}
    for row in results:
        # Assuming each row is a tuple (symbol, quantity)
        symbol = row[0]
        quantity = row[1]
        # If multiple rows for the same symbol exist, sum them
        positions[symbol] = positions.get(symbol, 0) + quantity
    return positions


def display_portfolio_summary():
    """Display portfolio summary section using optimized portfolio positions - Dash version."""
    try:
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div(id="portfolio-metrics", className="d-flex justify-content-around mb-4")
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Portfolio Holdings")),
                        dbc.CardBody([
                            html.Div(id="portfolio-holdings-table")
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Portfolio Allocation")),
                        dbc.CardBody([
                            dcc.Graph(
                                id="portfolio-allocation-chart",
                                figure={},  # Empty initially
                                config={"displayModeBar": False}
                            )
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Risk Analysis")),
                        dbc.CardBody([
                            html.Div(id="risk-analysis-content", children=[
                                dbc.Spinner(type="border", color="primary", size="sm"),
                                html.P("Loading risk analysis...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=6)
            ])
        ])
    except Exception as e:
        return dbc.Alert(
            f"Error displaying portfolio summary: {str(e)}",
            color="danger"
        )


def add_stock_to_portfolio(symbol: str, quantity: int, user_id: str):
    """Add a stock symbol to the optimized portfolio table for the current user."""
    config = {
        "host": os.getenv('host'),
        "port": os.getenv('port'),
        "user": os.getenv('user'),
        "password": os.getenv('password'),
        "database": os.getenv('database')
    }
    connection = s2.connect(**config)
    cursor = connection.cursor()

    if not user_id:
        return False, "User ID is not set."

    try:
        # Check if the symbol already exists for this user
        query = "SELECT quantity FROM optimized_portfolio WHERE user_id = %s AND symbol = %s"
        cursor.execute(query, (user_id, symbol))
        result = cursor.fetchone()

        if result:
            # Update the quantity if the stock already exists
            new_quantity = result[0] + quantity
            update_query = "UPDATE optimized_portfolio SET quantity = %s WHERE user_id = %s AND symbol = %s"
            cursor.execute(update_query, (new_quantity, user_id, symbol))
        else:
            # Insert new record; using 0.0 as a default for target_allocation
            insert_query = "INSERT INTO optimized_portfolio (user_id, symbol, quantity, target_allocation) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (user_id, symbol, quantity, 0.0))

        connection.commit()
        cursor.close()
        connection.close()
        return True, f"Added {quantity} shares of {symbol} to your portfolio."
    except Exception as e:
        return False, f"Error adding stock: {str(e)}"


def display_quick_actions():
    """Display quick actions section - Dash version."""
    return html.Div([
        html.H5("Add to Portfolio", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="add-stock-symbol",
                    type="text",
                    placeholder="Stock Symbol (e.g., AAPL)",
                    className="mb-2"
                )
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="add-stock-quantity",
                    type="number",
                    min=1,
                    step=1,
                    value=1,
                    placeholder="Quantity",
                    className="mb-2"
                )
            ], width=6),
            dbc.Col([
                dbc.Button(
                    "Add to Portfolio", 
                    id="add-stock-button", 
                    color="primary",
                    className="w-100"
                )
            ], width=6)
        ]),
        html.Div(id="add-stock-result", className="mt-2"),
        html.Hr(),
        dbc.Button(
            "Rebalance Portfolio", 
            id="rebalance-button", 
            color="secondary",
            className="w-100 mt-2"
        ),
        html.Div(id="rebalance-result", className="mt-2")
    ])


def display_market_summary():
    """Display market summary section - Dash version."""
    try:
        market_data = StockService.get_market_summary()
        
        metrics = []
        for index, data in market_data.items():
            metrics.append(
                dbc.Col([
                    html.H6(data['name'], className="text-muted"),
                    html.H5([
                        format_currency(data['price']),
                        html.Span(
                            format_percentage(data['change']),
                            className=f"ms-2 {'text-success' if data['change'] >= 0 else 'text-danger'}"
                        )
                    ])
                ], width=12, className="mb-3")
            )
        
        return html.Div([
            html.H5("Market Summary", className="mb-3"),
            dbc.Row(metrics)
        ])
    except Exception as e:
        return dbc.Alert(
            f"Error loading market data: {str(e)}",
            color="danger"
        )