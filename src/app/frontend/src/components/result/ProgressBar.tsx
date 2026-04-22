import React from 'react';

interface ProgressBarProps {
  current: number;
  total: number;
  filename: string;
  pct: number; // percentage as 0-100
}

export default function ProgressBar({ current, total, filename, pct }: ProgressBarProps) {
  return (
    <div className="mt-5 p-4 py-5 bg-white border border-[var(--border)] rounded-2xl">
      <div className="flex justify-between mb-2 text-sm text-[var(--text-secondary)]">
        <span className="font-medium">正在分析 {current}/{total}: {filename}</span>
        <span className="font-bold text-primary">{pct}%</span>
      </div>
      <div className="h-2 bg-[#e2e8f0] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary to-primary-light progress-bar-fill"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
