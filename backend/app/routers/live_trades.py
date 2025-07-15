from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import os
import pandas as pd
import singlestoredb as s2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

router = APIRouter()

# Database configuration
config = {
    "host": os.getenv('host'),
    "port": os.getenv('port'),
    "user": os.getenv('user'),
    "password": os.getenv('password'),
    "database": os.getenv('database')
}

def fetch_live_trades():
    """Fetch live trades data from the database"""
    query = """
    SELECT localTS, ticker, price, size
      FROM live_trades
     WHERE localTS >= CONVERT_TZ(NOW(), @@session.time_zone, 'America/New_York')
                       - INTERVAL 1 MINUTE
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
        return df.to_dict('records')
    return []

@router.get("/data")
async def get_live_trades_data(ticker: Optional[str] = Query(None, description="Filter by ticker symbol")):
    """
    Get live trades data, optionally filtered by ticker symbol.
    If a specific ticker is requested, a 5-period SMA is calculated.
    """
    try:
        all_trades = fetch_live_trades()
        trades_to_return = []

        if ticker and ticker.upper() != 'ALL':
            # Filter for the specific ticker
            filtered_trades_list = [t for t in all_trades if t['ticker'] == ticker.upper()]
            
            if filtered_trades_list:
                df_ticker = pd.DataFrame(filtered_trades_list)
                df_ticker.sort_values('localTS', inplace=True) # Ensure correct order for SMA
                
                sma_window = 5
                if len(df_ticker) >= 1: # Calculate SMA if there are any trades
                    # Calculate SMA. NaNs will be present for initial periods if len < sma_window.
                    # min_periods=1 ensures SMA is calculated even if fewer than sma_window points, starting with mean of available points.
                    df_ticker['sma'] = df_ticker['price'].rolling(window=sma_window, min_periods=1).mean().round(4)
                else:
                    df_ticker['sma'] = None # Should not happen if filtered_trades_list is not empty
                
                trades_to_return = df_ticker.to_dict(orient='records')
            else:
                trades_to_return = [] # No trades for this specific ticker
        else:
            # Return all trades without SMA if 'ALL' or no ticker specified
            trades_to_return = all_trades
        
        return {
            "status": "success",
            "data": trades_to_return,
            "count": len(trades_to_return)
        }
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in get_live_trades_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching live trades: {str(e)}")

@router.get("/tickers")
async def get_available_tickers():
    """
    Get list of available ticker symbols from live trades data
    """
    try:
        query = """
        SELECT DISTINCT ticker
        FROM live_trades
        WHERE localTS >= CONVERT_TZ(NOW(), @@session.time_zone, 'America/New_York')
                          - INTERVAL 1 HOUR
        ORDER BY ticker
        """
        conn = s2.connect(**config)
        try:
            df = pd.read_sql(query, conn)
        finally:
            conn.close()
        
        tickers = df['ticker'].tolist() if not df.empty else []
        
        # Add 'ALL' option at the beginning
        options = [{"label": "All", "value": "ALL"}]
        options.extend([{"label": ticker, "value": ticker} for ticker in tickers])
        
        return {
            "status": "success",
            "tickers": options
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickers: {str(e)}")

@router.get("/stats")
async def get_live_trades_stats():
    """
    Get statistics about live trades data
    """
    try:
        query = """
        SELECT 
            COUNT(*) as total_trades,
            COUNT(DISTINCT ticker) as unique_tickers,
            MIN(localTS) as earliest_trade,
            MAX(localTS) as latest_trade,
            AVG(price) as avg_price,
            SUM(size) as total_volume
        FROM live_trades
        WHERE localTS >= CONVERT_TZ(NOW(), @@session.time_zone, 'America/New_York')
                          - INTERVAL 5 MINUTE
        """
        conn = s2.connect(**config)
        try:
            df = pd.read_sql(query, conn)
        finally:
            conn.close()
        
        if not df.empty:
            stats = df.iloc[0].to_dict()
            # Convert timestamps to strings for JSON serialization
            if stats['earliest_trade']:
                stats['earliest_trade'] = stats['earliest_trade'].isoformat()
            if stats['latest_trade']:
                stats['latest_trade'] = stats['latest_trade'].isoformat()
        else:
            stats = {
                "total_trades": 0,
                "unique_tickers": 0,
                "earliest_trade": None,
                "latest_trade": None,
                "avg_price": 0,
                "total_volume": 0
            }
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}") 