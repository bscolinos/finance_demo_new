# Live Trades Integration

This document describes the integration of live trades functionality from `dash_app.py` into the main FastAPI/React application.

## Overview

The live trades functionality has been successfully migrated from the Dash application to the main app architecture, providing real-time trading data visualization with automatic updates.

## Backend Changes

### 1. New Router: `backend/app/routers/live_trades.py`
- **Endpoints:**
  - `GET /api/live-trades/data` - Fetch live trades data with optional ticker filtering. If a specific ticker is requested, a 5-period Simple Moving Average (SMA) is calculated and included.
  - `GET /api/live-trades/tickers` - Get available ticker symbols
  - `GET /api/live-trades/stats` - Get trading statistics for the last 5 minutes

- **Features:**
  - Fetches data from the `live_trades` table in SingleStore
  - Filters trades from the last 1 minute (configurable, updated from 5 minutes)
  - Calculates a 5-period SMA for individual ticker requests
  - Supports ticker-specific filtering
  - Returns JSON-serialized data for frontend consumption

### 2. Main App Integration: `backend/app/main.py`
- Added live trades router to the FastAPI application
- Endpoint prefix: `/api/live-trades`

### 3. Database Requirements
- Uses existing SingleStore database configuration
- Queries the `live_trades` table with columns:
  - `localTS` - timestamp
  - `ticker` - stock symbol
  - `price` - trade price
  - `size` - trade volume

## Frontend Changes

### 1. New Page Component: `frontend/src/pages/LiveTradesPage.js`
- **Features:**
  - Real-time chart using Chart.js and react-chartjs-2
  - Displays 5-period SMA as a dashed line when a single ticker is selected
  - Auto-refresh every second
  - Ticker filtering dropdown
  - Statistics display (total trades, unique tickers, average price, total volume)
  - Responsive design with dark theme support
  - Error handling and loading states

### 2. API Service Updates: `frontend/src/services/api.js`
- Added three new API functions:
  - `getLiveTradesData(ticker)` - Fetch trades data
  - `getAvailableTickers()` - Get ticker options
  - `getLiveTradesStats()` - Fetch statistics

### 3. App Router Integration: `frontend/src/App.js`
- Replaced placeholder LiveTradesPage with the full implementation
- Component is automatically available in navigation

### 4. Dependencies: `frontend/package.json`
- Added Chart.js dependencies:
  - `chart.js: ^4.4.0`
  - `react-chartjs-2: ^5.2.0`

## Usage

### Starting the Application

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install  # Chart.js dependencies now included
   npm start
   ```

### Accessing Live Trades

1. Navigate to the application (http://localhost:3000)
2. Click on "Live Trades" in the sidebar navigation
3. Use the ticker dropdown to filter by specific stocks or view all
4. Chart automatically updates every second with new data

## Key Features

### Real-time Updates
- Data refreshes every 1 second automatically
- Shows last update timestamp
- Loading indicator during data fetch

### Interactive Chart
- Multiple ticker support with color-coded lines
- 5-period Simple Moving Average (SMA) displayed for single-ticker views (dashed line)
- Hover tooltips showing exact values (price and SMA if applicable)
- Time-based X-axis with proper formatting
- Responsive design

### Statistics Dashboard
- Total trades count
- Unique tickers count
- Average price across all trades
- Total volume traded

### Filtering
- Filter by individual ticker symbols
- "All" option to view all tickers simultaneously
- Dynamic ticker list based on available data

## Database Schema

The live trades functionality expects a table with this structure:

```sql
CREATE TABLE live_trades (
    localTS DATETIME,
    ticker VARCHAR(10),
    price DECIMAL(10, 2),
    size INT,
    -- additional columns as needed
    INDEX (localTS),
    INDEX (ticker)
);
```

## Configuration

### Environment Variables
Ensure these are set in your `.env` file:
```
host=your_singlestore_host
port=your_singlestore_port
user=your_singlestore_user
password=your_singlestore_password
database=your_singlestore_database
```

### Customization Options

#### Update Frequency
To change the refresh rate, modify the interval in `LiveTradesPage.js`:
```javascript
const interval = setInterval(fetchData, 1000); // 1000ms = 1 second
```

#### Time Range
To change the data window, modify the query in `live_trades.py`:
```sql
WHERE localTS >= CONVERT_TZ(NOW(), @@session.time_zone, 'America/New_York')
                  - INTERVAL 1 MINUTE  -- Data is now fetched for the last 1 minute
```

#### Chart Colors
Customize the color palette in `LiveTradesPage.js`:
```javascript
const colors = [
  '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
  '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
];
```

## Migration from Dash App

The following functionality was successfully migrated and enhanced:
- ✅ Real-time data fetching from SingleStore
- ✅ Interactive line charts with SMA for single tickers
- ✅ Ticker filtering
- ✅ Auto-refresh capabilities
- ✅ Time-based visualization
- ✅ Multi-ticker support

## Troubleshooting

### Common Issues

1. **No data showing:**
   - Check database connection
   - Verify `live_trades` table exists and has recent data
   - Check time zone settings in database query

2. **Chart not rendering:**
   - Ensure Chart.js dependencies are installed: `npm install`
   - Check browser console for JavaScript errors

3. **API errors:**
   - Verify backend is running on port 8000
   - Check CORS configuration in `main.py`
   - Validate database credentials in `.env`

### Performance Considerations

- The 1-second refresh rate is suitable for demo purposes
- For production, consider:
  - Implementing WebSocket connections for more efficient real-time updates
  - Adding data compression for large datasets
  - Implementing proper caching strategies
  - Rate limiting API calls

## Next Steps

Potential enhancements:
1. WebSocket integration for true real-time updates
2. Data export functionality
3. More advanced charting options (candlestick, volume bars, customizable SMA periods)
4. Alert system for price thresholds
5. Historical data comparison
6. Performance metrics and analytics 