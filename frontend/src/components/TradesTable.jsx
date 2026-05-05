export default function TradesTable({ trades, symbol }) {
  if (!symbol) return null;

  if (trades.length === 0) {
    return (
      <div className="trades-empty">
        No trades found for <strong>{symbol}</strong> in the last 30 days.
      </div>
    );
  }

  return (
    <div className="trades-section">
      <p className="trades-count">
        {trades.length} trade{trades.length !== 1 ? 's' : ''} in the last 30 days
      </p>
      <div className="table-scroll">
        <table className="trades-table">
          <thead>
            <tr>
              <th>Symbol</th><th>Platform</th><th>Trade Type</th>
              <th>Option Type</th><th>Strategy</th><th>Side</th>
              <th>Expiry</th><th>Strike</th><th>Trade Price</th>
              <th>Qty</th><th>Status</th><th>Date</th>
            </tr>
          </thead>
          <tbody>
            {trades.map(trade => (
              <tr key={trade.id} className={`row-status-${trade.status}`}>
                <td>{trade.symbol}</td>
                <td>{trade.platform}</td>
                <td>{trade.trade_type}</td>
                <td>
                  {trade.option_type
                    ? <span className={`badge badge-${trade.option_type}`}>{trade.option_type}</span>
                    : <span className="badge badge-na">N/A</span>}
                </td>
                <td>
                  {trade.strategy
                    ? <span className={`badge badge-strategy badge-${trade.strategy.replace('_', '-')}`}>
                        {trade.strategy.replace(/_/g, ' ')}
                      </span>
                    : '—'}
                </td>
                <td className={`side-${trade.side}`}>{trade.side}</td>
                <td>{trade.expiration_date ?? '—'}</td>
                <td>{trade.strike_price != null ? `$${trade.strike_price}` : '—'}</td>
                <td>${trade.trade_price?.toFixed(2)}</td>
                <td>{trade.quantity}</td>
                <td>
                  <span className={`badge badge-status-${trade.status}`}>{trade.status}</span>
                </td>
                <td>{new Date(trade.executed_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
