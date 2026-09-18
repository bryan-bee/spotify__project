// fetch() calls below use relative paths - CRA's dev-server proxy (see
// package.json "proxy") forwards those to Flask during development, and
// they stay same-origin in production behind one host.
//
// LOGIN_URL is different: it's used for a real full-page navigation
// (a plain <a href>), not a fetch call. CRA's dev-server proxy only forwards
// requests whose Accept header does NOT ask for text/html - a real page
// navigation always sends "Accept: text/html", so the dev server would
// serve index.html instead of proxying it to Flask (this is intentional on
// CRA's part, so refreshing a client-side route doesn't get sent to the
// API). That makes the relative-path trick unusable for the login link, so
// it points directly at the Flask server instead.
//
// In production (npm run build sets NODE_ENV=production automatically),
// this same Flask app also serves the built frontend - genuinely the same
// origin, so a relative link is correct and simplest, exactly like the
// fetch() calls above. In local dev, the React dev server (this page) and
// Flask are two separate processes/ports, so it's built from
// window.location.hostname instead of a fixed value - works whether the
// page was opened as 127.0.0.1 (desktop) or a LAN IP (a phone on the same
// WiFi) - the backend (login.py's _redirect_uri) mirrors this same
// "derive from whoever's actually asking" approach.
export const LOGIN_URL =
  process.env.NODE_ENV === 'production'
    ? '/api/login'
    : `http://${window.location.hostname}:5000/api/login`;

async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const error = new Error(`Request to ${path} failed with ${response.status}`);
    error.status = response.status;
    try {
      error.body = await response.json();
    } catch {
      error.body = null;
    }
    throw error;
  }

  return response.json();
}

export function fetchMe() {
  return request('/api/me');
}

export function fetchTopStuff(timeRange) {
  return request(`/api/topStuff?time_range=${timeRange}`);
}

export function createShare(timeRange) {
  return request('/api/share', {
    method: 'POST',
    body: JSON.stringify({ time_range: timeRange }),
  });
}

export function fetchShare(shareId) {
  return request(`/api/share/${shareId}`);
}

export function logout() {
  return request('/api/logout', { method: 'POST' });
}
