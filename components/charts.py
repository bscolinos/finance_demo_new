import plotly.graph_objects as go
import plotly.express as px
from services.stock_service import StockService
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
from components import portfolio

def plot_portfolio_performance():
    """Display portfolio performance chart section."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("Portfolio Value Over Time", className="mb-3"),
                dcc.Graph(
                    id="portfolio-performance-chart",
                    figure={},  # Empty figure initially, will be populated by callback
                    config={"displayModeBar": True}
                )
            ], width=12, className="mb-4")
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id="portfolio-metrics", className="d-flex justify-content-around")
            ], width=12)
        ])
    ])

def create_portfolio_chart(data):
    """Create a line chart of portfolio performance over time."""
    if data is None or data.empty:
        # Return an empty figure with a message
        fig = go.Figure()
        fig.update_layout(
            title="Portfolio Performance",
            xaxis_title="Date",
            yaxis_title="Value ($)",
            height=400,
            annotations=[
                dict(
                    text="No portfolio data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
            ]
        )
        return fig
    
    # Create the figure with portfolio value data
    fig = go.Figure()
    
    # Check if 'portfolio_value' column exists, otherwise use 'value'
    value_col = 'portfolio_value' if 'portfolio_value' in data.columns else 'value'
    
    fig.add_trace(
        go.Scatter(
            x=data.index if hasattr(data, 'index') else data['date'],
            y=data[value_col],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#007bff', width=2)
        )
    )
    
    # Format the figure
    fig.update_layout(
        title="Portfolio Performance (YTD)",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode='x unified',
        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(230, 230, 230, 0.8)',
            zeroline=False,
            tickprefix='$'
        ),
        plot_bgcolor='white'
    )
    return fig
