function getAction(trade) {
  if (trade.trade_type === 'stock') {
    return trade.side === 'buy' ? 'Buy' : 'Sell';
  }
  if (trade.side === 'buy') {
    return trade.status === 'open' ? 'Buy to Open' : 'Buy to Close';
  }
  return trade.status === 'open' ? 'Sell to Open' : 'Sell to Close';
}

function computeGainLoss(trade, allTrades) {
  if (trade.status !== 'closed') return null;

  if (trade.trade_type === 'stock' && trade.side === 'sell') {
    const prior = allTrades
      .filter(t => t.symbol === trade.symbol && t.side === 'buy' && t.trade_type === 'stock' && new Date(t.executed_at) < new Date(trade.executed_at))
      .sort((a, b) => new Date(b.executed_at) - new Date(a.executed_at));
    if (!prior.length) return null;
    return (trade.trade_price - prior[0].trade_price) * Math.min(trade.quantity, prior[0].quantity);
  }

  if (trade.trade_type === 'option') {
    const matchFilter = t =>
      t.symbol === trade.symbol &&
      t.trade_type === 'option' &&
      t.expiration_date === trade.expiration_date &&
      t.strike_price === trade.strike_price &&
      t.option_type === trade.option_type &&
      new Date(t.executed_at) < new Date(trade.executed_at);

    if (trade.side === 'sell') {
      const prior = allTrades.filter(t => matchFilter(t) && t.side === 'buy')
        .sort((a, b) => new Date(b.executed_at) - new Date(a.executed_at));
      if (!prior.length) return null;
      return (trade.trade_price - prior[0].trade_price) * Math.min(trade.quantity, prior[0].quantity) * 100;
    }
    if (trade.side === 'buy') {
      const prior = allTrades.filter(t => matchFilter(t) && t.side === 'sell')
        .sort((a, b) => new Date(b.executed_at) - new Date(a.executed_at));
      if (!prior.length) return null;
      return (prior[0].trade_price - trade.trade_price) * Math.min(trade.quantity, prior[0].quantity) * 100;
    }
  }

  return null;
}

const DATE_FMT = { month: 'short', day: 'numeric', year: 'numeric' };

function fmtDate(str) {
  if (!str) return '—';
  // date-only strings (YYYY-MM-DD) must be parsed as local to avoid UTC offset shift
  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
    const [y, m, d] = str.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('en-US', DATE_FMT);
  }
  return new Date(str).toLocaleDateString('en-US', DATE_FMT);
}

function formatDateRange(trades) {
  const dates = trades.map(t => new Date(t.executed_at));
  const min = new Date(Math.min(...dates));
  const max = new Date(Math.max(...dates));
  return `${min.toLocaleDateString('en-US', DATE_FMT)} – ${max.toLocaleDateString('en-US', DATE_FMT)}`;
}

export default function TradesTable({ trades, symbol }) {
  if (!symbol) return null;

  if (trades.length === 0) {
    return (
      <div className="trades-empty">
        No trades found for <strong>{symbol}</strong>.
      </div>
    );
  }

  return (
    <div className="trades-section">
      <p className="trades-date-range">
        Trades between {formatDateRange(trades)}
      </p>
      <p className="trades-count">
        {trades.length} trade{trades.length !== 1 ? 's' : ''} found
      </p>
      <div className="table-scroll">
        <table className="trades-table">
          <thead>
            <tr>
              <th>Symbol</th><th>Trade Type</th>
              <th>Option / Strategy</th><th>Action</th>
              <th>Strike</th><th>Trade Price</th>
              <th>Qty</th><th>Status</th><th>Realized G/L</th><th>Trade Open Date</th><th>Expiry</th>
            </tr>
          </thead>
          <tbody>
            {trades.map(trade => {
              const gl = computeGainLoss(trade, trades);
              return (
                <tr key={trade.id} className={`row-status-${trade.status}`}>
                  <td>{trade.symbol}</td>
                  <td>{trade.trade_type}</td>
                  <td>
                    {trade.option_type
                      ? <>
                          <span className={`badge badge-${trade.option_type}`}>{trade.option_type}</span>
                          {trade.strategy && (
                            <span className={`badge badge-strategy badge-${trade.strategy.replace('_', '-')}`} style={{ marginLeft: 4 }}>
                              {trade.strategy.replace(/_/g, ' ')}
                            </span>
                          )}
                        </>
                      : '—'}
                  </td>
                  <td className={`side-${trade.side}`}>{getAction(trade)}</td>
                  <td>{trade.strike_price != null ? `$${trade.strike_price}` : '—'}</td>
                  <td>${trade.trade_price?.toFixed(2)}</td>
                  <td>{trade.quantity}</td>
                  <td>
                    <span className={`badge badge-status-${trade.status}`}>{trade.status}</span>
                  </td>
                  <td className={gl === null ? 'gl-na' : gl >= 0 ? 'gl-gain' : 'gl-loss'}>
                    {gl === null
                      ? '—'
                      : `${gl >= 0 ? '+' : '-'}$${Math.abs(gl).toFixed(2)}`}
                  </td>
                  <td>{fmtDate(trade.executed_at)}</td>
                  <td>{fmtDate(trade.expiration_date)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
