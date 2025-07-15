import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Welcome Page Endpoints
export const getInitialWelcomeData = () => {
  return apiClient.get('/welcome/initial_data');
};

export const submitFinancialPlan = (data) => {
  // data should match FinancialPlanRequest model: { user_name, current_savings, annual_income, investment_goals }
  return apiClient.post('/welcome/financial_plan', data);
};

// News Tracker Page Endpoints
export const getMarketNews = (limit = 10) => {
  return apiClient.get(`/news/market?limit=${limit}`);
};

export const getMarketNewsSentiment = () => {
  return apiClient.get('/news/sentiment');
};

// Portfolio Dashboard Page Endpoints
export const getPortfolioDashboardData = (userId) => {
  if (!userId) return Promise.reject(new Error("User ID is required to fetch portfolio data."));
  return apiClient.get(`/portfolio/dashboard/${userId}`);
};

// Live Trades Page Endpoints
export const getLiveTradesData = (ticker = null) => {
  const params = ticker && ticker !== 'ALL' ? `?ticker=${ticker}` : '';
  return apiClient.get(`/live-trades/data${params}`);
};

export const getAvailableTickers = () => {
  return apiClient.get('/live-trades/tickers');
};

export const getLiveTradesStats = () => {
  return apiClient.get('/live-trades/stats');
};

// Add other API functions here as needed for other pages
// e.g., for portfolio, news, AI insights etc.

export default apiClient; 