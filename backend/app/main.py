from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers here once they are created
from app.routers import welcome
from app.routers import news
from app.routers import portfolio
from app.routers import live_trades
# from app.routers import ai_insights, user

app = FastAPI(
    title="AI Financial Advisor API",
    description="API for the AI Financial Advisor application",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing) configuration
origins = [
    "http://localhost:3000",  # Default React development server
    "http://localhost:3001",  # Another common port for React dev
    # Add any other origins if your frontend is served from a different URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the AI Financial Advisor API"}

# Include routers for different sections of the application
app.include_router(welcome.router, prefix="/api/welcome", tags=["Welcome"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(live_trades.router, prefix="/api/live-trades", tags=["Live Trades"])
# Example:
# app.include_router(ai_insights.router, prefix="/ai", tags=["AI Insights"])
# app.include_router(user.router, prefix="/user", tags=["User"])

# If you plan to run this with uvicorn directly:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000) 