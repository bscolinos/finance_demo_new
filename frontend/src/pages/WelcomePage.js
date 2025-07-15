import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import ListGroup from 'react-bootstrap/ListGroup';
import Alert from 'react-bootstrap/Alert';
import Spinner from 'react-bootstrap/Spinner'; // For loading state

import { getInitialWelcomeData, submitFinancialPlan } from '../services/api';
// We'll need a global context to update App.js with pages and user data
// Let's assume an AppContext is created later. For now, we might pass functions or manage locally.
import { AppContext } from '../AppContext'; // Create this file: frontend/src/AppContext.js

const WelcomePage = () => {
    const navigate = useNavigate();
    const { userData, setUserData, availablePages, setAvailablePages, theme } = useContext(AppContext); // Get data and setters from context

    const [userName, setUserName] = useState('');
    const [currentSavings, setCurrentSavings] = useState('');
    const [annualIncome, setAnnualIncome] = useState('');
    const [investmentGoals, setInvestmentGoals] = useState('');
    
    const [portfolioResult, setPortfolioResult] = useState(null);
    const [portfolioAnalysis, setPortfolioAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);

    // Load initial data from context if available, or fetch from API
    useEffect(() => {
        // Check if userData exists in context first
        if (userData && Object.keys(userData).length > 0) {
            // Use data from context
            setUserName(userData.user_id || userData.user_name || '');
            setCurrentSavings(userData.amount !== null ? String(userData.amount) : '');
            setAnnualIncome(userData.income !== null ? String(userData.income) : '');
            setInvestmentGoals(userData.investment_goals || '');
            
            // If portfolio data exists in context
            if (userData.portfolio_result) {
                setPortfolioResult(userData.portfolio_result);
            }
            
            if (userData.portfolio_analysis) {
                setPortfolioAnalysis(userData.portfolio_analysis);
            }
            
            // Display success message if portfolio exists
            if (userData.portfolio_result && userData.portfolio_result.optimized_holdings) {
                setMessage("Your personalized portfolio has been created successfully!");
            }
        } else {
            // Fetch from API if not in context
            getInitialWelcomeData()
                .then(response => {
                    const initialData = response.data.user_data;
                    setUserName(initialData.user_id || '');
                    setCurrentSavings(initialData.amount !== null ? String(initialData.amount) : '');
                    setAnnualIncome(initialData.income !== null ? String(initialData.income) : '');
                    setInvestmentGoals(initialData.investment_goals || '');
                    setAvailablePages(response.data.base_pages || []); // Initialize pages in AppContext
                    setUserData(initialData); // Initialize user data in AppContext
                })
                .catch(err => {
                    console.error("Error fetching initial data:", err);
                    setError("Could not load initial page data. Please refresh.");
                });
        }
    }, [userData, setAvailablePages, setUserData]); // Add context as dependencies

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setError(null);
        setMessage(null);
        setPortfolioResult(null);
        setPortfolioAnalysis(null);

        const planData = {
            user_name: userName,
            current_savings: currentSavings ? parseFloat(currentSavings) : 0,
            annual_income: annualIncome ? parseFloat(annualIncome) : 0,
            investment_goals: investmentGoals,
        };

        try {
            const response = await submitFinancialPlan(planData);
            const result = response.data;

            if (result.error) {
                setError(result.error);
            } else {
                setMessage(result.message);
                setPortfolioResult(result.optimized_portfolio);
                setPortfolioAnalysis(result.portfolio_analysis);
                
                // Store everything in context including portfolio results
                const updatedUserData = {
                    ...result.user_data,
                    portfolio_result: result.optimized_portfolio,
                    portfolio_analysis: result.portfolio_analysis
                };
                
                setUserData(updatedUserData);
                if (setAvailablePages && result.pages) setAvailablePages(result.pages);
            }
        } catch (err) {
            console.error("Error submitting financial plan:", err);
            setError(err.response?.data?.detail || "An unexpected error occurred. Please try again.");
        }
        setIsLoading(false);
    };

    const themedCardStyle = {
        backgroundColor: theme.cardBg,
        color: theme.textColor,
        border: `1px solid ${theme.cardBorder}`,
        marginBottom: '1.5rem'
    };

    const themedListGroupItemStyle = {
        backgroundColor: theme.cardBg, // Or a slightly different shade like theme.inputBg
        color: theme.textColor,
        border: `1px solid ${theme.borderColor}`,
    };
    
    const themedFormCtrlStyle = {
        backgroundColor: theme.inputBg,
        color: theme.inputText,
        borderColor: theme.inputBorder,
    };

    const themedFormLabelStyle = {
        color: theme.textColor, // Ensure labels are visible
    };

    const themedAlertStyle = (variant) => {
        let backgroundColor = theme.cardBg;
        let textColor = theme.textColor;
        let borderColor = theme.borderColor;

        if (variant === "danger") {
            backgroundColor = '#58181F'; // Dark red
            textColor = '#F8D7DA';
            borderColor = '#C93A4C';
        } else if (variant === "success") {
            backgroundColor = '#1A4A3C'; // Dark green
            textColor = '#D1E7DD';
            borderColor = '#3C8C7A';
        } else if (variant === "info") {
            backgroundColor = '#1E4A5F'; // Dark blue/info
            textColor = '#CFF4FC';
            borderColor = '#4285F4'; 
        }
        // Add other variants if needed

        return { backgroundColor, color: textColor, borderColor, border: `1px solid ${borderColor}` };
    };

    const renderPortfolioMessage = () => {
        if (error) {
            return <Alert variant="danger" style={themedAlertStyle('danger')}>{error}</Alert>;
        }
        if (message && !portfolioResult?.optimized_holdings?.length) {
             return <Alert variant="info" style={themedAlertStyle('info')}>{message}</Alert>;
        }
        return null;
    };

    return (
        <Container fluid style={{ backgroundColor: theme.contentBg, color: theme.textColor, padding: '2rem', borderRadius: '8px' }}>
            <Row className="mb-4">
                <Col>
                    <h1 style={{ color: theme.lightPurpleAccent }}>Welcome to AI Financial Advisor</h1>
                </Col>
            </Row>
            <Row>
                <Col md={8}>
                    <Card className="mb-4" style={themedCardStyle}>
                        <Card.Header as="h5" style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderBottom: `1px solid ${theme.borderColor}`}}>Get Started</Card.Header>
                        <Card.Body>
                            <Form onSubmit={handleSubmit}>
                                <Form.Group as={Row} className="mb-3" controlId="userName">
                                    <Form.Label column sm={12} style={themedFormLabelStyle}>Enter your name:</Form.Label>
                                    <Col sm={12}>
                                        <Form.Control 
                                            type="text" 
                                            placeholder="Your name" 
                                            value={userName} 
                                            onChange={(e) => setUserName(e.target.value)} 
                                            required
                                            disabled={isLoading}
                                            style={themedFormCtrlStyle}
                                        />
                                    </Col>
                                </Form.Group>

                                <Form.Group as={Row} className="mb-3" controlId="currentSavings">
                                    <Form.Label column sm={12} style={themedFormLabelStyle}>Current Savings ($):</Form.Label>
                                    <Col sm={12}>
                                        <Form.Control 
                                            type="number" 
                                            placeholder="Amount in $" 
                                            value={currentSavings} 
                                            onChange={(e) => setCurrentSavings(e.target.value)} 
                                            disabled={isLoading}
                                            style={themedFormCtrlStyle}
                                        />
                                    </Col>
                                </Form.Group>

                                <Form.Group as={Row} className="mb-3" controlId="annualIncome">
                                    <Form.Label column sm={12} style={themedFormLabelStyle}>Annual Income ($):</Form.Label>
                                    <Col sm={12}>
                                        <Form.Control 
                                            type="number" 
                                            placeholder="Amount in $" 
                                            value={annualIncome} 
                                            onChange={(e) => setAnnualIncome(e.target.value)} 
                                            disabled={isLoading}
                                            style={themedFormCtrlStyle}
                                        />
                                    </Col>
                                </Form.Group>

                                <Form.Group as={Row} className="mb-3" controlId="investmentGoals">
                                    <Form.Label column sm={12} style={themedFormLabelStyle}>Enter your investment goals:</Form.Label>
                                    <Col sm={12}>
                                        <Form.Control 
                                            as="textarea" 
                                            rows={4} 
                                            placeholder="e.g., I want to save for retirement, college funds for kids, etc." 
                                            value={investmentGoals} 
                                            onChange={(e) => setInvestmentGoals(e.target.value)} 
                                            disabled={isLoading}
                                            style={themedFormCtrlStyle}
                                        />
                                    </Col>
                                </Form.Group>
                                
                                <Button variant="primary" type="submit" className="mt-3" disabled={isLoading} style={{backgroundColor: theme.mediumPurpleAccent, borderColor: theme.mediumPurpleAccent, color: theme.activeLinkText}}>
                                    {isLoading ? <><Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> Generating Plan...</> : "Create My Financial Plan"}
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                    <Card style={themedCardStyle}>
                        {renderPortfolioMessage()}
                    </Card>

                    {/* Results Area: Error, Messages, Portfolio, and Insights */}
                    {error && <Alert variant="danger" className="mt-3" style={themedAlertStyle('danger')}>{error}</Alert>}
                    
                    {/* Display initial message OR specific message if no portfolio generated */}
                    {(!isLoading && !error && !portfolioResult && message) && <Alert variant="info" className="mt-3" style={themedAlertStyle('info')}>{message}</Alert>}

                    {/* Portfolio Results Card (modified from renderPortfolioMessage) */}
                    {portfolioResult && portfolioResult.optimized_holdings && portfolioResult.optimized_holdings.length > 0 && (
                         <Card className="mt-4" id="portfolio-results-card" style={themedCardStyle}>
                            <Card.Header as="h5" style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderBottom: `1px solid ${theme.borderColor}`}}>Your Personalized Investment Plan</Card.Header>
                            <Card.Body>
                                {message && !error && <Alert variant="success" className="mt-0 mb-3" style={themedAlertStyle('success')}>{message}</Alert>}
                                <p>Based on your goals, we've created an optimized portfolio that aligns with your objectives:</p>
                                <ListGroup className="mb-3">
                                    {portfolioResult.optimized_holdings.map((holding, index) => (
                                        <ListGroup.Item key={index} style={themedListGroupItemStyle}>
                                            <div className="d-flex justify-content-between">
                                                <span className="fw-bold">{holding.symbol}</span>
                                                <span className={`badge ms-2`} style={{backgroundColor: theme.mediumPurpleAccent, color: theme.activeLinkText}}>{`${(holding.target_allocation * 100).toFixed(1)}%`}</span>
                                            </div>
                                            <div>{`Quantity: ${holding.quantity}`}</div>
                                        </ListGroup.Item>
                                    ))}
                                </ListGroup>
                                <p style={{ color: theme.mutedTextColor }}>Your portfolio has been saved and is ready for detailed analysis!</p>
                                <Button 
                                    variant="success" // Keep variant for semantics, override styles
                                    className="mt-2"
                                    onClick={() => navigate('/portfolio-dashboard')} 
                                    style={{backgroundColor: theme.mediumPurpleAccent, borderColor: theme.mediumPurpleAccent, color: theme.activeLinkText}}
                                >
                                    View Portfolio Details
                                </Button>
                            </Card.Body>
                        </Card>
                    )}
                    
                </Col>
                <Col md={4}>
                    {/* Conditionally render Portfolio Analysis or default cards */}
                    {portfolioAnalysis && !isLoading ? (
                        <Card className="mb-4" style={themedCardStyle}>
                            <Card.Header as="h5" style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderBottom: `1px solid ${theme.borderColor}`}}>Portfolio Analysis</Card.Header>
                            <Card.Body>
                                <h6 style={{color: theme.lightPurpleAccent}}>Summary</h6>
                                <p>{portfolioAnalysis.summary || "Not available."}</p>
                                <h6 style={{color: theme.lightPurpleAccent}}>Risks</h6>
                                {portfolioAnalysis.risks && portfolioAnalysis.risks.length > 0 ? 
                                    <ul style={{paddingLeft: '20px'}}>{portfolioAnalysis.risks.map((item, i) => <li key={`risk-${i}`}>{item}</li>)}</ul> : <p>No specific risks identified.</p>}
                                <h6 style={{color: theme.lightPurpleAccent}}>Opportunities</h6>
                                {portfolioAnalysis.opportunities && portfolioAnalysis.opportunities.length > 0 ?
                                    <ul style={{paddingLeft: '20px'}}>{portfolioAnalysis.opportunities.map((item, i) => <li key={`opp-${i}`}>{item}</li>)}</ul> : <p>No specific opportunities identified.</p>}
                                <h6 style={{color: theme.lightPurpleAccent}}>Recommendations</h6>
                                {portfolioAnalysis.recommendations && portfolioAnalysis.recommendations.length > 0 ?
                                    <ul style={{paddingLeft: '20px'}}>{portfolioAnalysis.recommendations.map((item, i) => <li key={`rec-${i}`}>{item}</li>)}</ul> : <p>No specific recommendations available.</p>}
                            </Card.Body>
                        </Card>
                    ) : (
                        <>
                            <Card className="mb-4" style={themedCardStyle}>
                                <Card.Header as="h5" style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderBottom: `1px solid ${theme.borderColor}`}}>Why Choose an AI Financial Advisor?</Card.Header>
                                <Card.Body>
                                    <p>Our AI-powered platform offers personalized financial advice tailored to your goals, without the cost associated with human intervention.</p>
                                    <ul style={{paddingLeft: '20px'}}>
                                        <li>Personalized investment strategies</li>
                                        <li>Real-time market analysis</li>
                                        <li>AI-driven portfolio optimization</li>
                                        <li>Customized goal planning</li>
                                    </ul>
                                </Card.Body>
                            </Card>
                            <Card style={themedCardStyle}>
                                <Card.Header as="h5" style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderBottom: `1px solid ${theme.borderColor}`}}>Market Insights</Card.Header>
                                <Card.Body>
                                    <p>Today's Market Overview</p>
                                    <ListGroup>
                                        <ListGroup.Item style={themedListGroupItemStyle}>
                                            <div className="fw-bold">S&P 500</div>
                                            <div className="d-flex justify-content-between">
                                                <span style={{color: theme.textColor}}>4,587.64 </span>
                                                <span style={{color: theme.textColor}}>+0.57%</span>
                                            </div>
                                        </ListGroup.Item>
                                        <ListGroup.Item style={themedListGroupItemStyle}>
                                            <div className="fw-bold">NASDAQ</div>
                                            <div className="d-flex justify-content-between">
                                                <span style={{color: theme.textColor}}>14,346.02 </span>
                                                <span style={{color: theme.textColor}}>+0.75%</span>
                                            </div>
                                        </ListGroup.Item>
                                        <ListGroup.Item style={themedListGroupItemStyle}>
                                            <div className="fw-bold">10-YR Treasury</div>
                                            <div className="d-flex justify-content-between">
                                                <span style={{color: theme.textColor}}>1.67% </span>
                                                <span style={{color: theme.textColor}}>-0.02%</span>
                                            </div>
                                        </ListGroup.Item>
                                    </ListGroup>
                                </Card.Body>
                            </Card>
                        </>
                    )}
                </Col>
            </Row>
        </Container>
    );
};

export default WelcomePage; 