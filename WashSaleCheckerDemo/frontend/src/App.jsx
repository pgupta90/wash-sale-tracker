import { useState, useEffect } from 'react';
import AuthBar from './components/AuthBar';
import RobinhoodModal from './components/RobinhoodModal';
import SyncBar from './components/SyncBar';
import SearchFilters from './components/SearchFilters';
import TradesTable from './components/TradesTable';
import { searchTrades } from './api';
import './App.css';

export default function App() {
  const [trades, setTrades] = useState([]);
  const [lastSymbol, setLastSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showRobinhoodModal, setShowRobinhoodModal] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 5000);
    return () => clearTimeout(id);
  }, [toast]);

  async function handleSearch({ symbol, expiry, strike }) {
    setLoading(true);
    setError(null);
    setLastSymbol(symbol);
    try {
      const results = await searchTrades({ symbol, expiry, strike });
      setTrades(results);
    } catch (err) {
      setError(err.message);
      setTrades([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-title-row">
          <h1>Wash Sale Checker</h1>
        </div>
        <AuthBar onConnectRobinhood={() => setShowRobinhoodModal(true)} />
      </header>

      {toast && (
        <div className={`toast toast-${toast.type}`}>{toast.message}</div>
      )}

      <SyncBar />

      <main className="app-main">
        <SearchFilters onSearch={handleSearch} />
        {loading && <p className="loading">Searching...</p>}
        {error && <p className="error">{error}</p>}
        {!loading && <TradesTable trades={trades} symbol={lastSymbol} />}
      </main>

      {showRobinhoodModal && (
        <RobinhoodModal onClose={() => setShowRobinhoodModal(false)} />
      )}
    </div>
  );
}
