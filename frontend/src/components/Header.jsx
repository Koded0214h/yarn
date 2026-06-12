export default function Header({ safewordTriggered }) {
  return (
    <header className="header">
      <div className="header__wordmark">
        Y<span>A</span>RN
      </div>
      <div className="header__badges">
        <span className="badge badge--call">Simulated Call · EN/PID</span>
        <span className={`badge ${safewordTriggered ? 'badge--emergency' : 'badge--safe'}`}>
          {safewordTriggered ? '⚠ LOCKED' : '● SAFE'}
        </span>
      </div>
    </header>
  );
}
