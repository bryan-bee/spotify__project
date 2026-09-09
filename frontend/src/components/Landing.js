import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import BrandMark from './BrandMark';
import { fetchMe, LOGIN_URL } from '../api';
import './Landing.css';

const ERROR_MESSAGES = {
  state_mismatch: 'Login could not be verified, please try again.',
  token_exchange_failed: 'Spotify could not confirm your login, please try again.',
  access_denied: 'Login was cancelled.',
};

export default function Landing() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [checkingSession, setCheckingSession] = useState(true);
  const loginError = searchParams.get('login_error');

  useEffect(() => {
    // If the browser already has a valid (or refreshable) session, skip
    // the login screen entirely - this is the "don't log in every time" part.
    fetchMe()
      .then(() => navigate('/dashboard', { replace: true }))
      .catch(() => setCheckingSession(false));
  }, [navigate]);

  if (checkingSession) {
    return <div className="landing landing--loading" />;
  }

  return (
    <div className="landing">
      <BrandMark size="lg" />
      <p className="landing__tagline">
        Your Spotify stats, wrapped up — for whatever timeframe you want.
      </p>
      {loginError && (
        <p className="landing__error">
          {ERROR_MESSAGES[loginError] || 'Something went wrong logging in, please try again.'}
        </p>
      )}
      <a className="landing__cta" href={LOGIN_URL}>
        Log in with Spotify
      </a>
    </div>
  );
}
