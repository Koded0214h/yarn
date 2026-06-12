const ACTION_LABELS = {
  transfer:  '⟢ TRANSFER',
  search:    '◎ WEB SEARCH',
  whatsapp:  '◈ WHATSAPP',
  invoice:   '▣ INVOICE',
  emergency: '⚠ EMERGENCY',
  confirmed: '✓ CONFIRMED',
};

function formatTime(date) {
  return new Intl.DateTimeFormat('en-NG', {
    hour:   '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

export default function MessageBubble({ message }) {
  const { role, text, timestamp, actionType } = message;
  const isUser   = role === 'user';
  const hasAction = !isUser && actionType && ACTION_LABELS[actionType];

  return (
    <div className={`msg msg--${role}${hasAction ? ' msg--action' : ''}`}>
      <div className="msg__bubble">
        {hasAction && (
          <div className="msg__action-tag">{ACTION_LABELS[actionType]}</div>
        )}
        {text}
        <span className="msg__meta">{formatTime(timestamp)}</span>
      </div>
    </div>
  );
}
