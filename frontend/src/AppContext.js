import React, { createContext, useState, useEffect } from 'react';
import { getInitialWelcomeData } from './services/api'; // To get base_pages

export const AppContext = createContext();

// Define theme colors
const theme = {
  darkBg: '#1a1a2e', // Dark navy/purple
  lightPurpleAccent: '#9370db', // Light-medium purple
  mediumPurpleAccent: '#7b68ee', // Medium purple
  textColor: '#e0e0e0', // Light gray for text
  mutedTextColor: '#a0a0a0', // Muted gray
  sidebarBg: '#161625', // Slightly lighter dark for sidebar
  activeLinkBg: '#7b68ee', // Medium purple for active link background
  activeLinkText: '#ffffff', // White for active link text
  borderColor: '#30304a', // Darker purple for borders/dividers
  contentBg: '#1c1c2f', // Slightly different dark for page content areas
  cardBg: '#25253a',    // Background for cards or distinct sections
  cardBorder: '#30304a', // Border for cards
  inputBg: '#25253a',
  inputBorder: '#30304a',
  inputText: '#e0e0e0',
};

export const AppProvider = ({ children }) => {
    const [userData, setUserData] = useState(null);
    const [availablePages, setAvailablePages] = useState([]);
    const [activePage, setActivePage] = useState('Welcome'); // Default active page

    // Fetch initial base pages for navigation
    useEffect(() => {
        getInitialWelcomeData()
            .then(response => {
                setAvailablePages(response.data.base_pages || []);
                setUserData(response.data.user_data || { user_id: '', investment_goals: '', custom_portfolio: {} });
            })
            .catch(err => {
                console.error("Error fetching initial page data for context:", err);
                // Set some defaults if API fails
                setAvailablePages(["Welcome", "Portfolio Dashboard", "News Tracker", "Live Trades"]);
                setUserData({ user_id: '', investment_goals: '', custom_portfolio: {} });
            });
    }, []);

    return (
        <AppContext.Provider value={{
            userData, 
            setUserData, 
            availablePages, 
            setAvailablePages,
            activePage,
            setActivePage,
            theme // Add theme to context
        }}>
            {children}
        </AppContext.Provider>
    );
}; 