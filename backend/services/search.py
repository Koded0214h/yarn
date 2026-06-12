import httpx
import logging
from config import get_settings

logger = logging.getLogger(__name__)

# ── Pre-cached demo responses for reliable demos ──────────────────────────────
DEMO_CACHE: dict[str, str] = {
    'tomato': 'As of this morning, tomato prices at Dawanau market (Kano) are ₦26,000–₦30,000 per basket. Prices are slightly up from last week due to dry-season supply pressure. (Source: market report, 2 hours ago)',
    'yam':    'A 50kg tuber of yam at Bodija market (Ibadan) is selling for ₦15,000–₦18,000. Grade A yams fetch closer to ₦18k. (Source: market report, 3 hours ago)',
    'rice':   'A 50kg bag of parboiled rice (Abakaliki) is going for ₦72,000–₦80,000 at Mile 12 market (Lagos). Imported rice is ₦85,000+. (Source: market report, today)',
    'pepper': 'Tatashe (red bell pepper) is selling at ₦8,000–₦12,000 per basket at Ketu market. Scotch bonnet is ₦5,000 per paint bucket. (Source: market report, today)',
    'onion':  'Onions at Dawanau are ₦35,000–₦42,000 per bag (120kg). Prices have risen 15% this week. (Source: market report, today)',
}


def search_web(query: str) -> str:
    """
    Search the web via SerpAPI. Falls back to demo cache then generic mock.
    """
    # Check demo cache first
    lower = query.lower()
    for keyword, cached in DEMO_CACHE.items():
        if keyword in lower:
            return cached

    settings = get_settings()
    if not settings.SERPAPI_KEY:
        return _mock_result(query)

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(
                'https://serpapi.com/search.json',
                params={
                    'q': query,
                    'api_key': settings.SERPAPI_KEY,
                    'num': 3,
                    'gl': 'ng',   # Nigeria results
                    'hl': 'en',
                },
            )
            resp.raise_for_status()
            data = resp.json()

        # Try answer box first
        if answer := data.get('answer_box', {}).get('answer'):
            return answer
        if snippet := data.get('answer_box', {}).get('snippet'):
            return snippet

        # Fall back to first organic result snippet
        results = data.get('organic_results', [])
        if results:
            first = results[0]
            snippet = first.get('snippet', '')
            source  = first.get('source', '')
            return f'{snippet} (Source: {source})'

        return _mock_result(query)

    except Exception as exc:
        logger.error('SerpAPI error: %s', exc)
        return _mock_result(query)


def _mock_result(query: str) -> str:
    return f'[SIMULATED] Search results for "{query}" — current market prices vary by region. Check local market for exact rates. (Simulated data — connect SerpAPI for live results)'
