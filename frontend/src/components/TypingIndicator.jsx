export default function TypingIndicator() {
  return (
    <div className="typing-indicator" aria-live="polite" aria-label="YARN is processing">
      <div className="typing-indicator__bubble">
        <div className="typing-indicator__label">YARN acting autonomously</div>
        <div className="typing-indicator__dots">
          <span className="typing-indicator__dot" />
          <span className="typing-indicator__dot" />
          <span className="typing-indicator__dot" />
        </div>
      </div>
    </div>
  );
}
