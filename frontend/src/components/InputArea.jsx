import { useState, useRef, useCallback } from 'react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';

const MicIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"
    strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="23"/>
    <line x1="8"  y1="23" x2="16" y2="23"/>
  </svg>
);

const SendIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"
    strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"/>
    <polygon points="22,2 15,22 11,13 2,9 22,2"/>
  </svg>
);

export default function InputArea({ onSend, disabled, onListeningChange }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  const handleResult = useCallback((transcript) => {
    onListeningChange?.(false);
    // Auto-dispatch voice input after brief delay for UX feedback
    setTimeout(() => {
      if (transcript.trim()) {
        onSend(transcript.trim());
        setValue('');
      }
    }, 380);
  }, [onSend, onListeningChange]);

  const handleEnd = useCallback(() => {
    onListeningChange?.(false);
  }, [onListeningChange]);

  const { isListening, isSupported, startListening, stopListening } =
    useSpeechRecognition({ onResult: handleResult, onEnd: handleEnd });

  const handleSend = useCallback(() => {
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue('');
    textareaRef.current?.focus();
  }, [value, disabled, onSend]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e) => {
    setValue(e.target.value);
    // Auto-resize textarea
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  };

  const toggleMic = () => {
    if (isListening) {
      stopListening();
    } else {
      onListeningChange?.(true);
      startListening();
    }
  };

  return (
    <div className="input-area">
      <textarea
        ref={textareaRef}
        className="input-area__field"
        placeholder={isListening ? 'Listening...' : 'Type or speak your request...'}
        value={isListening ? '🎤 Listening...' : value}
        onChange={handleChange}
        onKeyDown={handleKey}
        disabled={disabled || isListening}
        rows={1}
        aria-label="Message input"
      />
      {isSupported && (
        <button
          className={`icon-btn icon-btn--mic${isListening ? ' active' : ''}`}
          onClick={toggleMic}
          disabled={disabled}
          aria-label={isListening ? 'Stop listening' : 'Speak your request'}
          title={isListening ? 'Tap to stop' : 'Tap to speak'}
        >
          <MicIcon />
        </button>
      )}
      <button
        className="icon-btn icon-btn--send"
        onClick={handleSend}
        disabled={!value.trim() || disabled || isListening}
        aria-label="Send message"
      >
        <SendIcon />
      </button>
    </div>
  );
}
