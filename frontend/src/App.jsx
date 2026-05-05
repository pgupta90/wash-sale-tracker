import { useState } from 'react';
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
        <h1>Wash Sale Checker</h1>
      </header>
      <SyncBar />
      <main className="app-main">
        <SearchFilters onSearch={handleSearch} />
        {loading && <p className="loading">Searching...</p>}
        {error && <p className="error">{error}</p>}
        {!loading && <TradesTable trades={trades} symbol={lastSymbol} />}
      </main>
    </div>
  );
}
