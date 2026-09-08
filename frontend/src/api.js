// All calls go through relative paths so CRA's dev-server proxy (see
// package.json "proxy") forwards them to the Flask backend during
// development, and so they stay same-origin in production behind one host.

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
