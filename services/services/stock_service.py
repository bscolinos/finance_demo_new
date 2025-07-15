import yfinance as yf
import pandas as pd
import numpy as np

class StockService:
    @staticmethod
    def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            raise Exception(f"Failed to fetch stock data for {symbol}: {e}")

    @staticmethod
    def get_portfolio_performance(positions: dict) -> dict:
        """Calculate portfolio performance"""
        performance = {
            'total_value': 0,
            'daily_change': 0,
            'holdings': []
        }
        
        for symbol, quantity in positions.items():
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                
                # Check if we got valid data
                if not info or 'regularMarketPrice' not in info:
                    print(f"Warning: Could not get price data for {symbol}, skipping...")
                    continue
                    
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)  # Default to current if no prev
                
                position_value = current_price * quantity
                daily_change = (current_price - prev_close) * quantity
                
                performance['holdings'].append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'value': position_value,
                    'daily_change': daily_change
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
            idx = yf.Ticker(index)
            info = idx.info
            summary[index] = {
                'name': info.get('shortName', ''),
                'price': info.get('regularMarketPrice', 0),
                'change': info.get('regularMarketChangePercent', 0)
            }
            
        return summary

    def get_portfolio_chart_data(self, positions):
        """Get historical data for portfolio performance charting."""
        if not positions:
            print("No positions provided to get_portfolio_chart_data")
            return pd.DataFrame()
        
        print(f"Getting chart data for positions: {positions}")
        
        try:
            # Get 1 year historical data for each position
            portfolio_value = pd.DataFrame()
            
            for symbol, quantity in positions.items():
                try:
                    print(f"Processing historical data for {symbol} with quantity {quantity}")
                    # Get historical data for this symbol
                    df = self.get_stock_data(symbol, period="1y")
                    
                    # Skip if no data
                    if df is None or df.empty:
                        print(f"No historical data for {symbol}, skipping...")
                        continue
                    
                    print(f"Got data for {symbol} with shape {df.shape}")
                    
                    # Calculate position value over time
                    position_value = df['Close'] * quantity
                    position_df = pd.DataFrame({
                        'date': df.index,
                        symbol: position_value
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
                return pd.DataFrame()
            
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
            
            return result
            
        except Exception as e:
            print(f"Error getting portfolio chart data: {e}")
            import traceback
            traceback.print_exc()
            # Return empty DataFrame on error
            return pd.DataFrame()
