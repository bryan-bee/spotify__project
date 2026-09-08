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
  const [timeRange, setTimeRange] = useState('medium_term');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [shareUrl, setShareUrl] = useState(null);
  const [sharing, setSharing] = useState(false);

  useEffect(() => {
    fetchMe()
      .then(setMe)
      .catch(() => navigate('/', { replace: true }));
  }, [navigate]);

  useEffect(() => {
    if (!me) return;
    setLoading(true);
    setError(null);
    setShareUrl(null);
    fetchTopStuff(timeRange)
      .then(setStats)
      .catch(() => setError('Could not load your stats from Spotify. Try again in a bit.'))
      .finally(() => setLoading(false));
  }, [me, timeRange]);

  async function handleShare() {
    setSharing(true);
    try {
      const { share_id } = await createShare(timeRange);
      setShareUrl(`${window.location.origin}/share/${share_id}`);
    } catch {
      setError('Could not create a share link. Try again in a bit.');
    } finally {
      setSharing(false);
    }
  }

  async function handleLogout() {
    await logout();
    navigate('/', { replace: true });
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
          footer={
            shareUrl ? (
              <div className="dashboard__share-result">
                <input readOnly value={shareUrl} onFocus={(e) => e.target.select()} />
                <button onClick={() => navigator.clipboard.writeText(shareUrl)}>Copy</button>
              </div>
            ) : (
              <button className="dashboard__share-btn" onClick={handleShare} disabled={sharing}>
                {sharing ? 'Creating link…' : 'Share this Wrapped'}
              </button>
            )
          }
        />
      )}
    </div>
  );
}
