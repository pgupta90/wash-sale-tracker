import { useState } from 'react';
import { getAuthStatus } from '../api';

const COMMAND = 'python3 backend/authenticate.py';

export default function RobinhoodModal({ onClose }) {
  const [copyLabel, setCopyLabel] = useState('Copy');
  const [checking, setChecking] = useState(false);
  const [notConnected, setNotConnected] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(COMMAND).then(() => {
      setCopyLabel('Copied!');
      setTimeout(() => setCopyLabel('Copy'), 2000);
    });
  }

  async function handleDone() {
    setChecking(true);
    setNotConnected(false);
    try {
      const status = await getAuthStatus();
      if (status.authenticated) {
        onClose();
      } else {
        setNotConnected(true);
      }
    } catch {
      setNotConnected(true);
    } finally {
      setChecking(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Connect Robinhood</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <p className="modal-instruction">
            Robinhood uses push notification auth that requires your terminal.
          </p>
          <ol className="modal-steps">
            <li>Open Terminal</li>
            <li>
              Run this command:
              <div className="modal-command-block">
                <code>{COMMAND}</code>
                <button className="modal-copy-btn" onClick={handleCopy}>{copyLabel}</button>
              </div>
            </li>
            <li>Approve on your Robinhood app</li>
            <li>Return here and click Done</li>
          </ol>
          {notConnected && (
            <p className="modal-error">
              Still not connected — did you complete the steps?
            </p>
          )}
        </div>
        <div className="modal-footer">
          <button className="modal-done-btn" onClick={handleDone} disabled={checking}>
            {checking ? 'Checking...' : 'Done, Refresh'}
          </button>
        </div>
      </div>
    </div>
  );
}
