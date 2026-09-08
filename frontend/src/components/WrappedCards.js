import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import BrandMark from './BrandMark';
import './WrappedCards.css';

const GRADIENTS = [
  'linear-gradient(160deg, #1db954, #0b0b0c)',
  'linear-gradient(160deg, #ffd23f, #ff6b6b)',
  'linear-gradient(160deg, #6a3093, #1db954)',
  'linear-gradient(160deg, #ff6b6b, #0b0b0c)',
  'linear-gradient(160deg, #1db954, #ffd23f)',
];

function buildCards(stats, displayName) {
  const cards = [
    {
      key: 'intro',
      content: (
        <>
          <p className="wc-eyebrow">{stats.time_range_label}</p>
          <h1 className="wc-headline">{displayName ? `${displayName}'s` : 'Your'} Wrapped</h1>
          <p className="wc-sub">Let's see what you've been into.</p>
        </>
      ),
    },
  ];

  if (stats.best_genre) {
    cards.push({
      key: 'genre',
      content: (
        <>
          <p className="wc-eyebrow">Your top genre</p>
          <h1 className="wc-headline wc-headline--big">{stats.best_genre}</h1>
        </>
      ),
    });
  }

  if (stats.favorite_artists && stats.favorite_artists.length > 0) {
    cards.push({
      key: 'artists',
      content: (
        <>
          <p className="wc-eyebrow">Top Artists</p>
          <ol className="wc-list">
            {stats.favorite_artists.map((artist, i) => (
              <li key={artist.name} className="wc-list-item">
                <span className="wc-rank">{i + 1}</span>
                {artist.url && <img className="wc-thumb" src={artist.url} alt="" />}
                <span className="wc-list-label">{artist.name}</span>
              </li>
            ))}
          </ol>
        </>
      ),
    });
  }

  if (stats.favorite_songs && stats.favorite_songs.length > 0) {
    cards.push({
      key: 'songs',
      content: (
        <>
          <p className="wc-eyebrow">Top Songs</p>
          <ol className="wc-list">
            {stats.favorite_songs.map((song, i) => (
              <li key={`${song.song_name}-${i}`} className="wc-list-item">
                <span className="wc-rank">{i + 1}</span>
                <span className="wc-list-label">
                  {song.song_name}
                  <span className="wc-list-sub">{song.artists}</span>
                </span>
              </li>
            ))}
          </ol>
        </>
      ),
    });
  }

  return cards;
}

export default function WrappedCards({ stats, displayName, footer }) {
  const [index, setIndex] = useState(0);
  const cards = buildCards(stats, displayName);
  const card = cards[index];

  const goNext = () => setIndex((i) => Math.min(i + 1, cards.length - 1));
  const goPrev = () => setIndex((i) => Math.max(i - 1, 0));

  return (
    <div className="wc-shell" style={{ background: GRADIENTS[index % GRADIENTS.length] }}>
      <div className="wc-progress">
        {cards.map((c, i) => (
          <span key={c.key} className={`wc-progress-seg ${i <= index ? 'is-filled' : ''}`} />
        ))}
      </div>

      <div className="wc-topbar">
        <BrandMark size="sm" />
      </div>

      <button className="wc-tap wc-tap--left" aria-label="Previous card" onClick={goPrev} disabled={index === 0} />
      <button className="wc-tap wc-tap--right" aria-label="Next card" onClick={goNext} disabled={index === cards.length - 1} />

      <AnimatePresence mode="wait">
        <motion.div
          key={card.key}
          className="wc-card"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -24 }}
          transition={{ duration: 0.35 }}
        >
          {card.content}
        </motion.div>
      </AnimatePresence>

      {index === cards.length - 1 && footer && <div className="wc-footer">{footer}</div>}
    </div>
  );
}
