# AI Financial Advisor

A comprehensive AI-powered financial advisory platform built with modern web technologies. This application provides personalized investment strategies, real-time market analysis, portfolio optimization, and live trading data visualization.

## 🏗️ Architecture Overview

The application consists of four main components:

1. **Frontend** - React-based web interface
2. **Backend API** - FastAPI REST API server
3. **Dash Application** - Interactive analytics dashboard
4. **Streaming Service** - Real-time trade data processor

## 🚀 Features

- **Personalized Investment Plans**: AI-generated portfolio recommendations based on user goals
- **Real-time Portfolio Tracking**: Live portfolio performance monitoring
- **Market News Integration**: Curated financial news with sentiment analysis
- **AI-Powered Insights**: Market analysis and investment recommendations
- **Live Trading Data**: Real-time trade visualization and streaming
- **Risk Analysis**: Comprehensive portfolio risk assessment
- **Interactive Charts**: Advanced data visualization with Plotly

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 16+** and **npm**
- **SingleStore Database** (or compatible MySQL database)
- **Git**

## 🔧 Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/fin_demo_v3.git
cd fin_demo_v3
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following configuration:

```env
# Database Configuration
host=your-singlestore-host.com
port=3306
user=your-database-username
password=your-database-password
database=your-database-name

# Streaming Configuration
MODE=db
BATCH_SIZE=10
NUM_THREADS=8
LOG_INTERVAL=5

# API Keys (Add as needed)
# OPENAI_API_KEY=your-openai-api-key
# NEWS_API_KEY=your-news-api-key
# ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# Application Settings
DEBUG=True
ENVIRONMENT=development
```

### 3. Database Setup

Ensure your SingleStore database has the necessary tables. The application expects the following tables:
- `optimized_portfolio`
- `clients`
- `live_trades`
- `news_articles` (if using news features)

## 🛠️ Installation

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Return to root directory
cd ..
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to root directory
cd ..
```

### Dash Application Dependencies

```bash
# Install additional dependencies for Dash app (if not in virtual environment)
pip install dash dash-bootstrap-components plotly pandas singlestoredb python-dotenv
```

## 🚀 Running the Application

### Method 1: Run All Components Separately

#### 1. Start the Backend API Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

The API server will start on `http://localhost:8000`

#### 2. Start the Frontend Development Server

```bash
# In a new terminal
cd frontend
npm start
```

The React application will start on `http://localhost:3000`

#### 3. Start the Dash Application

```bash
# In a new terminal, from the root directory
source backend/venv/bin/activate  # On Windows: backend\venv\Scripts\activate
python dash_app.py
```

The Dash application will start on `http://localhost:8050`

#### 4. Start the Streaming Service

```bash
# In a new terminal, from the root directory
cd streaming
source ../backend/venv/bin/activate  # On Windows: ..\backend\venv\Scripts\activate
python main.py
```

### Method 2: Using Development Scripts (Recommended)

Create the following scripts for easier development:

#### `start-dev.sh` (macOS/Linux)

```bash
#!/bin/bash

# Start all services in separate terminal windows/tabs
echo "Starting AI Financial Advisor Development Environment..."

# Start backend
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && source venv/bin/activate && python run.py"'

# Start frontend
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/frontend && npm start"'

# Start Dash app
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)' && source backend/venv/bin/activate && python dash_app.py"'

# Start streaming service
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/streaming && source ../backend/venv/bin/activate && python main.py"'

echo "All services started! Check the terminal windows for status."
```

#### `start-dev.bat` (Windows)

```batch
@echo off
echo Starting AI Financial Advisor Development Environment...

start "Backend API" cmd /k "cd backend && venv\Scripts\activate && python run.py"
start "Frontend" cmd /k "cd frontend && npm start"
start "Dash App" cmd /k "backend\venv\Scripts\activate && python dash_app.py"
start "Streaming" cmd /k "cd streaming && ..\backend\venv\Scripts\activate && python main.py"

echo All services started! Check the command prompt windows for status.
```

Make the script executable (macOS/Linux):
```bash
chmod +x start-dev.sh
./start-dev.sh
```

## 📱 Application URLs

Once all services are running:

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Dash Application**: http://localhost:8050

## 📂 Project Structure

```
fin_demo_v3/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   ├── models/            # Data models
│   │   ├── services/          # Business logic
│   │   ├── core/              # Configuration
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Backend startup script
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── pages/            # React pages
│   │   ├── services/         # API services
│   │   └── App.js            # Main React component
│   ├── public/
│   └── package.json          # Node.js dependencies
├── streaming/                 # Real-time data processor
│   ├── main.py               # Streaming service
│   └── trades_data.csv       # Sample trade data
├── components/               # Dash components
│   ├── portfolio.py
│   ├── news.py
│   └── charts.py
├── services/                 # Shared services
│   ├── ai_service.py
│   ├── stock_service.py
│   └── news_service.py
├── utils/                    # Utility functions
│   └── data_utils.py
├── dash_app.py              # Main Dash application
├── .env                     # Environment variables
└── README.md               # This file
```

## 🔍 Usage Guide

### Getting Started

1. **Access the Frontend**: Navigate to http://localhost:3000
2. **Create Your Profile**: Enter your name, savings, income, and investment goals
3. **Generate Portfolio**: Click "Create My Financial Plan" to get AI recommendations
4. **Explore Features**: Use the navigation to explore different sections

### Key Features

#### Portfolio Dashboard
- View your optimized portfolio allocation
- Monitor performance metrics
- Analyze risk factors

#### News Tracker
- Stay updated with financial news
- AI-powered sentiment analysis
- Market trend insights

#### Live Trades
- Real-time trading data visualization
- Filter by specific stocks
- Track market movements

#### AI Insights
- Personalized portfolio analysis
- Market sentiment evaluation
- Investment recommendations

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
cd backend
flake8 .

# JavaScript linting
cd frontend
npm run lint
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify your database credentials in `.env`
   - Ensure your database server is running
   - Check network connectivity to database host

2. **Port Already in Use**
   - Kill existing processes: `lsof -ti:8000 | xargs kill -9`
   - Or use different ports in the configuration

3. **Module Import Errors**
   - Ensure virtual environment is activated
   - Install missing dependencies: `pip install -r requirements.txt`

4. **React Build Errors**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules: `rm -rf node_modules && npm install`

### Logs and Debugging

- **Backend logs**: Check the terminal running `python run.py`
- **Frontend logs**: Check browser console and terminal running `npm start`
- **Dash logs**: Check the terminal running `python dash_app.py`
- **Database logs**: Check your SingleStore dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation at http://localhost:8000/docs

---

**Happy Trading! 📈** 