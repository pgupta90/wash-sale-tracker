import { useState, useEffect } from 'react';
import {
  getSyncStatus, triggerSync,
  getSchwabSyncStatus, triggerSchwabSync,
} from '../api';

const STALE_MS = 24 * 60 * 60 * 1000;

function isStale(lastSynced) {
  if (!lastSynced) return false;
  return Date.now() - new Date(lastSynced).getTime() > STALE_MS;
}

function PlatformSyncRow({ name, getStatus, triggerSync: doSync }) {
  const [syncState, setSyncState] = useState({ status: 'idle', last_synced: null });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getStatus().then(setSyncState).catch(console.error);
  }, []);

  async function handleSync() {
    setLoading(true);
    setSyncState(s => ({ ...s, status: 'syncing' }));
    try {
      const result = await doSync();
      setSyncState(result);
    } catch (err) {
      setSyncState(s => ({ ...s, status: 'error', error: err.message }));
    } finally {
      setLoading(false);
    }
  }

  const stale = isStale(syncState.last_synced);

  let timestampText;
  if (syncState.status === 'syncing') {
    timestampText = 'Syncing...';
  } else if (syncState.last_synced) {
    timestampText = `Last synced: ${new Date(syncState.last_synced).toLocaleString()}`;
  } else {
    timestampText = 'Never synced';
  }

  return (
    <div className="sync-bar-row">
      <span className="sync-platform">{name}</span>
      <span className={`sync-timestamp${stale ? ' sync-timestamp-stale' : ''}`}>
        {timestampText}{stale ? ' ⚠️' : ''}
      </span>
      {syncState.status === 'error' && (
        <span className="sync-error"> — {syncState.error}</span>
      )}
      <button className="sync-button" onClick={handleSync} disabled={loading}>
        {loading ? '⟳ Syncing...' : 'Sync Now'}
      </button>
    </div>
  );
}

export default function SyncBar() {
  return (
    <div className="sync-bar">
      <PlatformSyncRow
        name="Robinhood"
        getStatus={getSyncStatus}
        triggerSync={triggerSync}
      />
      <PlatformSyncRow
        name="Schwab"
        getStatus={getSchwabSyncStatus}
        triggerSync={triggerSchwabSync}
      />
    </div>
  );
}
