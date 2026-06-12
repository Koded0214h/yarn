import random
import string


def execute_transfer(amount: int | float, recipient: str) -> dict:
    """
    Mock transfer — in production this would call a payment provider (OPay, Flutterwave, etc.).
    Returns a simulated success response.
    """
    ref = 'YARN-' + ''.join(random.choices(string.digits, k=6))
    return {
        'success': True,
        'tx_ref': ref,
        'amount': amount,
        'recipient': recipient,
        'message': f'Transfer of ₦{amount:,} to {recipient} complete. Ref: {ref}',
        'simulated': True,
    }
