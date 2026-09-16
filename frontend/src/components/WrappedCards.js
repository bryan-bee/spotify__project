import { useRef, useState } from 'react';
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

  if (stats.top_genres && stats.top_genres.length > 0) {
    cards.push({
      key: 'genre',
      preview: previews.top_genre,
      content: (
        <>
          <p className="wc-eyebrow">Your top genres</p>
          <ol className="wc-list">
            {stats.top_genres.map((genre, i) => (
              <li key={genre.name} className={`wc-list-item${i === 0 ? ' wc-list-item--top' : ''}`}>
                <span className="wc-rank">{i === 0 ? '👑' : i + 1}</span>
                <span className="wc-list-label wc-list-label--capitalize">{genre.name}</span>
              </li>
            ))}
          </ol>
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
              <li key={artist.name} className={`wc-list-item${i === 0 ? ' wc-list-item--top' : ''}`}>
                <span className="wc-rank">{i === 0 ? '👑' : i + 1}</span>
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
              <li key={`${song.song_name}-${i}`} className={`wc-list-item${i === 0 ? ' wc-list-item--top' : ''}`}>
                <span className="wc-rank">{i === 0 ? '👑' : i + 1}</span>
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
  const shellRef = useRef(null);
  const cards = buildCards(stats, displayName);
  const card = cards[index];

  function goNext() {
    setIndex((i) => Math.min(i + 1, cards.length - 1));
  }

  function goPrev() {
    setIndex((i) => Math.max(i - 1, 0));
  }

  // Tapping the left/right half of the card advances/rewinds, Stories-style.
  // This lives on a real click handler (not a full-height overlay button)
  // specifically so it coexists with scrolling: a touch-drag scroll doesn't
  // fire a click event, but an overlay button sitting on top of the
  // scrollable area would intercept the drag before it ever reached the
  // scrollable element underneath it.
  function handleCardClick(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickedLeftHalf = e.clientX - rect.left < rect.width / 2;
    if (clickedLeftHalf) {
      goPrev();
    } else {
      goNext();
    }
  }

  return (
    <div className="wc-shell" ref={shellRef} style={{ background: GRADIENTS[index % GRADIENTS.length] }}>
      <div className="wc-progress">
        {cards.map((c, i) => (
          <span key={c.key} className={`wc-progress-seg ${i <= index ? 'is-filled' : ''}`} />
        ))}
      </div>

      <div className="wc-topbar">
        <BrandMark size="sm" />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={card.key}
          className="wc-card"
          onClick={handleCardClick}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -24 }}
          transition={{ duration: 0.35 }}
        >
          {card.content}
        </motion.div>
      </AnimatePresence>

      {card.preview && (
        // Spotify's own official embed player - not our audio. Since Nov
        // 2024, Spotify's Web API returns preview_url: null for apps without
        // Extended API Access (confirmed for this app), so a custom <audio>
        // player has nothing to play; this embed is a separate Spotify
        // product with no such restriction. autoplay=1 asks Spotify's
        // player to start immediately; browsers only honor unmuted iframe
        // autoplay when it's tied to a real user gesture, and this iframe
        // is freshly created (new `key`) as a direct result of the click
        // that changed cards, so it has a real shot at working - but it's
        // not guaranteed on every browser (Safari is stricter than Chrome
        // here), so a tap on Spotify's own play button is still the
        // fallback if a given browser blocks it. Excluded from the
        // "Save as Image"/"Share" export (ShareMenu.js) either way, since
        // cross-origin iframe content can't be captured to canvas.
        <div className="wc-embed">
          <iframe
            key={card.key}
            title={`${card.preview.track_name} preview`}
            src={`https://open.spotify.com/embed/track/${card.preview.track_id}?utm_source=generator&theme=0&autoplay=1`}
            width="100%"
            height="152"
            frameBorder="0"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy"
          />
        </div>
      )}

      {/* Every card except the intro (index 0) gets the footer - there's
          nothing to share yet on the title card itself. */}
      {index > 0 && shareEnabled && (
        <div className="wc-footer">
          <ShareMenu shellRef={shellRef} onCreateShareLink={onCreateShareLink} />
        </div>
      )}
      {index > 0 && !shareEnabled && footer && <div className="wc-footer">{footer}</div>}
    </div>
  );
}
