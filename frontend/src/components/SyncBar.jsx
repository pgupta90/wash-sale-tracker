import { useState, useEffect } from 'react';
import { getSyncStatus, triggerSync } from '../api';

export default function SyncBar() {
  const [syncState, setSyncState] = useState({ status: 'idle', last_synced: null });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSyncStatus().then(setSyncState).catch(console.error);
  }, []);

  async function handleSync() {
    setLoading(true);
    setSyncState(s => ({ ...s, status: 'syncing' }));
    try {
      const result = await triggerSync();
      setSyncState(result);
    } catch (err) {
      setSyncState(s => ({ ...s, status: 'error', error: err.message }));
    } finally {
      setLoading(false);
    }
  }

  const timestampText = syncState.last_synced
    ? `Last synced: ${new Date(syncState.last_synced).toLocaleString()}`
    : 'Never synced';

  return (
    <div className="sync-bar">
      <span className="sync-timestamp">
        {syncState.status === 'syncing' ? 'Syncing...' : timestampText}
      </span>
      {syncState.status === 'error' && (
        <span className="sync-error"> — Error: {syncState.error}</span>
      )}
      <button className="sync-button" onClick={handleSync} disabled={loading}>
        {loading ? '⟳ Syncing...' : 'Sync Now'}
      </button>
    </div>
  );
}
