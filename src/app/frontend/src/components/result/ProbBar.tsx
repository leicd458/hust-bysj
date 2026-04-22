import React from 'react';

interface ProbBarProps {
  name: string;
  value: number; // 0~1
}

const PROB_STYLES: Record<string, string> = {
  benign: 'prob-benign',
  malignant: 'prob-malignant',
  normal: 'prob-normal',
};

export default function ProbBar({ name, value }: ProbBarProps) {
  const key = name.split(' ')[0].toLowerCase(); // "良性" → "benign"
  const pct = (value * 100).toFixed(2);
  const barClass = PROB_STYLES[key] || '';

  return (
    <div className="mb-3.5">
      <div className="block text-[14px] font-medium text-[var(--text-secondary)] mb-1.5">{name}</div>
      <div className="w-full h-7 bg-[#f1f5f9] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full progress-bar-fill ${barClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="text-sm text-[var(--text-muted)] font-semibold mt-1 text-right">{pct}%</div>
    </div>
  );
}
