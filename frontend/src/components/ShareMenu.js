import { useState } from 'react';
import { toBlob, toPng } from 'html-to-image';
import './ShareMenu.css';

// Nodes worth keeping out of the exported image: this menu's own footer is
// UI chrome, not part of the "card" being shared, and the Spotify embed
// iframe is cross-origin - a canvas render can't capture its pixels at all
// (the browser blocks reading cross-origin iframe content for security), so
// it would only show up as a blank box if left in.
function excludeChrome(node) {
  return !(
    node.classList &&
    (node.classList.contains('wc-footer') || node.classList.contains('wc-embed'))
  );
}

export default function ShareMenu({ shellRef, onCreateShareLink }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  async function exportPng() {
    return toPng(shellRef.current, { pixelRatio: 2, filter: excludeChrome, cacheBust: true });
  }

  async function exportBlob() {
    return toBlob(shellRef.current, { pixelRatio: 2, filter: excludeChrome, cacheBust: true });
  }

  async function handleSaveImage() {
    setBusy(true);
    setError(false);
    try {
      const dataUrl = await exportPng();
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = 'beespotifywrapped.png';
      link.click();
      setOpen(false);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  async function handleShareImage() {
    setBusy(true);
    setError(false);
    try {
      const blob = await exportBlob();
      const file = new File([blob], 'beespotifywrapped.png', { type: 'image/png' });
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: 'BeeSpotifyWrapped',
          text: 'Check out my BeeSpotifyWrapped!',
        });
      } else {
        // Most desktop browsers don't support sharing files at all yet -
        // fall back to a plain download so the button still does something.
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'beespotifywrapped.png';
        link.click();
      }
      setOpen(false);
    } catch (err) {
      if (err.name !== 'AbortError') setError(true); // AbortError = user cancelled the share sheet, not a failure
      else setOpen(false);
    } finally {
      setBusy(false);
    }
  }

  async function handleCopyLink() {
    setBusy(true);
    setError(false);
    try {
      const url = await onCreateShareLink();
      await navigator.clipboard.writeText(url);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="share-menu">
      <button className="share-menu__trigger" onClick={() => setOpen((o) => !o)}>
        Share this Wrapped
      </button>
      {open && (
        <div className="share-menu__dropdown">
          <button onClick={handleShareImage} disabled={busy}>
            Share…
          </button>
          <button onClick={handleSaveImage} disabled={busy}>
            Save as Image
          </button>
          <button onClick={handleCopyLink} disabled={busy}>
            {linkCopied ? 'Link copied!' : 'Copy Link'}
          </button>
          {error && <p className="share-menu__error">Something went wrong — try again.</p>}
        </div>
      )}
    </div>
  );
}
