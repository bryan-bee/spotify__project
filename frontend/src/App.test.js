import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the BeeSpotifyWrapped landing page', async () => {
  render(<App />);
  const tagline = await screen.findByText(/Your Spotify stats, wrapped up/i);
  expect(tagline).toBeInTheDocument();
});
