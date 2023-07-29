import React, { useEffect, useState } from 'react';
import axios from 'axios';
import UserInfoPage from './UserInfoPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [isLoadingUserInfo, setIsLoadingUserInfo] = useState(false);

  useEffect(() => {
    // Check authentication status when the app loads
    checkAuthenticationStatus();
  }, []);

  const checkAuthenticationStatus = async () => {
    try {
      // Send API request to check if the user is authenticated
      const response = await axios.get('/api/check-authentication');
      setIsLoggedIn(response.data.authenticated);

      if (response.data.authenticated) {
        // If the user is authenticated, fetch user info
        fetchUserInfo();
      }
    } catch (error) {
      console.error('Error checking authentication status:', error);
    }
  };

  const handleLogin = async () => {
    try {
      // Make a request to your Flask backend's login route
      const response = await axios.get('/api/login'); // Add a leading slash before 'api/login'
      const loginUrl = response.data.login_url;
       // Redirect the user to the Spotify login page
       window.location.href = loginUrl;
  
      // The browser will automatically follow the redirect to the Spotify login page
      // After the user logs in and grants permission, Spotify will redirect the user
      // back to your Flask backend's callback URL, where you'll handle the access token retrieval
  
    } catch (error) {
      console.error('Error while logging in:', error);
    }
  };

  const fetchUserInfo = async () => {
    try {
      // Set isLoadingUserInfo to true while fetching user info
      setIsLoadingUserInfo(true);

      // Send API request to get user info
      const response = await axios.get('/api/user-info');

      // Update the state with user info data
      setUserInfo(response.data);

      // Set isLoadingUserInfo back to false after successfully fetching user info
      setIsLoadingUserInfo(false);
    } catch (error) {
      console.error('Error fetching user info:', error);
      // Set isLoadingUserInfo back to false if there is an error
      setIsLoadingUserInfo(false);
    }
  };

  return (
    <div className="App">
      {isLoggedIn ? (
        userInfo ? (
          // User is already authenticated and user info is available
          <UserInfoPage userInfo={userInfo} />
        ) : isLoadingUserInfo ? (
          // User is authenticated, but user info is still loading
          <h1>Loading user info...</h1>
        ) : (
          // User is authenticated, but there was an error fetching user info
          <h1>Error fetching user info.</h1>
        )
      ) : (
        // User is not authenticated, show the login page
        <div>
          <h1>Login to Spotify</h1>
          <button onClick={handleLogin}>Login with Spotify</button>
        </div>
      )}
    </div>
  );
}

export default App;
