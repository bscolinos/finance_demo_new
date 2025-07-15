import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, no_update
import os
import json
import singlestoredb as s2
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
import ast  # used to convert string tool output to list
import pandas as pd
import plotly.express as px

load_dotenv()

# Database configuration
config = {
    "host": os.getenv('host'),
    "port": os.getenv('port'),
    "user": os.getenv('user'),
    "password": os.getenv('password'),
    "database": os.getenv('database')
}

# Import your components and services
from components import portfolio, news, charts
from components.portfolio import get_optimized_positions
from services.stock_service import StockService
from services.news_service import NewsService
from services.ai_service import AIService
from services.custom_investment_agent2 import get_additional_pages
from utils.data_utils import calculate_portfolio_metrics, format_currency, format_percentage

def insert_optimized_portfolio(optimized_portfolio_data: dict, user_id: str, amount: float = 0, income: float = 0):
    """
    Inserts optimized portfolio positions into SingleStore.
    Also inserts/updates client information including savings amount and income.
    """
    connection = s2.connect(**config)
    cursor = connection.cursor()

    # Clear previous optimizations for this user
    cursor.execute("DELETE FROM optimized_portfolio WHERE user_id = %s", (user_id, ))

    insert_query = '''
    INSERT INTO optimized_portfolio (user_id, symbol, quantity, target_allocation)
    VALUES (%s, %s, %s, %s);
    '''
    for holding in optimized_portfolio_data.get("optimized_holdings", []):
        data_tuple = (
            user_id,
            holding["symbol"],
            holding["quantity"],
            holding["target_allocation"]
        )
        cursor.execute(insert_query, data_tuple)

    # Insert or update client information
    client_query = '''
    INSERT INTO clients (user_id, amount, income)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE amount = %s, income = %s;
    '''
    client_data = (user_id, amount, income, amount, income)
    cursor.execute(client_query, client_data)

    connection.commit()
    cursor.close()
    connection.close()

# Define the base pages that should always be present.
# base_pages = ["Welcome", "Portfolio Dashboard", "News Tracker", "AI Insights", "Stock Research"]
base_pages = ["Welcome", "Portfolio Dashboard", "News Tracker", "AI Insights", "Live Trades"] # "Stock Research" commented out for now

# Initialize the Dash app with Bootstrap components and Font Awesome.
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ],
    suppress_callback_exceptions=True
)
server = app.server  # For deployment purposes

# Define custom styles.
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "250px",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "boxShadow": "1px 0 5px rgba(0,0,0,0.1)"
}

CONTENT_STYLE = {
    "marginLeft": "250px",
    "padding": "2rem 3rem",
    "backgroundColor": "#fff"
}

CARD_STYLE = {
    "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.1)",
    "borderRadius": "8px",
    "padding": "20px",
    "marginBottom": "20px",
    "backgroundColor": "white"
}

# Updated navbar with a clickable brand.
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.I(className="fas fa-chart-line me-2", style={"fontSize": "24px"})),
                        dbc.Col(dbc.NavbarBrand("AI Financial Advisor", className="ms-2", id="navbar-brand")),
                    ],
                    align="center",
                ),
                href="#",
                style={"textDecoration": "none"},
            )
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4",
)

# Define the welcome page layout.
def welcome_page(user_data):
    # If a custom portfolio with optimized holdings exists, display the portfolio details.
    if user_data.get("custom_portfolio", {}).get("optimized_holdings"):
        holdings_rows = []
        for holding in user_data["custom_portfolio"]["optimized_holdings"]:
            holdings_rows.append(
                dbc.ListGroupItem([
                    html.Div([
                        html.Span(holding["symbol"], className="fw-bold"),
                        html.Span(f"{holding['target_allocation']*100:.1f}%", className="badge bg-primary ms-2"),
                    ], className="d-flex justify-content-between"),
                    html.Div(f"Quantity: {holding['quantity']}")
                ])
            )
        portfolio_message = html.Div([
            html.H5("Your Personalized Investment Plan", className="text-success mb-3"),
            html.P("Based on your goals, we've created an optimized portfolio that aligns with your objectives:"),
            dbc.ListGroup(holdings_rows, className="mb-3"),
            html.P("Your portfolio has been saved and is ready for detailed analysis!", className="text-muted"),
            dbc.Button(
                "View Portfolio Details", 
                id={"type": "view-portfolio-btn", "index": "view-portfolio-btn"}, 
                color="success", 
                className="mt-2"
            )
        ], id="portfolio-results")
    else:
        portfolio_message = html.P(
            "Enter your details and click 'Create My Financial Plan' to see your personalized portfolio.",
            className="text-muted"
        )

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Welcome to AI Financial Advisor", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Get Started", className="card-title mb-4"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Label("Enter your name:", width=12, className="mb-2"),
                                dbc.Col([
                                    dbc.Input(
                                        id='user-name',
                                        type='text',
                                        placeholder='Your name',
                                        value=user_data.get('user_id', ''),
                                        className="mb-3"
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Label("Current Savings ($):", width=12, className="mb-2"),
                                dbc.Col([
                                    dbc.Input(
                                        id='current-savings',
                                        type='number',
                                        placeholder='Amount in $',
                                        value=user_data.get('amount', ''),
                                        className="mb-3"
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Label("Annual Income ($):", width=12, className="mb-2"),
                                dbc.Col([
                                    dbc.Input(
                                        id='annual-income',
                                        type='number',
                                        placeholder='Amount in $',
                                        value=user_data.get('income', ''),
                                        className="mb-3"
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Label("Enter your investment goals:", width=12, className="mb-2"),
                                dbc.Col([
                                    dbc.Textarea(
                                        id='investment-goals',
                                        placeholder='e.g., I want to save for retirement, college funds for kids, etc.',
                                        value=user_data.get('investment_goals', ''),
                                        className="mb-3",
                                        style={"height": "120px"}
                                    )
                                ])
                            ]),
                            dbc.Button(
                                "Create My Financial Plan",
                                id='submit-btn',
                                color="primary",
                                className="mt-3"
                            ),
                        ])
                    ])
                ], className="mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='welcome-output', children=portfolio_message)
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Why Choose an AI Financial Advisor?", className="card-title"),
                        html.P("Our AI-powered platform offers personalized financial advice tailored to your goals, without the cost associated with human intervention."),
                        html.Ul([
                            html.Li("Personalized investment strategies"),
                            html.Li("Real-time market analysis"),
                            html.Li("AI-driven portfolio optimization"),
                            html.Li("Customized goal planning"),
                        ])
                    ])
                ], className="mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Market Insights", className="card-title"),
                        html.P("Today's Market Overview"),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Div("S&P 500", className="fw-bold"),
                                html.Div([
                                    html.Span("4,587.64 ", className="text-success"),
                                    html.Span("+0.57%", className="text-success")
                                ], className="d-flex justify-content-between")
                            ]),
                            dbc.ListGroupItem([
                                html.Div("NASDAQ", className="fw-bold"),
                                html.Div([
                                    html.Span("14,346.02 ", className="text-success"),
                                    html.Span("+0.75%", className="text-success")
                                ], className="d-flex justify-content-between")
                            ]),
                            dbc.ListGroupItem([
                                html.Div("10-YR Treasury", className="fw-bold"),
                                html.Div([
                                    html.Span("1.67% ", className="text-danger"),
                                    html.Span("-0.02%", className="text-danger")
                                ], className="d-flex justify-content-between")
                            ])
                        ])
                    ])
                ])
            ], width=4)
        ])
    ])

app.layout = html.Div([
    # Stores to hold user data and the list of available pages.
    dcc.Store(id='store-pages', data=base_pages),
    dcc.Store(id='store-user', data={'user_id': '', 'investment_goals': '', 'custom_portfolio': {}}),
    dcc.Store(id='active-page', data='Welcome'),  # Store for active page
    
    # Sidebar navigation.
    html.Div([
        html.H4("Navigation", className="text-primary"),
        html.Hr(),
        html.Div(id='page-selector-nav'),  # Populated by callback.
    ], style=SIDEBAR_STYLE),
    
    # Main content area.
    html.Div([
        # Navbar.
        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(html.I(className="fas fa-chart-line me-2", style={"fontSize": "24px"})),
                                html.Span("AI Financial Advisor", className="ms-2 navbar-brand")
                            ],
                            align="center",
                        ),
                        id="navbar-home-link",
                        href="#",
                        style={"textDecoration": "none", "color": "white"},
                    )
                ]
            ),
            color="primary",
            dark=True,
            className="mb-4",
        ),
        # Main content.
        html.Div(id='main-content')
    ], style=CONTENT_STYLE)
])

# Callback to build the sidebar navigation from the pages store.
@app.callback(
    Output('page-selector-nav', 'children'),
    [Input('store-pages', 'data'),
     Input('active-page', 'data')]
)
def build_navigation(pages, active_page):
    nav_items = []
    icons = {
        "Welcome": "fas fa-home",
        "Portfolio Dashboard": "fas fa-chart-pie",
        "News Tracker": "fas fa-newspaper",
        "AI Insights": "fas fa-robot",
        "College Savings Account": "fas fa-graduation-cap",
        "529 Plan": "fas fa-university",
        "Crypto Investments": "fab fa-bitcoin",
        "Mortgage Planning": "fas fa-home",
        "Estate Planning": "fas fa-scroll",
        "Life Insurance": "fas fa-heartbeat"
    }
    
    for page in pages:
        icon = icons.get(page, "fas fa-circle")
        is_active = page == active_page
        
        nav_items.append(
            dbc.Button(
                [
                    html.I(className=f"{icon} me-2"),
                    html.Span(page)
                ],
                id={"type": "page-nav", "index": page},
                color="primary",
                outline=not is_active,  # Solid if active, outlined otherwise.
                className="mb-2 text-start w-100",
                style={"textAlign": "left", "justifyContent": "flex-start"}
            )
        )
    
    return html.Div(nav_items)

@app.callback(
    Output('active-page', 'data'),
    [
        Input({"type": "page-nav", "index": ALL}, "n_clicks"),
        Input("navbar-home-link", "n_clicks"),
        Input({"type": "view-portfolio-btn", "index": ALL}, "n_clicks")
    ],
    State('active-page', 'data'),
    prevent_initial_call=True
)
def update_active_page(nav_clicks, home_clicks, view_portfolio_clicks, current_page):
    ctx = callback_context
    if not ctx.triggered:
        return current_page

    for trigger in ctx.triggered:
        prop_id = trigger['prop_id']
        val = trigger.get('value')
        try:
            id_part = json.loads(prop_id.split('.')[0])
            # Only act if the button has been actually clicked (i.e. n_clicks > 0)
            if id_part.get("type") == "view-portfolio-btn" and val:
                return "Portfolio Dashboard"
            elif id_part.get("type") == "page-nav" and val:
                return id_part.get("index", current_page)
        except Exception:
            # Check for the navbar home link.
            if prop_id == "navbar-home-link.n_clicks" and val:
                return "Welcome"
    return current_page

@app.callback(
    Output('main-content', 'children'),
    [Input('active-page', 'data')],
    [State('store-user', 'data'),
     State('store-pages', 'data')]
)
def update_content(page, user_data, pages):
    if page not in pages:
        page = "Welcome"
    if page == "Welcome":
        return welcome_page(user_data)
    else:
        return render_page(page, user_data)

@app.callback(
    [Output('store-user', 'data'),
     Output('store-pages', 'data'),
     Output('welcome-output', 'children')],
    Input('submit-btn', 'n_clicks'),
    [State('user-name', 'value'),
     State('current-savings', 'value'),
     State('annual-income', 'value'),
     State('investment-goals', 'value'),
     State('store-user', 'data'),
     State('store-pages', 'data')],
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_welcome(n_clicks, user_name, current_savings, annual_income, investment_goals, user_data, pages):
    print("Create My Financial Plan Button clicked", n_clicks)
    if n_clicks is None or n_clicks == 0:
        return user_data, pages, no_update

    user_data['user_id'] = user_name
    user_data['investment_goals'] = investment_goals
    
    # Convert inputs to float, defaulting to 0 if empty
    try:
        amount = float(current_savings) if current_savings else 0
        income = float(annual_income) if annual_income else 0
        user_data['amount'] = amount
        user_data['income'] = income
    except (ValueError, TypeError):
        amount = 0
        income = 0
        user_data['amount'] = 0
        user_data['income'] = 0

    if investment_goals:
        try:
            additional_pages_text = get_additional_pages(investment_goals, base_pages)
            additional_pages = ast.literal_eval(additional_pages_text)
            pages = base_pages[:] + [p for p in additional_pages if p not in base_pages]
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing investment_goals: {e}")
            pages = base_pages
    else:
        pages = base_pages

    output_message = html.Div("Please provide investment goals to generate a plan.")
    
    if investment_goals:
        try:
            ai_service = AIService()
            optimized_portfolio = ai_service.optimize_portfolio({}, investment_goals)
            try:
                insert_optimized_portfolio(optimized_portfolio, user_name, amount, income)
                print("Optimized portfolio and client data inserted into the database.")
            except Exception as e:
                print(f"Error inserting optimized portfolio: {e}")
                return user_data, pages, html.Div(f"Database error: {str(e)}", className="text-danger")
                
            user_data['custom_portfolio'] = optimized_portfolio

            if not optimized_portfolio.get("optimized_holdings"):
                return user_data, pages, html.Div("No portfolio holdings were generated. Please try again.", className="text-danger")

            holdings_rows = []
            for holding in optimized_portfolio.get("optimized_holdings", []):
                holdings_rows.append(
                    dbc.ListGroupItem([
                        html.Div([
                            html.Span(holding["symbol"], className="fw-bold"),
                            html.Span(f"{holding['target_allocation']*100:.1f}%", className="badge bg-primary ms-2"),
                        ], className="d-flex justify-content-between"),
                        html.Div(f"Quantity: {holding['quantity']}")
                    ])
                )

            if holdings_rows:
                output_message = html.Div([
                    html.H5("Your Personalized Investment Plan", className="text-success mb-3"),
                    html.P("Based on your goals, we've created an optimized portfolio that aligns with your objectives:"),
                    dbc.ListGroup(holdings_rows, className="mb-3"),
                    html.P("Your portfolio has been saved and is ready for detailed analysis!", className="text-muted"),
                    dbc.Button(
                        "View Portfolio Details", 
                        id={"type": "view-portfolio-btn", "index": "view-portfolio-btn"}, 
                        color="success", 
                        className="mt-2"
                    )
                ], id="portfolio-results")
            else:
                output_message = html.Div("Could not generate portfolio holdings. Please try again.", className="text-danger")
                
        except Exception as e:
            print(f"Error in processing financial plan: {e}")
            output_message = html.Div([
                html.H5("Error Creating Financial Plan", className="text-danger"),
                html.P(f"An error occurred: {str(e)}")
            ])

    return user_data, pages, output_message

def fetch_live_trades():
    query = """
    SELECT localTS, ticker, price, size
      FROM live_trades
     WHERE localTS >= CONVERT_TZ(NOW(), @@session.time_zone, 'America/New_York')
                       - INTERVAL 5 MINUTE
     ORDER BY localTS
    """
    conn = s2.connect(**config)
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    if not df.empty:
        df['localTS'] = pd.to_datetime(df['localTS'])
        df.sort_values('localTS', inplace=True)
    return df

def render_live_trades_page():
    return dbc.Container([
        html.H2("Live Trades", className="text-primary mb-4"),
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id='ticker-dropdown',
                            options=[
                                {'label': 'All', 'value': 'ALL'},
                                {'label': 'AAPL', 'value': 'AAPL'},
                                {'label': 'MSFT', 'value': 'MSFT'},
                                {'label': 'NVDA', 'value': 'NVDA'},
                                {'label': 'TSLA', 'value': 'TSLA'},
                                {'label': 'AMZN', 'value': 'AMZN'}
                            ],
                            value='ALL',
                            clearable=False,
                            className="mb-3"
                        )
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='live-trades-graph')
                    ], width=12)
                ]),
                dcc.Interval(id='interval-component', interval=1_000, n_intervals=0)
            ])
        ])
    ])

@app.callback(
    Output('live-trades-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('ticker-dropdown', 'value')
)
def update_graph_live(n, selected_ticker):
    df = fetch_live_trades()
    if selected_ticker != 'ALL':
        df = df[df['ticker'] == selected_ticker]
    if df.empty:
        fig = px.line(title="No Data Available")
        fig.update_layout(xaxis_title="Timestamp", yaxis_title="Price")
        return fig

    fig = px.line(df, x='localTS', y='price', color='ticker',
                  title=f"Live Trades ({selected_ticker if selected_ticker!='ALL' else 'All'})")
    fig.update_traces(connectgaps=True)
    fig.update_xaxes(
        range=[df['localTS'].min(), df['localTS'].max()],
        tickformat='%H:%M:%S',
        nticks=6,
        tickangle=45,
        rangeslider_visible=False
    )
    fig.update_layout(xaxis_title="Timestamp", yaxis_title="Price")
    return fig

def render_page(page, user_data):
    try:
        if page == "Welcome":
            return welcome_page(user_data)
        elif page == "Portfolio Dashboard":
            return dbc.Container([
                html.H2("Portfolio Overview", className="text-primary mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Portfolio Summary")),
                            dbc.CardBody(portfolio.display_portfolio_summary())
                        ], className="mb-4")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Performance Charts")),
                            dbc.CardBody(charts.plot_portfolio_performance())
                        ], className="mb-4")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Quick Actions")),
                            dbc.CardBody(portfolio.display_quick_actions())
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Market Summary")),
                            dbc.CardBody(portfolio.display_market_summary())
                        ])
                    ], width=6)
                ])
            ])
        elif page == "News Tracker":
            return dbc.Container([
                html.H2("Financial News Tracker", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody(news.display_news_dashboard())
                ])
            ])
        elif page == "AI Insights":
            try:
                portfolio_data = user_data.get('custom_portfolio', {})
                ai_service = AIService()
                portfolio_analysis = ai_service.get_portfolio_insights(portfolio_data)
                news_service = NewsService()
                market_news = news_service.get_market_news(limit=5)
                sentiment = ai_service.get_market_sentiment(market_news)
                
                # Format portfolio analysis into Dash components
                portfolio_components = [
                    html.H6("Summary", className="mt-3"),
                    html.P(portfolio_analysis.get("summary", "No summary available.")),
                    
                    html.H6("Risks", className="mt-3"),
                    html.Ul([
                        html.Li(risk) for risk in portfolio_analysis.get("risks", ["No risks identified."])
                    ]),
                    
                    html.H6("Opportunities", className="mt-3"),
                    html.Ul([
                        html.Li(opportunity) for opportunity in portfolio_analysis.get("opportunities", ["No opportunities identified."])
                    ]),
                    
                    html.H6("Recommendations", className="mt-3"),
                    html.Ul([
                        html.Li(recommendation) for recommendation in portfolio_analysis.get("recommendations", ["No recommendations available."])
                    ])
                ]
                
                # Format sentiment analysis into Dash components
                sentiment_color = {
                    "bullish": "success",
                    "bearish": "danger",
                    "neutral": "secondary"
                }.get(sentiment.get("overall_sentiment", "neutral"), "secondary")
                
                sentiment_components = [
                    html.Div([
                        html.H6("Overall Market Sentiment"),
                        dbc.Badge(
                            sentiment.get("overall_sentiment", "Unknown").capitalize(),
                            color=sentiment_color,
                            className="mb-2",
                            style={"fontSize": "1rem", "padding": "0.5rem 1rem"}
                        ),
                        html.P(f"Confidence: {sentiment.get('confidence', 0) * 100:.0f}%")
                    ]),
                    
                    html.H6("Key Market Factors", className="mt-3"),
                    html.Ul([
                        html.Li(factor) for factor in sentiment.get("key_factors", ["No factors identified."])
                    ]),
                    
                    html.H6("Market Outlook", className="mt-3"),
                    html.P(sentiment.get("market_outlook", "No outlook available."))
                ]
                
            except Exception as e:
                print(f"Error loading AI insights: {e}")
                return dbc.Container([
                    html.H2("AI-Powered Insights", className="text-primary mb-4"),
                    dbc.Alert(f"Failed to load AI insights: {str(e)}", color="danger")
                ])
            
            return dbc.Container([
                html.H2("AI-Powered Insights", className="text-primary mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Portfolio Analysis")),
                            dbc.CardBody(portfolio_components)
                        ], className="mb-4")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Market Sentiment Analysis")),
                            dbc.CardBody(sentiment_components)
                        ])
                    ], width=12)
                ])
            ])
        elif page == "Live Trades":
            return render_live_trades_page()
        elif page == "College Savings Account":
            return dbc.Container([
                html.H2("College Savings Account", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "This page is designed to help you with planning and managing a college savings account. "
                            "Here you can find advice on setting savings goals, recommended account types, and strategies to optimize your contributions."
                        )
                    ])
                ])
            ])
        elif page == "529 Plan":
            return dbc.Container([
                html.H2("529 Plan", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "This page provides information on 529 plans—a tax-advantaged savings plan to encourage saving for future education costs. "
                            "You'll find details on tax benefits, investment options, and best practices for planning your child's education."
                        )
                    ])
                ])
            ])
        elif page == "Crypto Investments":
            return dbc.Container([
                html.H2("Crypto Investments", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "This page offers insights into cryptocurrency investments. "
                            "Explore market trends, top digital assets, and strategies for diversifying your portfolio with crypto. "
                            "Leverage the latest AI insights to help you make informed decisions in the dynamic crypto market."
                        )
                    ])
                ])
            ])
        elif page == "Mortgage Planning":
            return dbc.Container([
                html.H2("Mortgage Planning", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "This page provides information on mortgage planning. "
                            "Here you can find advice on setting savings goals, recommended account types, and strategies to optimize your contributions."
                        )
                    ])
                ])
            ])
        elif page == "Estate Planning":
            return dbc.Container([
                html.H2("Estate Planning", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "This page provides information on estate planning. "
                            "Here you can find advice on setting savings goals, recommended account types, and strategies to optimize your contributions."
                        )
                    ])
                ])
            ])
        elif page == "Life Insurance":
            return dbc.Container([
                html.H2("Life Insurance", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "This page provides information on life insurance. "
                            "Here you can find advice on setting savings goals, recommended account types, and strategies to optimize your contributions."
                        )
                    ])
                ])
            ])
        else:
            return dbc.Container([
                html.H2(f"{page} Page", className="text-primary mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(f"Content for {page} coming soon.")
                    ])
                ])
            ])
    except Exception as e:
        print(f"Error rendering {page} page: {e}")
        return dbc.Container([
            html.H2(f"Error Loading {page}", className="text-danger mb-4"),
            dbc.Alert([
                html.H4("An error occurred while loading this page", className="alert-heading"),
                html.P(f"Error details: {str(e)}"),
                html.Hr(),
                html.P("Please try refreshing the page or contact support if the issue persists.", className="mb-0")
            ], color="danger")
        ])
    
@app.callback(
    [Output("portfolio-allocation-chart", "figure"),
     Output("risk-analysis-content", "children")],
    Input("store-user", "data")
)
def update_portfolio_analysis(user_data):
    user_id = user_data.get("user_id", "")
    if not user_id:
        empty_chart = {
            "data": [],
            "layout": {
                "title": "Portfolio Allocation",
                "annotations": [{
                    "text": "No portfolio data available",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16}
                }]
            }
        }
        return empty_chart, html.P("Please generate your portfolio first to view risk analysis.")
    
    positions = get_optimized_positions(user_id)
    if not positions:
        empty_chart = {
            "data": [],
            "layout": {
                "title": "Portfolio Allocation",
                "annotations": [{
                    "text": "No portfolio data available",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16}
                }]
            }
        }
        return empty_chart, html.P("No portfolio positions found. Please generate your portfolio first.")
    
    stock_service = StockService()
    
    # Get performance data for the holdings
    try:
        performance = stock_service.get_portfolio_performance(positions)
        
        if not performance['holdings']:
            empty_chart = {
                "data": [],
                "layout": {
                    "title": "Portfolio Allocation",
                    "annotations": [{
                        "text": "No valid stock data available",
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 16}
                    }]
                }
            }
            return empty_chart, html.P("No valid stock data found for your portfolio symbols.")
        
        # Create allocation pie chart
        import plotly.graph_objects as go
        labels = [h['symbol'] for h in performance['holdings']]
        values = [h['value'] for h in performance['holdings']]
        
        allocation_chart = {
            "data": [
                {
                    "type": "pie",
                    "labels": labels,
                    "values": values,
                    "hole": 0.4,
                    "marker": {
                        "colors": [
                            "#4285F4", "#EA4335", "#FBBC05", "#34A853", 
                            "#FF6D01", "#46BDC6", "#7F00FF", "#00A6ED"
                        ]
                    },
                    "textinfo": "label+percent",
                    "hoverinfo": "label+value+percent"
                }
            ],
            "layout": {
                "title": "Portfolio Allocation",
                "showlegend": True,
                "legend": {"orientation": "h", "yanchor": "bottom", "y": -0.2},
                "margin": {"l": 30, "r": 30, "t": 30, "b": 30}
            }
        }
        
        # Calculate risk metrics
        metrics = calculate_portfolio_metrics(performance)
        
        # Ensure risk_metrics exists and has default values if needed
        if 'risk_metrics' not in metrics:
            metrics['risk_metrics'] = {
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'diversification_score': 0.0,
                'risk_assessment': 'Unable to calculate risk metrics',
                'recommendations': ['Consider consulting a financial advisor']
            }
        
        risk_metrics = metrics['risk_metrics']
        
        # Ensure all required keys exist
        default_values = {
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'diversification_score': len(labels) / 10.0 if labels else 0.0,  # Simple diversification based on number of stocks
            'risk_assessment': 'Risk assessment not available',
            'recommendations': ['Consider diversifying your portfolio across different asset classes']
        }
        
        for key, value in default_values.items():
            if key not in risk_metrics:
                risk_metrics[key] = value
        
        # Create risk analysis content
        risk_analysis = [
            dbc.Row([
                dbc.Col([
                    html.H6("Volatility", className="text-muted"),
                    html.H4(f"{risk_metrics['volatility']:.2f}%", className="text-primary")
                ], width=6),
                dbc.Col([
                    html.H6("Sharpe Ratio", className="text-muted"),
                    html.H4(f"{risk_metrics['sharpe_ratio']:.2f}", 
                           className=f"{'text-success' if risk_metrics['sharpe_ratio'] > 1 else 'text-warning'}")
                ], width=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.H6("Diversification Score", className="text-muted"),
                    html.Div([
                        dbc.Progress(
                            value=min(risk_metrics['diversification_score'] * 100, 100),
                            color="success" if risk_metrics['diversification_score'] > 0.7 else 
                                  "warning" if risk_metrics['diversification_score'] > 0.4 else "danger",
                            className="mb-2",
                            style={"height": "10px"}
                        ),
                        html.Span(f"{min(risk_metrics['diversification_score'] * 100, 100):.0f}%")
                    ])
                ], width=12)
            ], className="mb-3"),
            html.H6("Risk Assessment", className="text-muted mt-3"),
            html.P(risk_metrics['risk_assessment'], className="small"),
            html.H6("Recommendations", className="text-muted mt-3"),
            html.Ul([
                html.Li(rec, className="small") for rec in risk_metrics['recommendations']
            ])
        ]
        
        return allocation_chart, risk_analysis
        
    except Exception as e:
        print(f"Error in portfolio analysis: {str(e)}")
        empty_chart = {
            "data": [],
            "layout": {
                "title": "Portfolio Allocation",
                "annotations": [{
                    "text": "Error loading chart data",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16}
                }]
            }
        }
        
        # Create a simplified risk analysis with error message
        error_risk_analysis = [
            html.Div(className="alert alert-danger", children=[
                html.H6("Error Loading Risk Analysis", className="alert-heading"),
                html.P(f"An error occurred: {str(e)}"),
                html.Hr(),
                html.P("The system was unable to calculate risk metrics for your portfolio.")
            ]),
            html.H6("Default Risk Assessment", className="text-muted mt-3"),
            html.P("Your portfolio contains a mix of assets, but we cannot analyze the risk profile at this moment.", className="small"),
            html.H6("General Recommendations", className="text-muted mt-3"),
            html.Ul([
                html.Li("Diversify across different asset classes (stocks, bonds, real estate)", className="small"),
                html.Li("Consider your time horizon and risk tolerance when investing", className="small"),
                html.Li("Regularly rebalance your portfolio to maintain target allocations", className="small")
            ])
        ]
        
        return empty_chart, error_risk_analysis

@app.callback(
    [Output("portfolio-holdings-table", "children"),
     Output("portfolio-performance-chart", "figure"),
     Output("portfolio-metrics", "children")],
    Input("store-user", "data")
)
def update_portfolio_data(user_data):
    user_id = user_data.get("user_id", "")
    if not user_id:
        return "No portfolio positions found. Please generate your portfolio first.", charts.create_portfolio_chart(None), []
    
    positions = get_optimized_positions(user_id)
    if not positions:
        return "No portfolio positions found. Please generate your portfolio first.", charts.create_portfolio_chart(None), []
    
    stock_service = StockService()
    
    # Get performance data for the holdings table
    try:
        performance = stock_service.get_portfolio_performance(positions)
        
        if not performance['holdings']:
            return "No valid stock data found for your portfolio symbols.", charts.create_portfolio_chart(None), [
                dbc.Alert(
                    "No valid stock data found for your portfolio. Please check your stock symbols.",
                    color="warning"
                )
            ]
        
        # Create a nicely formatted holdings table like in Streamlit
        holdings_df = pd.DataFrame(performance['holdings'])
        
        # Create a formatted table
        holdings_table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Symbol"), 
                    html.Th("Quantity"),
                    html.Th("Value", className="text-end"),
                    html.Th("Daily Change", className="text-end")
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(holding['symbol']),
                    html.Td(f"{holding['quantity']:,}"),
                    html.Td(f"${holding['value']:,.2f}", className="text-end"),
                    html.Td([
                        html.Span(
                            f"${holding['daily_change']:+,.2f}",
                            className=f"{'text-success' if holding['daily_change'] >= 0 else 'text-danger'}"
                        )
                    ], className="text-end")
                ]) for holding in performance['holdings']
            ])
        ], bordered=True, hover=True, responsive=True, striped=True)
        
        # Create metrics cards
        metrics = calculate_portfolio_metrics(performance)
        metrics_cards = [
            dbc.Card(
                dbc.CardBody([
                    html.H5("Total Value", className="card-title text-muted"),
                    html.H3(f"${metrics['total_value']:,.2f}"),
                    html.P([
                        html.Span(
                            f"{metrics['daily_return']:+.2f}%", 
                            className=f"{'text-success' if metrics['daily_return'] >= 0 else 'text-danger'}"
                        ),
                        html.Span(" Today")
                    ])
                ]),
                className="text-center m-2"
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H5("YTD Return", className="card-title text-muted"),
                    html.H3([
                        html.Span(
                            f"{metrics['ytd_return']:+.2f}%",
                            className=f"{'text-success' if metrics['ytd_return'] >= 0 else 'text-danger'}"
                        )
                    ])
                ]),
                className="text-center m-2"
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H5("Diversification", className="card-title text-muted"),
                    html.H3(f"{metrics['risk_metrics']['diversification_score']*100:.0f}%")
                ]),
                className="text-center m-2"
            )
        ]
        
        # Generate the chart figure using the same performance data
        try:
            # Use the same portfolio value calculation for the chart
            # This ensures consistent data between the table and chart
            valid_symbols = [h['symbol'] for h in performance['holdings']]
            positions_with_data = {symbol: qty for symbol, qty in positions.items() if symbol in valid_symbols}
            
            # Only attempt to create chart if we have valid positions
            if positions_with_data:
                chart_data = stock_service.get_portfolio_chart_data(positions_with_data)
                if chart_data is None or chart_data.empty:
                    figure = charts.create_portfolio_chart(None)
                else:
                    figure = charts.create_portfolio_chart(chart_data)
            else:
                figure = charts.create_portfolio_chart(None)
            
            return holdings_table, figure, metrics_cards
            
        except Exception as e:
            print(f"Error creating portfolio chart: {e}")
            return holdings_table, charts.create_portfolio_chart(None), metrics_cards
        
    except Exception as e:
        print(f"Error in portfolio update: {str(e)}")
        return dbc.Alert(
            f"Error loading portfolio: {str(e)}",
            color="danger"
        ), charts.create_portfolio_chart(None), []

if __name__ == '__main__':
    app.run_server(debug=True)