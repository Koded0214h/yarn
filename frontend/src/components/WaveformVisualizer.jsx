import { useMemo } from 'react';

const BAR_COUNT = 38;

export default function WaveformVisualizer({ state = 'idle' }) {
  const bars = useMemo(() =>
    Array.from({ length: BAR_COUNT }, (_, i) => ({
      r:     (Math.sin(i * 1.72 + 0.85) * 0.5 + 0.5).toFixed(3),
      delay: (-((i * 0.067) % 0.94)).toFixed(3) + 's',
      dur:   (1.3 + Math.abs(Math.sin(i * 0.41)) * 1.3).toFixed(2) + 's',
    })),
    []
  );

  return (
    <div
      className="waveform"
      data-state={state}
      role="img"
      aria-label={`YARN voice visualizer — ${state}`}
    >
      {bars.map((bar, i) => (
        <span
          key={i}
          className="waveform__bar"
          style={{
            '--r':     bar.r,
            '--delay': bar.delay,
            '--dur':   bar.dur,
          }}
        />
      ))}
    </div>
  );
}
