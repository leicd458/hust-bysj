import React, { useState } from 'react';
import type { BatchResult } from '@/types';

interface BatchResultCardProps {
  result: BatchResult;
  index: number;
}

const BADGE_STYLES: Record<string, string> = {
  benign: 'bg-[var(--benign-bg)] text-benign',
  malignant: 'bg-[var(--malignant-bg)] text-malignant',
  normal: 'bg-[var(--normal-bg)] text-normal',
};

const BORDER_COLORS: Record<string, string> = {
  benign: 'border-l-benign',
  malignant: 'border-l-malignant',
  normal: 'border-l-normal',
};

export default function BatchResultCard({ result, index }: BatchResultCardProps) {
  const [expanded, setExpanded] = useState(false);
  const hasError = !!result.error;
  const cls = result.predicted_class || '';

  return (
    <div
      className={`bg-white border border-[var(--border)] rounded-xl overflow-hidden transition-shadow hover:shadow-md ${
        hasError ? 'border-l-3 border-l-amber-500' : BORDER_COLORS[cls] ? `border-l-3 ${BORDER_COLORS[cls].replace('text-', 'border-l-')}` : ''
      }`}
      style={hasError ? { borderLeftColor: '#f59e0b', borderLeftWidth: '3px' }
        : { borderLeftColor: `var(--${cls})`, borderLeftWidth: '3px' }}
    >
      {/* Header - clickable */}
      <div
        className="flex items-center gap-3.5 p-3.5 py-4 cursor-pointer transition-colors hover:bg-[var(--bg)]"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <span className="text-xs font-bold text-[var(--text-muted)] bg-[var(--bg)] w-6.5 h-6.5 flex items-center justify-center rounded-lg flex-shrink-0">
            #{index + 1}
          </span>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-semibold text-[var(--text)] truncate">{result.filename}</span>
            <span className="text-xs text-[var(--text-muted)] mt-0.5">{result.elapsed_ms}ms</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5 flex-shrink-0">
          {hasError ? (
            <span className="px-2.5 py-0.75 rounded-full text-xs font-bold bg-amber-100 text-amber-800 whitespace-nowrap">
              分析失败
            </span>
          ) : (
            <>
              <span className={`px-2.5 py-0.75 rounded-full text-xs font-bold whitespace-nowrap ${BADGE_STYLES[cls] || ''}`}>
                {result.predicted_class_cn}
              </span>
              <span className="text-sm font-bold text-primary whitespace-nowrap">
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </>
          )}
          <span className={`text-xs transition-transform duration-250 ${expanded ? 'rotate-180' : ''}`}>
            &#9660;
          </span>
        </div>
      </div>

      {/* Expandable Detail */}
      {expanded && (
        <div className="animate-slideDown px-4.5 pb-4.5 pl-14 border-t border-[var(--border)] pt-3">
          {hasError ? (
            <p className="py-3 text-red-600 text-sm leading-relaxed">{result.error}</p>
          ) : (
            <>
              {/* Probabilities */}
              <div className="mt-2">
                {(Object.entries(result.probabilities) as [string, number][]).map(([name, prob]) => (
                  <div key={name} className="flex items-center gap-2.5 mb-2 text-sm text-[var(--text-secondary)]">
                    <span className="w-[42px] flex-shrink-0 font-medium">
                      {name === 'benign' ? '良性' : name === 'malignant' ? '恶性' : '正常'}
                    </span>
                    <div className="flex-1 h-2 bg-[#e2e8f0] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full progress-bar-fill ${
                          name === 'benign' ? 'prob-benign' :
                          name === 'malignant' ? 'prob-malignant' : 'prob-normal'
                        }`}
                        style={{ width: `${(prob * 100).toFixed(1)}%` }}
                      />
                    </div>
                    <span className="w-12 text-right font-semibold text-[var(--text)]">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>

              {/* Grad-CAM */}
              {result.gradcam && (
                <div className="mt-3.5">
                  <h5 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">Grad-CAM 热力图</h5>
                  <img
                    src={result.gradcam}
                    alt="Grad-CAM"
                    loading="lazy"
                    className="max-w-full h-auto rounded-lg border border-[var(--border)]"
                  />
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
