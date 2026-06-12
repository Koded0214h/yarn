from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from db.database import get_db
from db.crud import get_or_create_session, update_session
from schemas.chat import ChatRequest, ConfirmRequest, EmergencyRequest, ChatResponse, ActionTaken
from services.safeword import is_safeword
from services.intent_router import classify_intent
from services.transfer import execute_transfer
from services.search import search_web
from services.whatsapp import send_whatsapp
from services.invoice import generate_invoice

router = APIRouter(prefix='/api', tags=['chat'])


@router.post('/chat', response_model=ChatResponse)
def chat(body: ChatRequest, db: DBSession = Depends(get_db)):
    session = get_or_create_session(db, body.session_id)

    # Block if safeword already triggered
    if session.safeword_triggered:
        return ChatResponse(
            reply='Session is locked. Start a new session to continue.',
            action_taken=ActionTaken(type='blocked', status='locked'),
        )

    # Safeword check before Gemini (faster)
    if is_safeword(body.message):
        update_session(db, session, safeword_triggered=True, clear_pending=True)
        return ChatResponse(
            reply='Safeword recognized. All pending actions cancelled. Session locked. Emergency contacts would be alerted.',
            action_taken=ActionTaken(type='emergency', status='simulated'),
        )

    # ── Intent classification ──────────────────────────────────────────────
    result = classify_intent(body.message, session.history or [])
    intent = result.get('intent', 'other')
    params = result.get('params', {})
    reply  = result.get('response', "I didn't understand that. Could you try again?")

    action_taken     = None
    requires_confirm = False
    pending_action   = None

    # ── Execute intent ─────────────────────────────────────────────────────
    if intent == 'transfer':
        amount    = params.get('amount', 0)
        recipient = params.get('recipient', 'recipient')
        # Store pending action for confirmation flow
        pending = {'type': 'transfer', 'amount': amount, 'recipient': recipient}
        update_session(db, session, pending_action=pending)
        action_taken     = ActionTaken(type='transfer', status='awaiting_confirmation', data=params)
        requires_confirm = True
        pending_action   = pending

    elif intent == 'search':
        query          = params.get('query', body.message)
        search_result  = search_web(query)
        reply          = search_result
        action_taken   = ActionTaken(type='search', status='success', data={'query': query})
        update_session(db, session, clear_pending=True)

    elif intent == 'whatsapp':
        wa_result    = send_whatsapp(params.get('recipient', ''), params.get('message_text', ''))
        reply        = wa_result['message']
        action_taken = ActionTaken(
            type='whatsapp',
            status='simulated' if wa_result.get('simulated') else 'success',
            data=params,
        )
        update_session(db, session, clear_pending=True)

    elif intent == 'invoice':
        inv          = generate_invoice(params.get('description', ''), params.get('amount', 0), params.get('client_name', 'Client'))
        reply        = f"Your invoice is ready. Download here: {inv['url']}" if inv['success'] else 'Invoice generation failed. Please try again.'
        action_taken = ActionTaken(
            type='invoice',
            status='simulated' if inv.get('simulated') else 'success',
            data={'url': inv.get('url'), 'invoice_number': inv.get('invoice_number')},
        )
        update_session(db, session, clear_pending=True)

    elif intent == 'emergency':
        update_session(db, session, safeword_triggered=True, clear_pending=True)
        reply        = 'Emergency protocol activated. All pending actions cancelled. Session locked.'
        action_taken = ActionTaken(type='emergency', status='simulated')

    else:
        action_taken = ActionTaken(type='chat', status='success')
        update_session(db, session, clear_pending=True)

    # ── Append to history ──────────────────────────────────────────────────
    history = list(session.history or [])
    history.append({'role': 'user',      'text': body.message})
    history.append({'role': 'assistant', 'text': reply})
    # Keep last 20 turns to avoid unbounded growth
    update_session(db, session, history=history[-20:])

    return ChatResponse(
        reply=reply,
        action_taken=action_taken,
        requires_confirmation=requires_confirm,
        pending_action=pending_action,
    )


@router.post('/confirm', response_model=ChatResponse)
def confirm(body: ConfirmRequest, db: DBSession = Depends(get_db)):
    session = get_or_create_session(db, body.session_id)
    pending = session.pending_action

    if not pending:
        return ChatResponse(
            reply='No pending action to confirm.',
            action_taken=ActionTaken(type='confirm', status='no_pending'),
        )

    update_session(db, session, clear_pending=True)

    if not body.confirmed:
        history = list(session.history or [])
        history.extend([
            {'role': 'user',      'text': 'NO'},
            {'role': 'assistant', 'text': 'Action cancelled. No changes were made.'},
        ])
        update_session(db, session, history=history[-20:])
        return ChatResponse(
            reply='Action cancelled. No changes were made.',
            action_taken=ActionTaken(type='cancelled', status='success'),
        )

    # ── Execute the confirmed action ───────────────────────────────────────
    if pending['type'] == 'transfer':
        result = execute_transfer(pending['amount'], pending['recipient'])
        reply  = result['message']
        action = ActionTaken(type='confirmed', status='success', data=result)
    else:
        reply  = 'Action confirmed and executed.'
        action = ActionTaken(type='confirmed', status='success')

    history = list(session.history or [])
    history.extend([
        {'role': 'user',      'text': 'YES'},
        {'role': 'assistant', 'text': reply},
    ])
    update_session(db, session, history=history[-20:])

    return ChatResponse(reply=reply, action_taken=action)


@router.post('/emergency', response_model=ChatResponse)
def emergency(body: EmergencyRequest, db: DBSession = Depends(get_db)):
    session = get_or_create_session(db, body.session_id)
    update_session(db, session, safeword_triggered=True, clear_pending=True)

    history = list(session.history or [])
    history.extend([
        {'role': 'user',      'text': body.safeword},
        {'role': 'assistant', 'text': 'Emergency triggered. Session locked.'},
    ])
    update_session(db, session, history=history[-20:])

    return ChatResponse(
        reply='Safeword recognized. All pending actions cancelled. Session locked. Emergency contacts would be alerted.',
        action_taken=ActionTaken(type='emergency', status='simulated'),
    )
