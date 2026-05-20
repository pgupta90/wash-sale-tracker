import { useState, useEffect } from 'react';
import { getAuthStatus } from '../api';

export default function AuthBar({ onConnectRobinhood }) {
  const [status, setStatus] = useState({ authenticated: false });

  useEffect(() => {
    getAuthStatus().then(setStatus).catch(console.error);
  }, []);

  return (
    <div className="auth-bar">
      <div className="auth-bar-row">
        <span className={`auth-dot ${status.authenticated ? 'auth-dot-connected' : 'auth-dot-disconnected'}`} />
        <span className="auth-platform-name">Robinhood</span>
        <span className={`auth-status-text ${status.authenticated ? 'auth-connected' : 'auth-disconnected'}`}>
          {status.authenticated ? 'Connected' : 'Not connected'}
        </span>
        {!status.authenticated && (
          <button className="auth-connect-btn" onClick={onConnectRobinhood}>
            Connect
          </button>
        )}
      </div>
    </div>
  );
}
