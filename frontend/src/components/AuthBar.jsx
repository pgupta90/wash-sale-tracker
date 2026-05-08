import { useState, useEffect } from 'react';
import { getAuthStatus, getSchwabAuthStatus, getSchwabConnectUrl } from '../api';

function PlatformAuthRow({ name, getStatus, onConnectClick, isConnecting }) {
  const [status, setStatus] = useState({ authenticated: false });

  const refresh = () => getStatus().then(setStatus).catch(console.error);

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!isConnecting) return;
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [isConnecting]);

  return (
    <div className="auth-bar-row">
      <span className={`auth-dot ${status.authenticated ? 'auth-dot-connected' : 'auth-dot-disconnected'}`} />
      <span className="auth-platform-name">{name}</span>
      <span className={`auth-status-text ${status.authenticated ? 'auth-connected' : 'auth-disconnected'}`}>
        {status.authenticated ? 'Connected' : 'Not connected'}
      </span>
      {!status.authenticated && (
        <button className="auth-connect-btn" onClick={onConnectClick}>
          Connect
        </button>
      )}
    </div>
  );
}

export default function AuthBar({ onConnectRobinhood, schwabConnecting, onSchwabConnectInitiated }) {
  async function handleConnectSchwab() {
    try {
      const { url } = await getSchwabConnectUrl();
      window.open(url, '_blank');
      if (onSchwabConnectInitiated) onSchwabConnectInitiated();
    } catch (err) {
      console.error('Failed to get Schwab connect URL', err);
    }
  }

  return (
    <div className="auth-bar">
      <PlatformAuthRow
        name="Robinhood"
        getStatus={getAuthStatus}
        onConnectClick={onConnectRobinhood}
        isConnecting={false}
      />
      <PlatformAuthRow
        name="Schwab"
        getStatus={getSchwabAuthStatus}
        onConnectClick={handleConnectSchwab}
        isConnecting={schwabConnecting}
      />
    </div>
  );
}
