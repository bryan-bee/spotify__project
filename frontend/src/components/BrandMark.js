import './BrandMark.css';

// Shown on the landing page, every wrapped card, and the public share page -
// the one piece of UI that always has to be there per the project brief.
export default function BrandMark({ size = 'md' }) {
  return (
    <div className={`brand-mark brand-mark--${size}`}>
      <span className="brand-mark__icon">🐝</span>
      <span className="brand-mark__text">
        Bee<span className="brand-mark__accent">Spotify</span>Wrapped
      </span>
    </div>
  );
}
