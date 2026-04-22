import React from 'react';
import type { PredictionResult } from '@/types';
import ProbBar from './ProbBar';

interface DiagnosisCardProps {
  result: PredictionResult;
  originalImageUrl: string;
  inferenceTime?: string;
}

const CLASS_COLORS: Record<string, { color: string; bg: string }> = {
  benign: { color: 'var(--benign)', bg: 'var(--benign-bg)' },
  malignant: { color: 'var(--malignant)', bg: 'var(--malignant-bg)' },
  normal: { color: 'var(--normal)', bg: 'var(--normal-bg)' },
};

export default function DiagnosisCard({ result, originalImageUrl, inferenceTime }: DiagnosisCardProps) {
  const cls = result.predicted_class;

  return (
    <div className="bg-white border border-[var(--border)] rounded-2xl p-7 shadow-sm">
      <h3 className="text-lg font-bold text-[var(--text)] mb-4 flex items-center gap-2">
        诊断结论
        {inferenceTime && <span className="text-xs text-[var(--text-muted)] font-normal ml-auto">{inferenceTime}</span>}
      </h3>

      <div className="text-center py-6 px-4 bg-[var(--bg)] rounded-xl mb-6">
        <div
          className={`text-[2.2rem] font-extrabold tracking-tight mb-2 ${cls}`}
          style={{ color: CLASS_COLORS[cls]?.color }}
        >
          {result.predicted_class_cn}
        </div>
        <div className="text-base text-[var(--text-secondary)]">
          置信度：<span className="font-bold text-primary text-xl">{(result.confidence * 100).toFixed(2)}%</span>
        </div>
      </div>

      {/* 概率分布 */}
      <h4 className="text-[15px] font-semibold text-[var(--text)] mb-4">各类别概率分布</h4>
      <div>
        {(Object.entries(result.probabilities) as [string, number][]).map(([name, prob]) => {
          const labelMap: Record<string, string> = {
            benign: '良性 (Benign)',
            malignant: '恶性 (Malignant)',
            normal: '正常 (Normal)',
          };
          return (
            <ProbBar key={name} name={labelMap[name] || name} value={prob} />
          );
        })}
      </div>
    </div>
  );
}
