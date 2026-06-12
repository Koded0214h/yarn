SAFEWORDS = frozenset({
    'safeword', 'stop everything', 'cancel everything',
    'emergency help', 'abort', 'lock session',
})


def is_safeword(text: str) -> bool:
    lower = text.lower().strip()
    if lower.startswith('safeword'):
        return True
    return any(sw in lower for sw in SAFEWORDS)
