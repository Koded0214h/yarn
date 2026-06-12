import logging
from config import get_settings

logger = logging.getLogger(__name__)


def send_whatsapp(recipient: str, message_text: str) -> dict:
    """
    Send a WhatsApp message via Twilio Sandbox.
    If Twilio is not configured, logs and returns a simulated success.
    """
    settings = get_settings()

    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN):
        logger.info('[SIMULATED] WhatsApp to %s: %s', recipient, message_text)
        return {
            'success': True,
            'simulated': True,
            'message': f'[SIMULATED] WhatsApp message sent to {recipient}.',
        }

    # Twilio requires a WhatsApp number — for prototype we use the sandbox
    # Recipients must opt into the sandbox at: https://wa.me/14155238886?text=join+<sandbox-word>
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Recipient must be whatsapp:+<country_code><number>
        to_number = recipient if recipient.startswith('whatsapp:') else f'whatsapp:{recipient}'

        msg = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            body=message_text,
            to=to_number,
        )
        return {
            'success': True,
            'simulated': False,
            'sid': msg.sid,
            'message': f'WhatsApp message sent to {recipient}. SID: {msg.sid}',
        }
    except Exception as exc:
        logger.error('Twilio WhatsApp error: %s', exc)
        return {
            'success': False,
            'simulated': True,
            'message': f'[SIMULATED] WhatsApp to {recipient}: "{message_text}"',
        }
