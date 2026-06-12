import Header from './Header';
import WaveformVisualizer from './WaveformVisualizer';
import ChatArea from './ChatArea';
import InputArea from './InputArea';
import ActionLog from './ActionLog';
import ConfirmDialog from './ConfirmDialog';
import useChat from '../hooks/useChat';

const STATUS_LABELS = {
  idle:      'YARN is ready',
  listening: 'YARN is listening...',
  thinking:  'YARN is acting autonomously...',
  speaking:  'YARN is responding...',
};

export default function YarnInterface() {
  const {
    messages,
    pendingAction,
    safewordTriggered,
    isLoading,
    waveformState,
    actionLog,
    handleSend,
    handleConfirm,
    setWaveformState,
  } = useChat();

  const handleListeningChange = (listening) => {
    if (!isLoading) setWaveformState(listening ? 'listening' : 'idle');
  };

  return (
    <div className="yarn-app">
      <Header safewordTriggered={safewordTriggered} />

      <div className="call-section">
        <div className="call-section__label">◉ Simulated Voice Call · English / Pidgin</div>
        <WaveformVisualizer state={waveformState} />
        <div className={`call-section__status call-section__status--${waveformState}`}>
          {STATUS_LABELS[waveformState]}
        </div>
      </div>

      <ChatArea messages={messages} isLoading={isLoading} />

      <ActionLog entries={actionLog} />

      <InputArea
        onSend={handleSend}
        disabled={isLoading || safewordTriggered}
        onListeningChange={handleListeningChange}
      />

      {pendingAction && (
        <ConfirmDialog action={pendingAction} onConfirm={handleConfirm} />
      )}
    </div>
  );
}
