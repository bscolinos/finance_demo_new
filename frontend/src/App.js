import React, { useContext } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, NavLink } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import './App.css';
import { AppContext } from './AppContext';

// Import actual page components
import WelcomePage from './pages/WelcomePage';
import NewsTrackerPage from './pages/NewsTrackerPage';
import PortfolioDashboardPage from './pages/PortfolioDashboardPage';
import LiveTradesPage from './pages/LiveTradesPage';

// Placeholder components for other pages - these will be developed later

// Dynamically created pages (placeholders for now)
const GenericPage = ({ pageName }) => {
  const { theme } = useContext(AppContext);
  return <Container style={{ backgroundColor: theme.contentBg, color: theme.textColor, padding: '2rem', borderRadius: '8px' }}><h2>{pageName}</h2><p>Content for {pageName} coming soon...</p></Container>; 
}

function App() {
  const { availablePages, activePage, setActivePage, userData, theme } = useContext(AppContext);

  const pageToComponent = {
    "Welcome": WelcomePage,
    "Portfolio Dashboard": PortfolioDashboardPage,
    "News Tracker": NewsTrackerPage,
    "Live Trades": LiveTradesPage,
    // Add mappings for dynamically added pages if they have specific components
    // Otherwise, a generic component can be used.
  };

  const getPageComponent = (pageName) => {
    return pageToComponent[pageName] || (() => <GenericPage pageName={pageName} />); 
  };
  
  const handleNavClick = (pageName) => {
    setActivePage(pageName);
  };

  return (
    <Router>
      <div className="d-flex" style={{ backgroundColor: theme.darkBg, color: theme.textColor, minHeight: '100vh' }}>
        {/* Sidebar */}
        <div style={{
          width: '250px',
          minHeight: '100vh',
          backgroundColor: theme.sidebarBg,
          padding: '1rem',
          position: 'fixed',
          boxShadow: `1px 0 5px ${theme.borderColor}`,
          color: theme.textColor,
        }}>
          <h4 style={{ color: theme.lightPurpleAccent }} className="mb-3">Navigation</h4>
          {userData && userData.user_id && <p style={{color: theme.mutedTextColor}} className="small">User: {userData.user_id}</p>}
          <hr style={{ borderColor: theme.borderColor }}/>
          <Nav className="flex-column">
            {(availablePages && availablePages.length > 0) ? availablePages.map(page => {
              const path = `/${page.toLowerCase().replace(/ /g, '-')}`;
              const isActive = page === activePage;
              return (
                <Nav.Item key={page}>
                  <Nav.Link 
                    as={NavLink} 
                    to={path} 
                    onClick={() => handleNavClick(page)}
                    className={isActive ? 'fw-bold' : ''}
                    style={{
                      padding: '0.75rem 1rem', 
                      borderRadius: '0.3rem',
                      marginBottom: '0.25rem',
                      color: isActive ? theme.activeLinkText : theme.textColor,
                      backgroundColor: isActive ? theme.activeLinkBg : 'transparent',
                      transition: 'background-color 0.2s ease-in-out, color 0.2s ease-in-out',
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = theme.mediumPurpleAccent;
                        e.currentTarget.style.color = theme.activeLinkText;
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = theme.textColor;
                      }
                    }}
                  >
                    {/* Add icons later based on page name */}
                    {page}
                  </Nav.Link>
                </Nav.Item>
              );
            }) : <p style={{ color: theme.mutedTextColor }}>Loading navigation...</p>}
          </Nav>
        </div>

        {/* Main Content Area */}
        <div style={{ marginLeft: '250px', padding: '0rem', width: 'calc(100% - 250px)', backgroundColor: theme.darkBg, minHeight: '100vh' }}>
          {/* Top Navbar */}
          <Navbar style={{ backgroundColor: theme.mediumPurpleAccent, borderRadius: '0' }} variant="dark" className="mb-4">
            <Container fluid style={{paddingLeft: '2rem', paddingRight: '2rem'}}>
              <Navbar.Brand as={Link} to="/welcome" onClick={() => handleNavClick("Welcome")} style={{ color: theme.activeLinkText }}>
                {/* Add icon later: <FontAwesomeIcon icon={faChartLine} className="me-2" /> */}
                AI Financial Advisor
              </Navbar.Brand>
              <Nav className="ms-auto">
                {/* Could add user profile/logout here */}
              </Nav>
            </Container>
          </Navbar>

          {/* Page Content */}
          <div style={{padding: '0rem 2rem 2rem 2rem', color: theme.textColor}}>
            <Routes>
              {/* Default route to Welcome */}
              <Route path="/" element={React.createElement(getPageComponent("Welcome"))} /> 
              
              {(availablePages && availablePages.length > 0) && availablePages.map(page => {
                const path = `/${page.toLowerCase().replace(/ /g, '-')}`;
                const PageComponent = getPageComponent(page);
                return <Route key={page} path={path} element={<PageComponent />} />;
              })}
              {/* Fallback for any unknown routes */}
              { availablePages.length > 0 && <Route path="*" element={React.createElement(getPageComponent("Welcome"))} /> }
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App; 