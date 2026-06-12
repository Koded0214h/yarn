export default function ConfirmDialog({ action, onConfirm }) {
  if (!action) return null;

  const descriptions = {
    transfer: `Send ₦${action.amount} to ${action.recipient}`,
  };

  const description = descriptions[action.type] ?? 'Proceed with this action?';

  return (
    <div className="confirm-overlay" role="dialog" aria-modal="true" aria-label="Confirm action">
      <div className="confirm-card">
        <div className="confirm-card__tag">▸ Awaiting Confirmation</div>
        <div className="confirm-card__text">{description}</div>
        <div className="confirm-card__sub">
          This action will be executed immediately. Say YES to confirm.
        </div>
        <div className="confirm-card__actions">
          <button className="btn btn--confirm" onClick={() => onConfirm(true)}>
            YES — Confirm
          </button>
          <button className="btn btn--cancel" onClick={() => onConfirm(false)}>
            NO — Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
