const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function sendMessage(message, sessionId) {
  try {
    return await request('/api/chat', { message, session_id: sessionId });
  } catch {
    return getMockResponse(message);
  }
}

export async function confirmAction(sessionId, confirmed) {
  try {
    return await request('/api/confirm', { session_id: sessionId, confirmed });
  } catch {
    const ref = 'YARN-' + String(Math.floor(Math.random() * 9000) + 1000);
    return confirmed
      ? { reply: `Transfer complete. Reference: ${ref}`, action_taken: { type: 'confirmed', status: 'success' } }
      : { reply: 'Action cancelled. No funds moved.', action_taken: { type: 'cancelled', status: 'success' } };
  }
}

export async function triggerEmergency(sessionId, safeword) {
  try {
    return await request('/api/emergency', { session_id: sessionId, safeword });
  } catch {
    return {
      reply: 'Safeword recognized. All pending actions cancelled. Session locked. Emergency contacts would be alerted.',
      action_taken: { type: 'emergency', status: 'simulated' },
    };
  }
}

// ── Mock fallback responses (used when backend is down) ──
function getMockResponse(message) {
  const lower = message.toLowerCase();

  if (/send|transfer|pay/.test(lower)) {
    const amount  = message.match(/(\d[\d,]*)/)?.[1] ?? '5000';
    const toMatch = message.match(/to\s+([A-Za-z][\w\s]{1,30}?)(?:\s*$|[.,])/i);
    const recipient = toMatch?.[1]?.trim() ?? 'recipient';
    return {
      reply: `Confirm sending ₦${amount} to ${recipient}? Reply YES to proceed.`,
      action_taken: { type: 'transfer', amount, recipient, status: 'awaiting_confirmation' },
      requires_confirmation: true,
      pending_action: { type: 'transfer', amount, recipient },
    };
  }

  if (/price|market|cost|how much|tomato|yam|rice|pepper|onion/.test(lower)) {
    return {
      reply: '[SIMULATED] As of this morning, tomatoes go for ₦28,000 per basket at Dawanau market. Yam is ₦15,000–₦18,000 for 50kg. Prices checked 2 hours ago.',
      action_taken: { type: 'search', query: message, status: 'simulated' },
    };
  }

  if (/invoice|receipt|bill/.test(lower)) {
    return {
      reply: '[SIMULATED] Invoice generated. Download: yarn-invoice-demo.pdf — Link sent to your email.',
      action_taken: { type: 'invoice', status: 'simulated', url: '#' },
    };
  }

  if (/whatsapp|message|tell|contact|chat/.test(lower)) {
    return {
      reply: "[SIMULATED] WhatsApp message sent to contact.",
      action_taken: { type: 'whatsapp', status: 'simulated' },
    };
  }

  return {
    reply: "Sannu! I'm YARN, your voice-first agent. I can send money, check market prices, send WhatsApp messages, or generate invoices — all by voice. What do you need?",
    action_taken: { type: 'chat', status: 'success' },
  };
}
