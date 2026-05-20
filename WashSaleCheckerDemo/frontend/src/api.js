const BASE = 'http://localhost:8001';

export async function getAuthStatus() {
  const res = await fetch(`${BASE}/auth/status`);
  if (!res.ok) throw new Error('Failed to fetch auth status');
  return res.json();
}

export async function getSyncStatus() {
  const res = await fetch(`${BASE}/sync/status`);
  if (!res.ok) throw new Error('Failed to fetch sync status');
  return res.json();
}

export async function triggerSync() {
  const res = await fetch(`${BASE}/sync`, { method: 'POST' });
  if (!res.ok) throw new Error('Sync failed');
  return res.json();
}

export async function searchTrades({ symbol, expiry, strike }) {
  const params = new URLSearchParams({ symbol });
  if (expiry) params.set('expiry', expiry);
  if (strike !== undefined && strike !== '') params.set('strike', String(strike));
  const res = await fetch(`${BASE}/trades?${params}`);
  if (!res.ok) throw new Error('Failed to fetch trades');
  return res.json();
}
