import { useState, useEffect, useRef, useCallback } from 'react';

export default function useSpeechRecognition({ onResult, onEnd } = {}) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);
  // Use refs so recognition event handlers never become stale
  const onResultRef = useRef(onResult);
  const onEndRef    = useRef(onEnd);

  useEffect(() => { onResultRef.current = onResult; }, [onResult]);
  useEffect(() => { onEndRef.current = onEnd; }, [onEnd]);

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    setIsSupported(true);

    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-NG'; // Nigerian English; falls back gracefully

    recognition.onresult = (e) => {
      const transcript = e.results[0]?.[0]?.transcript ?? '';
      if (transcript) onResultRef.current?.(transcript);
    };

    recognition.onend = () => {
      setIsListening(false);
      onEndRef.current?.();
    };

    recognition.onerror = (e) => {
      if (e.error !== 'aborted') console.warn('Speech recognition error:', e.error);
      setIsListening(false);
      onEndRef.current?.();
    };

    recognitionRef.current = recognition;
  }, []);

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;
    try {
      recognitionRef.current.start();
      setIsListening(true);
    } catch { /* already started */ }
  }, [isListening]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;
    recognitionRef.current.stop();
  }, [isListening]);

  return { isListening, isSupported, startListening, stopListening };
}
