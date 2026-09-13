import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import BrandMark from './BrandMark';
import ShareMenu from './ShareMenu';
import './WrappedCards.css';

const GRADIENTS = [
  'linear-gradient(160deg, #1db954, #0b0b0c)',
  'linear-gradient(160deg, #ffd23f, #ff6b6b)',
  'linear-gradient(160deg, #6a3093, #1db954)',
  'linear-gradient(160deg, #ff6b6b, #0b0b0c)',
  'linear-gradient(160deg, #1db954, #ffd23f)',
];

function buildCards(stats, displayName) {
  const previews = stats.previews || {};
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
      preview: previews.top_genre,
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
      preview: previews.top_artist,
      content: (
        <>
          <p className="wc-eyebrow">Top Artists</p>
          <ol className="wc-list">
            {stats.favorite_artists.map((artist, i) => (
              <li key={artist.name} className="wc-list-item">
                <span className="wc-rank">{i + 1}</span>
                {artist.url && <img className="wc-thumb" src={artist.url} alt="" />}
                <span className="wc-list-label">
                  {artist.name}
                  {artist.estimated_top_percent != null && (
                    <span className="wc-list-sub">
                      Est. top {artist.estimated_top_percent.toFixed(2)}% listener
                    </span>
                  )}
                </span>
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
      preview: previews.top_song,
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

export default function WrappedCards({ stats, displayName, footer, shareEnabled, onCreateShareLink }) {
  const [index, setIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  // Persists across card navigation, unlike pausing - muting here means "don't
  // autoplay the next clip either," not just "stop the current one."
  const [muted, setMuted] = useState(false);
  const audioRef = useRef(null);
  const shellRef = useRef(null);
  const cards = buildCards(stats, displayName);
  const card = cards[index];

  useEffect(() => {
    const audio = audioRef.current;
    return () => audio && audio.pause();
  }, []);

  function playCardAudio(targetCard) {
    const audio = audioRef.current;
    if (!audio) return;
    audio.pause();
    if (targetCard.preview) {
      audio.src = targetCard.preview.preview_url;
      audio.currentTime = 0;
      if (!muted) {
        // Autoplay is allowed here because this only ever runs inside a click
        // handler (goNext/goPrev) - i.e. as a direct result of a user gesture.
        audio.play().catch(() => {});
      }
    } else {
      audio.removeAttribute('src');
    }
  }

  function goNext() {
    if (index >= cards.length - 1) return;
    const next = index + 1;
    playCardAudio(cards[next]);
    setIndex(next);
  }

  function goPrev() {
    if (index <= 0) return;
    const prev = index - 1;
    playCardAudio(cards[prev]);
    setIndex(prev);
  }

  function toggleMute() {
    const next = !muted;
    const audio = audioRef.current;
    if (audio) {
      if (next) {
        audio.pause();
      } else if (card.preview) {
        if (audio.src !== card.preview.preview_url) {
          audio.src = card.preview.preview_url;
          audio.currentTime = 0;
        }
        audio.play().catch(() => {});
      }
    }
    setMuted(next);
  }

  return (
    <div className="wc-shell" ref={shellRef} style={{ background: GRADIENTS[index % GRADIENTS.length] }}>
      <audio
        ref={audioRef}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
      />

      <div className="wc-progress">
        {cards.map((c, i) => (
          <span key={c.key} className={`wc-progress-seg ${i <= index ? 'is-filled' : ''}`} />
        ))}
      </div>

      <div className="wc-topbar">
        <BrandMark size="sm" />
      </div>

      <button
        className="wc-mute-toggle"
        aria-label={muted ? 'Unmute preview clips' : 'Mute preview clips'}
        onClick={toggleMute}
      >
        {muted ? '🔇' : '🔊'}
      </button>

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

      {card.preview && (
        <button className="wc-now-playing" onClick={toggleMute}>
          <span className="wc-now-playing__icon">{muted ? '🔇' : isPlaying ? '⏸' : '▶'}</span>
          <span className="wc-now-playing__text">
            {card.preview.track_name} — {card.preview.artist_name}
          </span>
        </button>
      )}

      {index === cards.length - 1 && shareEnabled && (
        <div className="wc-footer">
          <ShareMenu shellRef={shellRef} onCreateShareLink={onCreateShareLink} />
        </div>
      )}
      {index === cards.length - 1 && !shareEnabled && footer && <div className="wc-footer">{footer}</div>}
    </div>
  );
}
