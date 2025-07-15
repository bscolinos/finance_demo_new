import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Form, Badge, Alert } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { AppContext } from '../AppContext';
import { getLiveTradesData, getAvailableTickers, getLiveTradesStats } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const LiveTradesPage = () => {
  const { theme } = useContext(AppContext);
  const [tradesData, setTradesData] = useState([]);
  const [availableTickers, setAvailableTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState('ALL');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch available tickers on component mount
  useEffect(() => {
    const fetchTickers = async () => {
      try {
        const response = await getAvailableTickers();
        if (response.data.status === 'success') {
          setAvailableTickers(response.data.tickers);
        }
      } catch (err) {
        console.error('Error fetching tickers:', err);
        setError('Failed to load ticker options');
      }
    };

    fetchTickers();
  }, []);

  // Fetch trades data and stats
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch live trades data
      const tradesResponse = await getLiveTradesData(selectedTicker);
      if (tradesResponse.data.status === 'success') {
        setTradesData(tradesResponse.data.data);
      }

      // Fetch stats
      const statsResponse = await getLiveTradesStats();
      if (statsResponse.data.status === 'success') {
        setStats(statsResponse.data.stats);
      }

      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load live trades data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch and set up interval for updates
  useEffect(() => {
    fetchData();
    
    // Set up interval to refresh data every second
    const interval = setInterval(fetchData, 1000);
    
    return () => clearInterval(interval);
  }, [selectedTicker]);

  const handleTickerChange = (event) => {
    setSelectedTicker(event.target.value);
  };

  // Prepare chart data
  const getChartData = () => {
    if (!tradesData || tradesData.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }

    // Group data by ticker
    const tickerGroups = {};
    tradesData.forEach(trade => {
      if (!tickerGroups[trade.ticker]) {
        tickerGroups[trade.ticker] = [];
      }
      tickerGroups[trade.ticker].push(trade);
    });

    // Generate colors for different tickers
    const colors = [
      '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
      '#9966FF', '#FF9F40', '#C9CBCF' // Removed one duplicate color
    ];

    const datasets = [];

    Object.keys(tickerGroups).forEach((ticker, index) => {
      const tickerData = tickerGroups[ticker];
      const color = colors[index % colors.length];
      
      // Price line dataset
      datasets.push({
        label: ticker,
        data: tickerData.map(trade => ({
          x: new Date(trade.localTS).toLocaleTimeString(),
          y: trade.price
        })),
        borderColor: color,
        backgroundColor: color + '20',
        tension: 0.1,
        fill: false,
        pointRadius: 2,
        pointHoverRadius: 5,
        yAxisID: 'y', // Ensure price uses the main y-axis
      });

      // SMA line dataset (only if a specific ticker is selected and SMA data is present)
      if (selectedTicker && selectedTicker !== 'ALL' && selectedTicker === ticker && tickerData.some(trade => trade.sma !== null && trade.sma !== undefined)) {
        datasets.push({
          label: `${ticker} SMA (5-period)`,
          data: tickerData.map(trade => ({
            x: new Date(trade.localTS).toLocaleTimeString(),
            y: trade.sma
          })).filter(point => point.y !== null && point.y !== undefined), // Filter out points where SMA is null
          borderColor: '#0066FF', // Use bright blue for SMA line - much better contrast against pink/orange
          borderDash: [5, 5], // Make SMA line dashed
          backgroundColor: 'transparent',
          tension: 0.1,
          fill: false,
          pointRadius: 0, // No points on SMA line
          pointHoverRadius: 0,
          yAxisID: 'y', // Ensure SMA uses the same y-axis
        });
      }
    });

    // Get all unique timestamps for labels
    const allTimestamps = [...new Set(tradesData.map(trade => 
      new Date(trade.localTS).toLocaleTimeString()
    ))].sort();

    return {
      labels: allTimestamps,
      datasets: datasets
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: theme.textColor
        }
      },
      title: {
        display: true,
        text: `Live Trades (${selectedTicker === 'ALL' ? 'All Tickers' : selectedTicker})`,
        color: theme.textColor
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time',
          color: theme.textColor
        },
        ticks: {
          color: theme.textColor,
          maxTicksLimit: 10 // Increased for better visibility of 1-minute data
        },
        grid: {
          color: theme.borderColor
        }
      },
      y: { // Main Y-axis for price and SMA
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Price ($)',
          color: theme.textColor
        },
        ticks: {
          color: theme.textColor
        },
        grid: {
          color: theme.borderColor
        }
      },
    },
  };

  return (
    <Container fluid style={{ color: theme.textColor }}>
      <Row className="mb-4">
        <Col>
          <h2 style={{ color: theme.lightPurpleAccent }}>Live Trades</h2>
          <p style={{ color: theme.mutedTextColor }}>
            Real-time trading data updated every second
          </p>
        </Col>
      </Row>

      {error && (
        <Row className="mb-3">
          <Col>
            <Alert variant="danger">{error}</Alert>
          </Col>
        </Row>
      )}

      {/* Stats Cards */}
      {stats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card style={{ backgroundColor: theme.contentBg, borderColor: theme.borderColor }}>
              <Card.Body className="text-center">
                <h5 style={{ color: theme.lightPurpleAccent }}>{stats.total_trades}</h5>
                <small style={{ color: theme.mutedTextColor }}>Total Trades</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card style={{ backgroundColor: theme.contentBg, borderColor: theme.borderColor }}>
              <Card.Body className="text-center">
                <h5 style={{ color: theme.lightPurpleAccent }}>{stats.unique_tickers}</h5>
                <small style={{ color: theme.mutedTextColor }}>Unique Tickers</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card style={{ backgroundColor: theme.contentBg, borderColor: theme.borderColor }}>
              <Card.Body className="text-center">
                <h5 style={{ color: theme.lightPurpleAccent }}>
                  ${stats.avg_price ? stats.avg_price.toFixed(2) : '0.00'}
                </h5>
                <small style={{ color: theme.mutedTextColor }}>Avg Price</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card style={{ backgroundColor: theme.contentBg, borderColor: theme.borderColor }}>
              <Card.Body className="text-center">
                <h5 style={{ color: theme.lightPurpleAccent }}>
                  {stats.total_volume ? stats.total_volume.toLocaleString() : '0'}
                </h5>
                <small style={{ color: theme.mutedTextColor }}>Total Volume</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Controls and Chart */}
      <Row>
        <Col>
          <Card style={{ backgroundColor: theme.contentBg, borderColor: theme.borderColor }}>
            <Card.Header style={{ backgroundColor: theme.sidebarBg, borderColor: theme.borderColor }}>
              <Row className="align-items-center">
                <Col md={4}>
                  <Form.Group>
                    <Form.Label style={{ color: theme.textColor }}>Filter by Ticker:</Form.Label>
                    <Form.Select 
                      value={selectedTicker} 
                      onChange={handleTickerChange}
                      style={{ 
                        backgroundColor: theme.darkBg, 
                        borderColor: theme.borderColor,
                        color: theme.textColor 
                      }}
                    >
                      {availableTickers.map(ticker => (
                        <option key={ticker.value} value={ticker.value}>
                          {ticker.label}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <div className="text-center">
                    {loading && <Badge bg="warning">Updating...</Badge>}
                    {!loading && (
                      <Badge bg="success">
                        {tradesData.length} trades loaded
                      </Badge>
                    )}
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-end">
                    <small style={{ color: theme.mutedTextColor }}>
                      Last updated: {lastUpdate.toLocaleTimeString()}
                    </small>
                  </div>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <div style={{ height: '500px' }}>
                {tradesData.length > 0 ? (
                  <Line data={getChartData()} options={chartOptions} />
                ) : (
                  <div className="d-flex justify-content-center align-items-center h-100">
                    <div className="text-center">
                      <h5 style={{ color: theme.mutedTextColor }}>No Data Available</h5>
                      <p style={{ color: theme.mutedTextColor }}>
                        {loading ? 'Loading live trades data...' : 'No trades found for the selected timeframe'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default LiveTradesPage; 