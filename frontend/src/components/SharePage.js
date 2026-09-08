import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import WrappedCards from './WrappedCards';
import BrandMark from './BrandMark';
import { fetchShare } from '../api';
import './SharePage.css';

export default function SharePage() {
  const { shareId } = useParams();
  const [stats, setStats] = useState(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    fetchShare(shareId)
      .then(setStats)
      .catch(() => setNotFound(true));
  }, [shareId]);

  if (notFound) {
    return (
      <div className="share-page share-page--empty">
        <BrandMark size="md" />
        <p>This Wrapped link doesn't exist (or expired).</p>
        <a className="share-page__cta" href="/">Make your own</a>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="share-page">
      <WrappedCards
        stats={stats}
        displayName={stats.display_name}
        footer={
          <a className="share-page__cta" href="/">
            Make your own BeeSpotifyWrapped
          </a>
        }
      />
    </div>
  );
}
