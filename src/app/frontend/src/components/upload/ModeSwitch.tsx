import React from 'react';
import type { AnalysisMode } from '@/types';

interface ModeSwitchProps {
  mode: AnalysisMode;
  onModeChange: (mode: AnalysisMode) => void;
}

export default function ModeSwitch({ mode, onModeChange }: ModeSwitchProps) {
  return (
    <div className="flex gap-4 justify-center flex-wrap mb-6 p-3.5-5 bg-white rounded-2xl border border-[var(--border)] shadow-sm items-center">
      <label className="inline-flex items-center gap-2.5 cursor-pointer select-none text-sm text-[var(--text-secondary)]">
        TTA 增强推理（推荐）
      </label>

      <div className="inline-flex bg-[var(--bg)] rounded-[10px] p-[3px] gap-[2px]">
        {(['single', 'batch'] as const).map(m => (
          <button
            key={m}
            onClick={() => onModeChange(m)}
            className={`px-5 py-1.75 border-none rounded-lg font-semibold text-[13.5px] cursor-pointer transition-all duration-[220ms] ${
              mode === m
                ? 'bg-white text-primary shadow-sm'
                : 'bg-transparent text-[var(--text-secondary)] hover:text-[var(--text)]'
            }`}
          >
            {m === 'single' ? '单张' : '批量'}
          </button>
        ))}
      </div>
    </div>
  );
}
