import json
import logging
from google import genai
from google.genai import types
from config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are YARN, a voice-first AI agent for everyday Nigerians — traders, artisans, and small business owners.

Analyze the user's message and return ONLY valid JSON matching this schema:
{
  "intent": "transfer|search|whatsapp|invoice|emergency|other",
  "params": {},
  "response": "your reply"
}

Intent classification rules:
- transfer: user wants to send or transfer money
  params: {"amount": number, "recipient": "string"}
- search: user asks about prices, market info, news, or anything requiring a web lookup
  params: {"query": "optimized search query"}
- whatsapp: user wants to send a WhatsApp or SMS message to someone
  params: {"recipient": "name or number", "message_text": "the message to send"}
- invoice: user wants a receipt, invoice, or bill generated
  params: {"description": "work/goods description", "amount": number, "client_name": "string"}
- emergency: user says a safeword or needs urgent help
  params: {}
- other: general conversation, greeting, or unclear request
  params: {}

Response style:
- Short, friendly, actionable — max 2 sentences
- Use Naira symbol ₦ for currency (NOT NGN)
- You may sprinkle Pidgin English naturally: "Oya", "No wahala", "E don do", "Wetin"
- For transfer/invoice: always confirm back the key details before asking for YES
- For search: say you are searching now (backend will inject real results)
- NEVER make up financial data"""


def get_client() -> genai.Client | None:
    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        return None
    return genai.Client(api_key=settings.GEMINI_API_KEY)


_client: genai.Client | None = None


def _ensure_client() -> genai.Client | None:
    global _client
    if _client is None:
        _client = get_client()
    return _client


def classify_intent(message: str, history: list) -> dict:
    """
    Classify user intent using Gemini. Falls back to regex heuristics if API unavailable.
    """
    client = _ensure_client()

    if client is None:
        logger.warning('Gemini not configured — using heuristic fallback')
        return _heuristic_fallback(message)

    # Build conversation history (last 6 turns = 3 exchanges)
    contents = []
    for turn in history[-6:]:
        role = 'user' if turn.get('role') == 'user' else 'model'
        contents.append(
            types.Content(role=role, parts=[types.Part(text=turn['text'])])
        )
    contents.append(types.Content(role='user', parts=[types.Part(text=message)]))

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type='application/json',
                temperature=0.3,
            ),
            contents=contents,
        )
        return json.loads(response.text)
    except Exception as exc:
        logger.error('Gemini error: %s', exc)
        return _heuristic_fallback(message)


# Heuristic fallback (no API key / API down)
def _heuristic_fallback(message: str) -> dict:
    import re
    lower = message.lower()

    if re.search(r'\bsend|transfer|pay\b', lower):
        amount = re.search(r'(\d[\d,]*)', message)
        to_m   = re.search(r'\bto\s+([A-Za-z][\w\s]{1,25}?)(?:\s*$|[.,])', message, re.I)
        amt    = amount.group(1) if amount else '5000'
        recip  = to_m.group(1).strip() if to_m else 'recipient'
        return {
            'intent': 'transfer',
            'params': {'amount': int(amt.replace(',', '')), 'recipient': recip},
            'response': f'Confirm sending ₦{amt} to {recip}? Reply YES to proceed.',
        }

    if re.search(r'\bprice|market|cost|how much|tomato|yam|rice|pepper|onion\b', lower):
        return {
            'intent': 'search',
            'params': {'query': message},
            'response': 'Oya, let me check that for you now...',
        }

    if re.search(r'\bwhatsapp|message|tell\b', lower):
        return {
            'intent': 'whatsapp',
            'params': {'recipient': 'contact', 'message_text': message},
            'response': 'No wahala, I will send that message.',
        }

    if re.search(r'\binvoice|receipt|bill\b', lower):
        return {
            'intent': 'invoice',
            'params': {'description': message, 'amount': 0, 'client_name': 'Client'},
            'response': 'Generating your invoice now...',
        }

    return {
        'intent': 'other',
        'params': {},
        'response': "I'm YARN, your voice agent. I can send money, check market prices, send messages, or generate invoices. What do you need?",
    }
