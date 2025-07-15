import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';
import Plot from 'react-plotly.js'; // For charts

import { AppContext } from '../AppContext';
import { getPortfolioDashboardData } from '../services/api';

const PortfolioDashboardPage = () => {
    const { userData, theme } = useContext(AppContext); // Get user_id and theme from global state
    const [dashboardData, setDashboardData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (userData && userData.user_id) {
            setIsLoading(true);
            getPortfolioDashboardData(userData.user_id)
                .then(response => {
                    setDashboardData(response.data);
                })
                .catch(err => {
                    console.error("Error fetching portfolio dashboard data:", err);
                    setError(err.response?.data?.detail || "Could not load portfolio dashboard.");
                })
                .finally(() => {
                    setIsLoading(false);
                });
        } else {
            // This case might happen if context is not loaded yet, or no user_id
            // A small delay or check might be needed, or rely on userData update to trigger fetch
            setIsLoading(false);
            // setError("User information not available. Cannot load dashboard."); 
            // Or, show a message to create a portfolio if that's the implied state
        }
    }, [userData]); // Re-fetch if userData (and thus user_id) changes

    // Helper style objects & functions based on theme
    const themedCardStyle = {
        backgroundColor: theme.cardBg,
        color: theme.textColor,
        border: `1px solid ${theme.cardBorder}`,
        marginBottom: '1.5rem'
    };

    const themedCardHeaderStyle = {
        backgroundColor: theme.sidebarBg, // A slightly different background for headers
        color: theme.lightPurpleAccent,
        borderBottom: `1px solid ${theme.borderColor}`
    };

    const themedAlertStyle = (variant) => {
        let style = { 
            backgroundColor: theme.cardBg, 
            color: theme.textColor, 
            borderColor: theme.borderColor, 
            border: `1px solid ${theme.borderColor}`,
            padding: '1rem'
        };
        if (variant === "danger" || variant === "warning") {
            style.backgroundColor = '#58181F';
            style.color = '#F8D7DA';
            style.borderColor = '#C93A4C';
        } else if (variant === "info") {
            style.backgroundColor = '#1E4A5F';
            style.color = '#CFF4FC';
            style.borderColor = '#4285F4';
        }
        return style;
    };
    
    const themedButtonStyle = {
        backgroundColor: theme.mediumPurpleAccent,
        borderColor: theme.mediumPurpleAccent,
        color: theme.activeLinkText,
    };

    const plotlyLayoutDefaults = {
        paper_bgcolor: theme.cardBg,
        plot_bgcolor: theme.cardBg,
        font: { color: theme.textColor },
        legend: {
            font: { color: theme.textColor },
            bgcolor: theme.sidebarBg, // Or a slightly transparent version of cardBg
            bordercolor: theme.borderColor,
            borderwidth: 1
        },
        titlefont: { color: theme.lightPurpleAccent }, // For main title
        xaxis: {
            titlefont: { color: theme.textColor },
            tickfont: { color: theme.textColor },
            gridcolor: theme.borderColor, // Color of grid lines
            linecolor: theme.borderColor, // Color of the axis line itself
            zerolinecolor: theme.borderColor
        },
        yaxis: {
            titlefont: { color: theme.textColor },
            tickfont: { color: theme.textColor },
            gridcolor: theme.borderColor,
            linecolor: theme.borderColor,
            zerolinecolor: theme.borderColor
        }
    };

    if (isLoading) {
        return <div className="text-center p-5" style={{color: theme.textColor, backgroundColor: theme.contentBg, height: '100vh'}}><Spinner animation="border" style={{color: theme.lightPurpleAccent}} /><p className="mt-2">Loading Portfolio Dashboard...</p></div>;
    }

    if (error) {
        return <Container style={{backgroundColor: theme.contentBg, padding: '2rem', borderRadius: '8px'}}><Alert variant="danger" style={themedAlertStyle('danger')} className="mt-4">{error}</Alert></Container>;
    }
    
    if (!userData || !userData.user_id) {
         return (
            <Container className="mt-4 text-center" style={{backgroundColor: theme.contentBg, padding: '2rem', borderRadius: '8px'}}>
                <Alert variant="warning" style={themedAlertStyle('warning')}>
                    Please log in or provide your user details on the Welcome page to view your portfolio dashboard.
                </Alert>
                <Link to="/welcome"><Button style={themedButtonStyle}>Go to Welcome Page</Button></Link>
            </Container>
        );
    }

    if (!dashboardData || !dashboardData.user_has_portfolio) {
        return (
            <Container className="mt-4 text-center" style={{backgroundColor: theme.contentBg, padding: '2rem', borderRadius: '8px'}}>
                <Alert variant="info" style={themedAlertStyle('info')}>
                    {dashboardData?.message || "No portfolio data found. Please create your financial plan on the Welcome page first."}
                </Alert>
                <Link to="/welcome"><Button style={themedButtonStyle}>Create Financial Plan</Button></Link>
            </Container>
        );
    }

    // Destructure for easier access
    const {
        allocation_chart_data,
        risk_metrics,
        performance_chart_data,
        holdings_performance,
        portfolio_summary_metrics
    } = dashboardData;

    // Render Portfolio Allocation Chart
    const renderAllocationChart = () => {
        if (!allocation_chart_data || allocation_chart_data.length === 0) return <p style={{color: theme.mutedTextColor}}>No allocation data available.</p>;
        
        // Define a color sequence for pie chart segments, can be expanded
        const pieChartColors = [theme.lightPurpleAccent, theme.mediumPurpleAccent, '#f06292', '#fff176', '#81c784', '#64b5f6'];

        return (
            <Plot
                data={[
                    {
                        labels: allocation_chart_data.map(d => d.label),
                        values: allocation_chart_data.map(d => d.value),
                        type: 'pie',
                        hole: 0.4,
                        marker: {
                            colors: pieChartColors,
                            line: { color: theme.cardBg, width: 2 } // Add lines between segments
                        },
                        textinfo: "label+percent",
                        hoverinfo: "label+value+percent",
                        insidetextfont: { color: theme.darkBg }, // Make text inside segments readable
                        outsidetextfont: { color: theme.textColor }
                    }
                ]}
                layout={{
                    ...plotlyLayoutDefaults,
                    title: 'Portfolio Allocation',
                    showlegend: true,
                    legend: { 
                        ...plotlyLayoutDefaults.legend,
                        orientation: 'h', yanchor: 'bottom', y: -0.2, xanchor: 'center', x: 0.5 
                    },
                    height: 400,
                    margin: { l: 20, r: 20, t: 50, b: 20 }
                }}
                style={{ width: '100%', height: '100%' }}
                useResizeHandler={true}
            />
        );
    };

    // Render Risk Analysis
    const renderRiskAnalysis = () => {
        if (!risk_metrics) return <p style={{color: theme.mutedTextColor}}>No risk analysis available.</p>;
        return (
            <>
                <h5 style={{color: theme.lightPurpleAccent}}>Risk Analysis</h5>
                <p><strong>Volatility:</strong> {risk_metrics.volatility}%</p>
                <p><strong>Sharpe Ratio:</strong> {risk_metrics.sharpe_ratio}</p>
                <p><strong>Diversification:</strong> {risk_metrics.diversification_score * 100}%</p>
                <p><strong>Assessment:</strong> {risk_metrics.risk_assessment}</p>
                <h6 style={{color: theme.lightPurpleAccent}} className="mt-3">Recommendations:</h6>
                <ul style={{paddingLeft: '20px'}}>
                    {risk_metrics.recommendations.map((rec, i) => <li key={`risk-rec-${i}`}>{rec}</li>)}
                </ul>
            </>
        );
    };

    // Render Performance Line Chart
    const renderPerformanceChart = () => {
        if (!performance_chart_data || performance_chart_data.length === 0) return <p style={{color: theme.mutedTextColor}}>No performance data available for chart.</p>;
        return (
            <Plot
                data={[
                    {
                        x: performance_chart_data.map(d => new Date(d.timestamp)),
                        y: performance_chart_data.map(d => d.value),
                        type: 'scatter',
                        mode: 'lines+markers',
                        marker: { color: theme.mediumPurpleAccent },
                        line: { color: theme.mediumPurpleAccent },
                        name: 'Portfolio Value'
                    }
                ]}
                layout={{
                    ...plotlyLayoutDefaults,
                    title: 'Portfolio Value Over Time',
                    xaxis: { ...plotlyLayoutDefaults.xaxis, title: 'Date' },
                    yaxis: { ...plotlyLayoutDefaults.yaxis, title: 'Portfolio Value ($)' },
                    height: 400,
                    margin: { l: 60, r: 30, t: 50, b: 50 } // Adjusted left margin for y-axis title
                }}
                style={{ width: '100%', height: '100%' }}
                useResizeHandler={true}
            />
        );
    };

    // Render Holdings Table
    const renderHoldingsTable = () => {
        if (!holdings_performance || holdings_performance.length === 0) return <p style={{color: theme.mutedTextColor}}>No holdings information available.</p>;
        return (
            // Table uses Bootstrap's dark variant and then we override for specific theme needs
            <Table striped bordered hover responsive size="sm" variant="dark" style={{color: theme.textColor, borderColor: theme.borderColor}}>
                <thead style={{borderColor: theme.borderColor}}>
                    <tr style={{borderColor: theme.borderColor}}>
                        {['Symbol', 'Quantity', 'Value ($)', 'Day Change ($)', 'Day Change (%)'].map(header => (
                            <th key={header} style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderColor: theme.borderColor}} className={header.includes('$') || header.includes('%') ? 'text-end' : ''}>{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {holdings_performance.map((h, i) => {
                        // Calculate daily_change_percent if it's missing
                        const percent = h.daily_change_percent !== undefined ? h.daily_change_percent : 
                                        (h.value && h.value !== 0 && h.daily_change !== undefined) ? 
                                        (h.daily_change / (h.value - h.daily_change)) * 100 : 0;
                        
                        return (
                            <tr key={`holding-${i}`} style={{borderColor: theme.borderColor}}>
                                <td style={{borderColor: theme.borderColor}}>{h.symbol}</td>
                                <td style={{borderColor: theme.borderColor}}>{h.quantity.toLocaleString()}</td>
                                <td style={{borderColor: theme.borderColor}} className="text-end">{h.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style={{borderColor: theme.borderColor}} className={`text-end ${h.daily_change >= 0 ? 'text-success-themed' : 'text-danger-themed'}`}>
                                    {h.daily_change.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                </td>
                                <td style={{borderColor: theme.borderColor}} className={`text-end ${percent >= 0 ? 'text-success-themed' : 'text-danger-themed'}`}>
                                    {percent.toFixed(2)}%
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </Table>
        );
    };

    // Render Metrics Cards
    const renderMetricsCards = () => {
        if (!portfolio_summary_metrics) return null;
        const metricCardStyle = {...themedCardStyle, textAlign: 'center', height: '100%'};
        return (
            <Row className="g-3 mb-3">
                <Col md={4}>
                    <Card style={metricCardStyle}>
                        <Card.Body>
                            <Card.Title as="h6" style={{color: theme.mutedTextColor}}>Total Value</Card.Title>
                            <h4 style={{color: theme.lightPurpleAccent}}>${portfolio_summary_metrics.total_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</h4>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={4}>
                     <Card style={metricCardStyle}>
                        <Card.Body>
                            <Card.Title as="h6" style={{color: theme.mutedTextColor}}>Daily Return</Card.Title>
                            {/* Define themed success/danger text colors directly or via CSS classes if preferred */}
                            <h4 style={{color: portfolio_summary_metrics.daily_return >= 0 ? '#4CAF50' : '#F44336'}}>
                                {portfolio_summary_metrics.daily_return.toFixed(2)}%
                            </h4>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={4}>
                     <Card style={metricCardStyle}>
                        <Card.Body>
                            <Card.Title as="h6" style={{color: theme.mutedTextColor}}>YTD Return</Card.Title>
                            <h4 style={{color: portfolio_summary_metrics.ytd_return >= 0 ? '#4CAF50' : '#F44336'}}>
                                {portfolio_summary_metrics.ytd_return.toFixed(2)}%
                            </h4>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        );
    };
    
    // Mock Quick Actions & Market Summary (as per original Dash app structure)
    const renderQuickActions = () => (
        <Card className="mb-4" style={themedCardStyle}>
            <Card.Header as="h5" style={themedCardHeaderStyle}>Quick Actions</Card.Header>
            <Card.Body>
                <Button style={{...themedButtonStyle, marginRight: '0.5rem', marginBottom: '0.5rem'}}>Rebalance Portfolio (Mock)</Button>
                <Button style={{...themedButtonStyle, backgroundColor: theme.sidebarBg, borderColor: theme.borderColor, marginBottom: '0.5rem'}}>Download Report (Mock)</Button>
            </Card.Body>
        </Card>
    );

    const renderMarketSummary = () => (
        <Card style={themedCardStyle}>
            <Card.Header as="h5" style={themedCardHeaderStyle}>Market Summary (Mock)</Card.Header>
            <Card.Body>
                {/* Define themed success/danger text colors */}
                <p>S&P 500: <span style={{color: '#4CAF50'}}>+0.5%</span></p>
                <p>NASDAQ: <span style={{color: '#4CAF50'}}>+0.7%</span></p>
                <p>Dow Jones: <span style={{color: '#F44336'}}>-0.1%</span></p>
            </Card.Body>
        </Card>
    );

    return (
        <Container fluid style={{ backgroundColor: theme.contentBg, color: theme.textColor, padding: '2rem', borderRadius: '8px' }}>
            <h1 style={{ color: theme.lightPurpleAccent, margin: '1.5rem 0' }}>Portfolio Dashboard</h1>
            
            {renderMetricsCards()}

            <Row className="mb-4">
                <Col lg={7} className="mb-3 mb-lg-0">
                    <Card className="h-100" style={themedCardStyle}>
                        <Card.Header as="h5" style={themedCardHeaderStyle}>Performance Over Time</Card.Header>
                        <Card.Body>
                            {renderPerformanceChart()}
                        </Card.Body>
                    </Card>
                </Col>
                <Col lg={5}>
                    <Card className="h-100" style={themedCardStyle}>
                        <Card.Header as="h5" style={themedCardHeaderStyle}>Asset Allocation</Card.Header>
                        <Card.Body>
                            {renderAllocationChart()}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
            
            <Card className="mb-4" style={themedCardStyle}>
                <Card.Header as="h5" style={themedCardHeaderStyle}>Detailed Holdings</Card.Header>
                <Card.Body>
                    {renderHoldingsTable()}
                </Card.Body>
            </Card>

            <Card className="mb-4" style={themedCardStyle}>
                <Card.Header as="h5" style={themedCardHeaderStyle}>AI-Powered Risk Analysis</Card.Header>
                 <Card.Body>
                    {renderRiskAnalysis()}
                </Card.Body>
            </Card>

            <Row>
                <Col md={6} className="mb-3 mb-md-0">
                    {renderQuickActions()}
                </Col>
                <Col md={6}>
                    {renderMarketSummary()}
                </Col>
            </Row>
        </Container>
    );
};

export default PortfolioDashboardPage; 