import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import WrappedCards from './WrappedCards';
import { fetchMe, fetchTopStuff, createShare, logout } from '../api';
import './Dashboard.css';

const TIME_RANGES = [
  { value: 'short_term', label: 'Last 4 Weeks' },
  { value: 'medium_term', label: 'Last 6 Months' },
  { value: 'long_term', label: 'All Time' },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [me, setMe] = useState(null);
  const [meError, setMeError] = useState(null);
  const [timeRange, setTimeRange] = useState('medium_term');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMe()
      .then(setMe)
      .catch((err) => {
        if (err.status === 401) {
          // Genuinely not logged in (or the session expired) - back to the login screen.
          navigate('/', { replace: true });
        } else {
          // Login/token exchange succeeded, but Spotify rejected the actual API
          // call - most commonly because this app is still in Spotify's
          // restricted "Development Mode" and this account isn't on the
          // allowlist. Show that instead of silently bouncing back to login
          // with no explanation (which is what happened before this fix, and
          // looked identical to "not logged in" from the outside).
          setMeError(
            "Spotify blocked this request. If you're not the site owner, this app may still be in restricted developer mode - ask the owner to add your Spotify account."
          );
        }
      });
  }, [navigate]);

  useEffect(() => {
    if (!me) return;
    setLoading(true);
    setError(null);
    fetchTopStuff(timeRange)
      .then(setStats)
      .catch(() => setError('Could not load your stats from Spotify. Try again in a bit.'))
      .finally(() => setLoading(false));
  }, [me, timeRange]);

  // Passed down to ShareMenu (via WrappedCards) - it only gets called if the
  // user picks "Copy Link", so a share snapshot is only ever created on demand.
  async function handleCreateShareLink() {
    const { share_id } = await createShare(timeRange);
    return `${window.location.origin}/share/${share_id}`;
  }

  async function handleLogout() {
    await logout();
    navigate('/', { replace: true });
  }

  if (meError) {
    return (
      <div className="dashboard">
        <p className="dashboard__status dashboard__status--error">{meError}</p>
      </div>
    );
  }

  if (!me) return null;

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <span>Hey, {me.display_name}</span>
        <button className="dashboard__logout" onClick={handleLogout}>
          Log out
        </button>
      </header>

      <div className="dashboard__timeframes">
        {TIME_RANGES.map((tr) => (
          <button
            key={tr.value}
            className={`dashboard__timeframe ${tr.value === timeRange ? 'is-active' : ''}`}
            onClick={() => setTimeRange(tr.value)}
          >
            {tr.label}
          </button>
        ))}
      </div>

      {loading && <p className="dashboard__status">Loading your wrapped…</p>}
      {error && <p className="dashboard__status dashboard__status--error">{error}</p>}

      {!loading && !error && stats && (
        <WrappedCards
          stats={stats}
          displayName={me.display_name}
          shareEnabled
          onCreateShareLink={handleCreateShareLink}
        />
      )}
    </div>
  );
}
