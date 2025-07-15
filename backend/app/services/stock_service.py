import yfinance as yf
import pandas as pd
import numpy as np
import os
import singlestoredb as s2
from typing import Dict, List, Any
import datetime
import time
import random

class StockService:
    # Class-level cache for stock data and info
    _stock_data_cache = {}
    _stock_info_cache = {}
    
    # Common stock prices for consistency (dummy data)
    _dummy_prices = {
        'BND': 78.50,
        'VTI': 245.30,
        'VNQ': 95.75,
        'VTIP': 49.20,
        'SPY': 420.15,
        'QQQ': 350.80,
        'IWM': 185.60,
        'GLD': 182.40,
        'TLT': 95.30,
        'EFA': 75.20
    }

    @staticmethod
    def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
        """Generate dummy stock data instead of fetching from Yahoo Finance"""
        cache_key = f"{symbol}_{period}"
        
        # Check if we have cached data and it's less than 1 hour old
        if cache_key in StockService._stock_data_cache:
            cache_entry = StockService._stock_data_cache[cache_key]
            cache_time = cache_entry["timestamp"]
            current_time = time.time()
            
            # If cache is less than 1 hour old, use it
            if current_time - cache_time < 3600:
                print(f"Using cached data for {symbol} (period: {period})")
                return cache_entry["data"]
        
        # Generate dummy historical data
        print(f"Generating dummy historical data for {symbol}")
        
        # Determine number of days based on period
        if period == "1y":
            days = 365
        elif period == "6mo":
            days = 180
        elif period == "3mo":
            days = 90
        elif period == "1mo":
            days = 30
        else:
            days = 365  # Default to 1 year
        
        # Generate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Get base price for this symbol
        base_price = StockService._dummy_prices.get(symbol, 100.0)
        
        # Generate realistic price data with some volatility
        np.random.seed(hash(symbol) % 2147483647)  # Consistent seed per symbol
        daily_returns = np.random.normal(0.0005, 0.02, len(date_range))  # Small positive drift with 2% daily volatility
        
        prices = [base_price]
        for i in range(1, len(date_range)):
            new_price = prices[-1] * (1 + daily_returns[i])
            prices.append(max(new_price, 1.0))  # Ensure price doesn't go below $1
        
        # Create DataFrame with OHLCV data
        df = pd.DataFrame({
            'Open': [p * random.uniform(0.99, 1.01) for p in prices],
            'High': [p * random.uniform(1.00, 1.03) for p in prices],
            'Low': [p * random.uniform(0.97, 1.00) for p in prices],
            'Close': prices,
            'Volume': [random.randint(100000, 5000000) for _ in prices]
        }, index=date_range)
        
        # Ensure High >= Close >= Low and Open is reasonable
        for i in range(len(df)):
            df.iloc[i, df.columns.get_loc('High')] = max(df.iloc[i, df.columns.get_loc('High')], df.iloc[i, df.columns.get_loc('Close')])
            df.iloc[i, df.columns.get_loc('Low')] = min(df.iloc[i, df.columns.get_loc('Low')], df.iloc[i, df.columns.get_loc('Close')])
        
        # Cache the result
        StockService._stock_data_cache[cache_key] = {
            "data": df,
            "timestamp": time.time()
        }
        
        return df

    def get_optimized_positions(self, user_id: str) -> List[Dict[str, Any]]:
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
            return []

        try:
            query = "SELECT symbol, quantity FROM optimized_portfolio WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            print(f"Optimized positions for user {user_id}: {results}")
        except Exception as e:
            print(f"Error fetching optimized positions: {e}")
            return []
        cursor.close()
        connection.close()

        positions = []
        for row in results:
            # Each row is a tuple (symbol, quantity)
            symbol = row[0]
            quantity = float(row[1])  # Convert to float to match expected type
            positions.append({"symbol": symbol, "quantity": quantity})
        return positions

    @staticmethod
    def get_stock_info(symbol: str) -> Dict[str, Any]:
        """Generate dummy stock info instead of fetching from Yahoo Finance"""
        # Check if we have cached info and it's less than 1 hour old
        if symbol in StockService._stock_info_cache:
            cache_entry = StockService._stock_info_cache[symbol]
            cache_time = cache_entry["timestamp"]
            current_time = time.time()
            
            # If cache is less than 1 hour old, use it
            if current_time - cache_time < 3600:
                print(f"Using cached info for {symbol}")
                return cache_entry["info"]
        
        # Generate dummy stock info
        print(f"Generating dummy stock info for {symbol}")
        
        # Get base price for consistency
        current_price = StockService._dummy_prices.get(symbol, 100.0)
        # Add small random variation to current price
        current_price *= random.uniform(0.98, 1.02)
        
        # Calculate previous close (slight variation)
        prev_close = current_price * random.uniform(0.99, 1.01)
        
        dummy_info = {
            'regularMarketPrice': round(current_price, 2),
            'previousClose': round(prev_close, 2),
            'shortName': f"{symbol} Dummy Stock",
            'longName': f"{symbol} Dummy Corporation",
            'currency': 'USD',
            'marketCap': random.randint(1000000000, 500000000000),  # 1B to 500B
            'volume': random.randint(1000000, 50000000),
            'averageVolume': random.randint(5000000, 25000000),
            'fiftyTwoWeekHigh': current_price * random.uniform(1.1, 1.5),
            'fiftyTwoWeekLow': current_price * random.uniform(0.5, 0.9),
            'dividendYield': random.uniform(0.0, 0.05) if random.random() > 0.3 else 0.0,  # 70% chance of having dividend
            'beta': random.uniform(0.5, 1.8),
            'trailingPE': random.uniform(10, 30) if random.random() > 0.2 else None,
            'forwardPE': random.uniform(12, 25) if random.random() > 0.2 else None,
        }
        
        # Cache the result
        StockService._stock_info_cache[symbol] = {
            "info": dummy_info,
            "timestamp": time.time()
        }
        
        return dummy_info

    @staticmethod
    def get_portfolio_performance(positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio performance"""
        performance = {
            'total_value': 0,
            'daily_change': 0,
            'holdings': []
        }
        
        for position in positions:
            symbol = position["symbol"]
            quantity = position["quantity"]
            try:
                # Use our cached info method instead of direct yf.Ticker access
                info = StockService.get_stock_info(symbol)
                
                # Check if we got valid data
                if not info or 'regularMarketPrice' not in info:
                    print(f"Warning: Could not get price data for {symbol}, skipping...")
                    continue
                    
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)  # Default to current if no prev
                
                position_value = current_price * quantity
                daily_change = (current_price - prev_close) * quantity
                
                # Calculate daily change percentage
                daily_change_percent = 0.0
                if prev_close > 0:
                    daily_change_percent = ((current_price - prev_close) / prev_close) * 100
                
                performance['holdings'].append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'value': position_value,
                    'daily_change': daily_change,
                    'daily_change_percent': round(daily_change_percent, 2)
                })
                
                performance['total_value'] += position_value
                performance['daily_change'] += daily_change
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                # Continue with other stocks if one fails
                continue
        
        return performance

    @staticmethod
    def get_market_summary() -> dict:
        """Get summary of major market indices"""
        indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
        summary = {}
        
        for index in indices:
            try:
                # Use our cached info method
                info = StockService.get_stock_info(index)
                summary[index] = {
                    'name': info.get('shortName', ''),
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChangePercent', 0)
                }
            except Exception as e:
                print(f"Error getting info for index {index}: {e}")
                # Provide placeholder data in case of error
                summary[index] = {
                    'name': index,
                    'price': 0,
                    'change': 0
                }
            
        return summary

    def get_portfolio_chart_data(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get historical data for portfolio performance charting using dummy data.
        Returns a list of dicts like {"timestamp": str, "value": float}.
        The timestamp must be in ISO format string for JavaScript new Date() compatibility.
        """
        if not positions:
            print("No positions provided to get_portfolio_chart_data")
            return self._generate_mock_chart_data()
        
        print(f"Getting chart data for positions: {positions}")
        
        try:
            # Get 1 year historical data for each position using dummy data
            portfolio_value = pd.DataFrame()
            
            for position in positions:
                symbol = position["symbol"]
                quantity = position["quantity"]
                try:
                    print(f"Processing historical data for {symbol} with quantity {quantity}")
                    # Get dummy historical data for this symbol
                    df = self.get_stock_data(symbol, period="1y")
                    
                    # Skip if no data (shouldn't happen with dummy data)
                    if df is None or df.empty:
                        print(f"No historical data for {symbol}, skipping...")
                        continue
                    
                    print(f"Got data for {symbol} with shape {df.shape}")
                    
                    # Calculate position value over time
                    position_value_over_time = df['Close'] * quantity
                    position_df = pd.DataFrame({
                        'date': df.index,
                        symbol: position_value_over_time
                    }).set_index('date')
                    
                    # Add to portfolio value
                    if portfolio_value.empty:
                        portfolio_value = position_df
                    else:
                        portfolio_value = portfolio_value.join(position_df, how='outer')
                except Exception as e:
                    print(f"Error processing historical data for {symbol}: {e}")
                    continue  # Skip this symbol and continue with others
            
            # Check if we have any data
            if portfolio_value.empty:
                print("No portfolio data available after processing all symbols")
                # Return mock data if we couldn't get real data
                return self._generate_mock_chart_data()
            
            print(f"Portfolio value DataFrame shape: {portfolio_value.shape}")
            
            # Fill missing values (e.g., if some stocks have data for dates others don't)
            portfolio_value = portfolio_value.ffill()
            portfolio_value = portfolio_value.bfill()
            
            # Calculate total portfolio value
            portfolio_value['value'] = portfolio_value.sum(axis=1)
            
            # Reset index to get date as a column
            result = portfolio_value.reset_index()[['date', 'value']]
            print(f"Final result shape: {result.shape}")
            
            # Add weekly resampling to smooth the chart (optional)
            if len(result) > 50:  # Only if we have enough data points
                result = result.set_index('date')
                result = result.resample('W').last()  # Weekly resampling
                result = result.reset_index()
            
            # Convert to the format expected by the frontend
            chart_data = []
            for _, row in result.iterrows():
                # Convert timestamp to ISO format string for JavaScript compatibility
                timestamp = row['date']
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    # If it's already a string or other type, convert to string
                    timestamp_str = str(timestamp)
                
                chart_data.append({
                    "timestamp": timestamp_str,
                    "value": float(row['value'])
                })
            
            # Print a sample of the data to debug
            if chart_data:
                print(f"Chart data sample (first 2 points): {chart_data[:2]}")
                print(f"Total chart points: {len(chart_data)}")
                print(f"Timestamp type: {type(chart_data[0]['timestamp'])}")
            else:
                print("No chart data generated")
                
            return chart_data
            
        except Exception as e:
            print(f"Error getting portfolio chart data: {e}")
            import traceback
            traceback.print_exc()
            # Return mock data on error
            return self._generate_mock_chart_data()

    def _generate_mock_chart_data(self) -> List[Dict[str, Any]]:
        """Generate mock chart data when we can't get real data due to rate limiting"""
        print("Generating mock chart data due to rate limiting")
        chart_data = []
        
        # Start date - 1 year ago
        start_date = datetime.datetime.now() - datetime.timedelta(days=365)
        
        # Generate 52 weekly data points (1 year)
        current_value = 10000.0  # Starting portfolio value
        
        for week in range(53):  # 0 to 52 weeks
            # Current date for this data point - convert to ISO string
            current_date = start_date + datetime.timedelta(weeks=week)
            iso_date_str = current_date.isoformat()
            
            # Add some randomness with slight upward trend for realism
            if week > 0:
                # Random change with a slight upward bias
                pct_change = random.uniform(-0.03, 0.04)  # -3% to +4% weekly change
                current_value = current_value * (1 + pct_change)
            
            chart_data.append({
                "timestamp": iso_date_str,  # Use ISO format string
                "value": round(current_value, 2)
            })
        
        # Print a sample to debug
        print(f"Mock chart data generated. Sample (first 2 points): {chart_data[:2]}")
        print(f"Total mock data points: {len(chart_data)}")
        print(f"Timestamp type: {type(chart_data[0]['timestamp'])}")
        
        return chart_data 