from dash import html, dcc
import dash_bootstrap_components as dbc
from services.news_service import NewsService
from services.ai_service import AIService

def display_news_dashboard():
    """Display news dashboard - Dash version with immediate content loading"""
    try:
        # Initialize services and load default market news immediately
        news_service = NewsService()
        ai_service = AIService()
        news_articles = news_service.get_market_news()
        
        # Get sentiment analysis if articles are found
        sentiment = None
        sentiment_component = html.Div()
        if news_articles:
            try:
                sentiment = ai_service.get_market_sentiment(news_articles)
                sentiment_component = get_sentiment_component(sentiment)
            except Exception as e:
                sentiment_component = dbc.Alert(f"Error analyzing sentiment: {str(e)}", color="warning")
        
        # Create articles component
        articles_component = get_news_articles_component(news_articles)
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        id="news-search-input",
                        type="text",
                        placeholder="Enter keywords or stock symbols",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Search News", 
                        id="news-search-button", 
                        color="primary",
                        className="mb-4"
                    )
                ], width=12)
            ]),
            
            # Display sentiment analysis immediately
            html.Div(sentiment_component, id="news-sentiment-container", className="mb-4"),
            
            # Display news articles immediately
            html.H4("Latest News", className="mb-3"),
            html.Div(articles_component, id="news-articles-container")
        ])
    except Exception as e:
        return dbc.Alert(
            f"Error loading news dashboard: {str(e)}",
            color="danger"
        )

def get_sentiment_component(sentiment):
    """Creates a sentiment analysis component for the news dashboard"""
    if not sentiment:
        return html.Div()
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Market Sentiment"),
                    html.H3(sentiment['overall_sentiment'], className="text-primary")
                ], width=6),
                dbc.Col([
                    html.H5("Confidence"),
                    html.H3(f"{sentiment['confidence']*100:.1f}%", className="text-primary")
                ], width=6)
            ]),
            html.H5("Key Factors:", className="mt-3"),
            html.Ul([
                html.Li(factor) for factor in sentiment['key_factors']
            ]),
            html.H5("Market Outlook:", className="mt-3"),
            html.P(sentiment['market_outlook'])
        ])
    ])

def get_news_articles_component(articles):
    """Creates news articles components for the news dashboard"""
    if not articles:
        return html.Div([
            dbc.Alert("No news articles found. Try a different search term.", color="info")
        ])
    
    # Create a list of article components using accordion
    article_items = []
    for i, article in enumerate(articles):
        article_items.append(
            dbc.AccordionItem(
                [
                    dbc.Row([
                        dbc.Col([
                            html.Strong("Source: "),
                            html.Span(article['source']['name'])
                        ], width=6),
                        dbc.Col([
                            html.Strong("Published: "),
                            html.Span(article['publishedAt'])
                        ], width=6)
                    ], className="mb-2"),
                    html.P(article['description'], className="mb-3"),
                    html.A("Read more", href=article['url'], target="_blank", className="btn btn-sm btn-outline-primary")
                ],
                title=article['title'],
                item_id=f"article-{i}"
            )
        )
    
    return dbc.Accordion(article_items, start_collapsed=True, always_open=False)

def process_news_search(search_query=None):
    """Process news search and return articles and sentiment components"""
    try:
        news_service = NewsService()
        ai_service = AIService()
        
        # Get news based on search query or default to market news
        if search_query:
            from services.tracking_service import TrackingService
            TrackingService.log_activity("news_search", {"query": search_query})
            news_articles = news_service.search_news(search_query)
        else:
            news_articles = news_service.get_market_news()
        
        # Get sentiment analysis if articles are found
        sentiment = None
        if news_articles:
            sentiment = ai_service.get_market_sentiment(news_articles)
        
        # Create and return components
        sentiment_component = get_sentiment_component(sentiment)
        articles_component = get_news_articles_component(news_articles)
        
        return sentiment_component, articles_component
    except Exception as e:
        return dbc.Alert(f"Error processing news: {str(e)}", color="danger"), None
