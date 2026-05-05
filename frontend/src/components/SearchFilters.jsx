import { useState } from 'react';

export default function SearchFilters({ onSearch }) {
  const [symbol, setSymbol] = useState('');
  const [expiry, setExpiry] = useState('');
  const [strike, setStrike] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!symbol.trim()) return;
    onSearch({
      symbol: symbol.trim().toUpperCase(),
      expiry: expiry || undefined,
      strike: strike !== '' ? parseFloat(strike) : undefined,
    });
  }

  return (
    <form className="search-filters" onSubmit={handleSubmit}>
      <label className="filter-group">
        <span>Symbol *</span>
        <input
          type="text"
          value={symbol}
          onChange={e => setSymbol(e.target.value)}
          placeholder="e.g. META"
          required
        />
      </label>
      <label className="filter-group">
        <span>Expiry</span>
        <input
          type="date"
          value={expiry}
          onChange={e => setExpiry(e.target.value)}
        />
      </label>
      <label className="filter-group">
        <span>Strike</span>
        <input
          type="number"
          value={strike}
          onChange={e => setStrike(e.target.value)}
          placeholder="e.g. 600"
          step="0.5"
          min="0"
        />
      </label>
      <button type="submit">Search</button>
    </form>
  );
}
