const BASE = 'http://localhost:8000';

export async function getAuthStatus() {
  const res = await fetch(`${BASE}/auth/status`);
  if (!res.ok) throw new Error('Failed to fetch auth status');
  return res.json();
}

export async function getSchwabAuthStatus() {
  const res = await fetch(`${BASE}/auth/schwab/status`);
  if (!res.ok) throw new Error('Failed to fetch Schwab auth status');
  return res.json();
}

export async function getSchwabConnectUrl() {
  const res = await fetch(`${BASE}/auth/schwab/connect`);
  if (!res.ok) throw new Error('Failed to get Schwab connect URL');
  return res.json();
}

export async function submitSchwabManualCallback(url) {
  const res = await fetch(`${BASE}/auth/schwab/manual-callback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error('Manual callback failed');
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

export async function getSchwabSyncStatus() {
  const res = await fetch(`${BASE}/sync/schwab/status`);
  if (!res.ok) throw new Error('Failed to fetch Schwab sync status');
  return res.json();
}

export async function triggerSchwabSync() {
  const res = await fetch(`${BASE}/sync/schwab`, { method: 'POST' });
  if (!res.ok) throw new Error('Schwab sync failed');
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
