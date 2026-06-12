import { useState } from 'react';

const TYPE_LABELS = {
  search:    'SEARCH',
  transfer:  'TRANSFER',
  whatsapp:  'WHATSAPP',
  invoice:   'INVOICE',
  emergency: 'EMERGENCY',
  confirmed: 'CONFIRMED',
  cancelled: 'CANCELLED',
  chat:      'CHAT',
};

export default function ActionLog({ entries }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="action-log-toggle"
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
        aria-controls="action-log-panel"
      >
        <span>Action Log</span>
        <span className="action-log-toggle__right">
          {entries.length > 0 && (
            <span className="action-log-toggle__count">{entries.length}</span>
          )}
          <span className={`action-log-toggle__chevron${open ? ' open' : ''}`}>▲</span>
        </span>
      </button>

      <div
        id="action-log-panel"
        className={`action-log${open ? ' open' : ''}`}
        aria-hidden={!open}
      >
        <div className="action-log__inner">
          {entries.length === 0 ? (
            <span className="action-log__empty">No actions yet.</span>
          ) : (
            entries.map(entry => (
              <div
                key={entry.id}
                className={`action-log__entry${entry.status === 'error' ? ' action-log__entry--error' : ''}`}
              >
                <span className={`action-log__badge action-log__badge--${entry.type}`}>
                  {TYPE_LABELS[entry.type] ?? entry.type.toUpperCase()}
                </span>
                <span>{entry.text}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
