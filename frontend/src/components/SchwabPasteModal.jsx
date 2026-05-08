import { useState } from 'react';
import { submitSchwabManualCallback } from '../api';

export default function SchwabPasteModal({ onClose, onSuccess }) {
  const [pastedUrl, setPastedUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit() {
    if (!pastedUrl.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await submitSchwabManualCallback(pastedUrl.trim());
      if (result.success) {
        onSuccess();
      } else {
        setError(result.error || 'Connection failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Connect Schwab</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <p className="modal-instruction">
            After approving on Schwab, your browser will show a page that can't load.
            Copy the full URL from the address bar and paste it below.
          </p>
          <ol className="modal-steps">
            <li>Approve the connection on the Schwab page that just opened</li>
            <li>Your browser will redirect to a URL starting with <code>https://127.0.0.1</code></li>
            <li>Copy the full URL from the address bar</li>
            <li>Paste it here:</li>
          </ol>
          <input
            className="modal-url-input"
            type="text"
            placeholder="https://127.0.0.1?code=..."
            value={pastedUrl}
            onChange={e => setPastedUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            autoFocus
          />
          {error && <p className="modal-error">{error}</p>}
        </div>
        <div className="modal-footer">
          <button className="modal-done-btn" onClick={handleSubmit} disabled={submitting || !pastedUrl.trim()}>
            {submitting ? 'Connecting...' : 'Connect'}
          </button>
        </div>
      </div>
    </div>
  );
}
