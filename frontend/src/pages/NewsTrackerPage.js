import React, { useState, useEffect, useContext } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';
import Badge from 'react-bootstrap/Badge'; // For sentiment display
import { getMarketNews, getMarketNewsSentiment } from '../services/api';
import { AppContext } from '../AppContext'; // Import AppContext

const NewsTrackerPage = () => {
    const { theme } = useContext(AppContext); // Consume theme from context

    const [newsArticles, setNewsArticles] = useState([]);
    const [marketSentiment, setMarketSentiment] = useState(null);
    const [isLoadingNews, setIsLoadingNews] = useState(true);
    const [isLoadingSentiment, setIsLoadingSentiment] = useState(true);
    const [errorNews, setErrorNews] = useState(null);
    const [errorSentiment, setErrorSentiment] = useState(null);

    useEffect(() => {
        // Fetch Market News
        setIsLoadingNews(true);
        getMarketNews(10)
            .then(response => {
                setNewsArticles(response.data.articles || []);
            })
            .catch(err => {
                console.error("Error fetching market news:", err);
                setErrorNews(err.response?.data?.detail || "Could not load market news.");
            })
            .finally(() => {
                setIsLoadingNews(false);
            });

        // Fetch Market Sentiment
        setIsLoadingSentiment(true);
        getMarketNewsSentiment()
            .then(response => {
                setMarketSentiment(response.data);
            })
            .catch(err => {
                console.error("Error fetching market sentiment:", err);
                setErrorSentiment(err.response?.data?.detail || "Could not load market sentiment.");
            })
            .finally(() => {
                setIsLoadingSentiment(false);
            });
    }, []);

    // Helper style objects based on theme
    const themedCardStyle = {
        backgroundColor: theme.cardBg,
        color: theme.textColor,
        border: `1px solid ${theme.cardBorder}`,
        marginBottom: '1.5rem'
    };

    const themedListGroupItemStyle = {
        backgroundColor: theme.cardBg, // Or theme.inputBg for slight variation
        color: theme.textColor,
        border: `1px solid ${theme.borderColor}`,
        marginBottom: '0.5rem',
        borderRadius: '0.25rem'
    };

    const themedAlertStyle = (variant) => {
        let style = { 
            backgroundColor: theme.cardBg, 
            color: theme.textColor, 
            borderColor: theme.borderColor, 
            border: `1px solid ${theme.borderColor}`
        };
        if (variant === "danger" || variant === "warning") {
            style.backgroundColor = '#58181F';
            style.color = '#F8D7DA';
            style.borderColor = '#C93A4C';
        } else if (variant === "success") {
            style.backgroundColor = '#1A4A3C';
            style.color = '#D1E7DD';
            style.borderColor = '#3C8C7A';
        } // Add other variants if needed
        return style;
    };

    const renderMarketSentiment = () => {
        if (isLoadingSentiment) return <div className="text-center p-3" style={{color: theme.textColor}}><Spinner animation="border" style={{color: theme.lightPurpleAccent}} /><p className="mt-2">Loading sentiment...</p></div>;
        if (errorSentiment) return <Alert variant="warning" style={themedAlertStyle('warning')}>Error loading sentiment: {errorSentiment}</Alert>;
        if (!marketSentiment) return <p style={{color: theme.mutedTextColor}}>Market sentiment data is currently unavailable.</p>;

        const sentimentValue = marketSentiment.overall_sentiment?.toLowerCase();
        let sentimentStyle = {
            fontSize: "1rem", 
            padding: "0.5rem 1rem",
            backgroundColor: theme.mutedTextColor, // Default for neutral/unknown
            color: theme.darkBg 
        };

        if (sentimentValue === "bullish") {
            sentimentStyle.backgroundColor = theme.mediumPurpleAccent; // Or a green color from theme if defined
            sentimentStyle.color = theme.activeLinkText;
        } else if (sentimentValue === "bearish") {
            sentimentStyle.backgroundColor = '#C93A4C'; // Darker red
            sentimentStyle.color = '#F8D7DA';
        }

        return (
            <Card style={themedCardStyle}>
                <Card.Header as="h5" style={{backgroundColor: theme.sidebarBg, color: theme.lightPurpleAccent, borderBottom: `1px solid ${theme.borderColor}`}}>Market Sentiment Analysis</Card.Header>
                <Card.Body>
                    <div className="mb-2">
                        <h6 style={{color: theme.lightPurpleAccent}}>Overall Market Sentiment</h6>
                        <Badge style={sentimentStyle}>
                            {(marketSentiment.overall_sentiment || "NEUTRAL").toUpperCase()}
                        </Badge>
                        {marketSentiment.confidence > 0 && <p className="mt-1 mb-0" style={{color: theme.mutedTextColor}}>Confidence: {(marketSentiment.confidence * 100).toFixed(0)}%</p>}
                    </div>
                    <h6 className="mt-3" style={{color: theme.lightPurpleAccent}}>Key Market Factors</h6>
                    {marketSentiment.key_factors && marketSentiment.key_factors.length > 0 ?
                        <ListGroup variant="flush">{marketSentiment.key_factors.map((item, i) => <ListGroup.Item style={{...themedListGroupItemStyle, backgroundColor: 'transparent', borderBottom: `1px solid ${theme.borderColor}`}} key={`factor-${i}`}>{item}</ListGroup.Item>)}</ListGroup> : <p style={{color: theme.mutedTextColor}}>No specific factors identified.</p>}
                    <h6 className="mt-3" style={{color: theme.lightPurpleAccent}}>Market Outlook</h6>
                    <p>{marketSentiment.market_outlook || "Not available."}</p>
                </Card.Body>
            </Card>
        );
    }

    const renderNewsArticles = () => {
        if (isLoadingNews) return <div className="text-center p-3" style={{color: theme.textColor}}><Spinner animation="border" style={{color: theme.lightPurpleAccent}} /><p className="mt-2">Loading news...</p></div>;
        if (errorNews) return <Alert variant="danger" style={themedAlertStyle('danger')}>{errorNews}</Alert>;
        if (!newsArticles || newsArticles.length === 0) return <p style={{color: theme.mutedTextColor}}>No news articles found.</p>;

        return (
            <ListGroup>
                {newsArticles.map((article, index) => (
                    <ListGroup.Item 
                        key={index} 
                        action 
                        href={article.url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={themedListGroupItemStyle}
                        // Add hover effect for better UX
                        onMouseEnter={(e) => { 
                            e.currentTarget.style.backgroundColor = theme.mediumPurpleAccent;
                            e.currentTarget.style.borderColor = theme.mediumPurpleAccent;
                            e.currentTarget.style.color = theme.activeLinkText;
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = themedListGroupItemStyle.backgroundColor;
                            e.currentTarget.style.borderColor = themedListGroupItemStyle.border.split(' ')[2]; // Extract color
                            e.currentTarget.style.color = themedListGroupItemStyle.color;
                        }}
                    >
                        <div className="d-flex w-100 justify-content-between">
                            <h5 className="mb-1" style={{color: 'inherit'}}>{article.title}</h5>
                        </div>
                        <p className="mb-1" style={{color: 'inherit'}}><em>Source: {article.source.name}</em></p>
                        {article.description && <p className="mb-1" style={{color: theme.mutedTextColor}}>{article.description}</p>}
                    </ListGroup.Item>
                ))}
            </ListGroup>
        );
    }

    return (
        <Container fluid style={{ backgroundColor: theme.contentBg, color: theme.textColor, padding: '2rem', borderRadius: '8px' }}>
            <Row className="mb-4">
                <Col>
                    <h1 style={{ color: theme.lightPurpleAccent }}>Financial News Tracker</h1>
                </Col>
            </Row>
            <Row>
                <Col md={8}>
                    <h2 className="h4 mb-3" style={{ color: theme.lightPurpleAccent }}>Today's Market News</h2>
                    {renderNewsArticles()}
                </Col>
                <Col md={4}>
                    <h2 className="h4 mb-3" style={{ color: theme.lightPurpleAccent }}>AI-Powered Sentiment</h2>
                    {renderMarketSentiment()}
                </Col>
            </Row>
        </Container>
    );
};

export default NewsTrackerPage; 