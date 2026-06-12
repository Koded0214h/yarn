import { useState, useCallback, useRef } from 'react';
import { sendMessage, confirmAction, triggerEmergency } from '../api/client';

const SAFEWORDS = ['safeword', 'stop everything', 'cancel everything', 'emergency help'];

function makeId() { return crypto.randomUUID(); }

export default function useChat() {
  const [messages, setMessages] = useState([
    {
      id: makeId(),
      role: 'assistant',
      text: "Sannu! I'm YARN, your voice-first agent. I can send money, check market prices, send messages, or generate invoices — all by voice or text. What do you need?",
      timestamp: new Date(),
    },
  ]);
  const [pendingAction, setPendingAction]           = useState(null);
  const [safewordTriggered, setSafewordTriggered]   = useState(false);
  const [isLoading, setIsLoading]                   = useState(false);
  const [waveformState, setWaveformState]           = useState('idle');
  const [actionLog, setActionLog]                   = useState([]);
  const sessionId = useRef(makeId());

  const addMessage = useCallback((role, text, extra = {}) => {
    setMessages(prev => [
      ...prev,
      { id: makeId(), role, text, timestamp: new Date(), ...extra },
    ]);
  }, []);

  const addLog = useCallback((entry) => {
    setActionLog(prev => [...prev, { id: makeId(), timestamp: new Date(), ...entry }]);
  }, []);

  const handleSend = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const lower = text.toLowerCase();

    // ── Safeword detection ───────────────────────────────
    if (SAFEWORDS.some(sw => lower.includes(sw)) || lower.startsWith('safeword')) {
      addMessage('user', text);
      setSafewordTriggered(true);
      setPendingAction(null);
      setIsLoading(true);
      setWaveformState('thinking');

      const res = await triggerEmergency(sessionId.current, text);
      addMessage('assistant', res.reply, { actionType: 'emergency' });
      addLog({ type: 'emergency', text: 'Emergency triggered — session locked', status: 'simulated' });
      setIsLoading(false);
      setWaveformState('idle');
      return;
    }

    addMessage('user', text);
    setIsLoading(true);
    setWaveformState('thinking');

    const res = await sendMessage(text, sessionId.current);

    addMessage('assistant', res.reply, { actionType: res.action_taken?.type });

    if (res.action_taken) {
      addLog({
        type:   res.action_taken.type ?? 'chat',
        text:   `Intent: ${res.action_taken.type ?? 'chat'} — ${res.action_taken.status ?? 'ok'}`,
        status: res.action_taken.status ?? 'success',
      });
    }

    if (res.requires_confirmation && res.pending_action) {
      setPendingAction(res.pending_action);
    }

    setIsLoading(false);
    setWaveformState('speaking');
    setTimeout(() => setWaveformState('idle'), 2800);
  }, [isLoading, addMessage, addLog]);

  const handleConfirm = useCallback(async (confirmed) => {
    setPendingAction(null);
    addMessage('user', confirmed ? 'YES' : 'NO');
    setIsLoading(true);
    setWaveformState('thinking');

    const res = await confirmAction(sessionId.current, confirmed);

    addMessage('assistant', res.reply, { actionType: res.action_taken?.type });
    addLog({
      type:   res.action_taken?.type ?? 'confirmed',
      text:   res.reply.slice(0, 70),
      status: res.action_taken?.status ?? 'success',
    });

    setIsLoading(false);
    setWaveformState('speaking');
    setTimeout(() => setWaveformState('idle'), 2000);
  }, [addMessage, addLog]);

  return {
    messages,
    pendingAction,
    safewordTriggered,
    isLoading,
    waveformState,
    actionLog,
    sessionId: sessionId.current,
    handleSend,
    handleConfirm,
    setWaveformState,
  };
}
