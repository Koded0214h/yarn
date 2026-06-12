from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession
from db.models import Session as SessionModel


def get_or_create_session(db: DBSession, session_id: str) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        session = SessionModel(
            session_id=session_id,
            history=[],
            pending_action=None,
            safeword_triggered=False,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def update_session(
    db: DBSession,
    session: SessionModel,
    *,
    history: list | None = None,
    pending_action: dict | None = None,
    clear_pending: bool = False,
    safeword_triggered: bool | None = None,
) -> SessionModel:
    if history is not None:
        session.history = history
    if clear_pending:
        session.pending_action = None
    elif pending_action is not None:
        session.pending_action = pending_action
    if safeword_triggered is not None:
        session.safeword_triggered = safeword_triggered
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session
