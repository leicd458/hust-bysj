import React from 'react';
import type { BatchResult } from '@/types';

interface BatchSummaryProps {
  results: BatchResult[];
  onExport: () => void;
  onClear: () => void;
}

export default function BatchSummary({ results, onExport, onClear }: BatchSummaryProps) {
  const stats = { benign: 0, malignant: 0, normal: 0, errors: 0 };
  results.forEach(r => {
    if (r.error) stats.errors++;
    else stats[r.predicted_class] = (stats[r.predicted_class] || 0) + 1;
  });

  const summaryItems = [
    { label: '总数量', value: results.length },
    { label: '良性', value: stats.benign, cls: 'benign' as const },
    { label: '恶性', value: stats.malignant, cls: 'malignant' as const },
    { label: '正常', value: stats.normal, cls: 'normal' as const },
  ];

  return (
    <div className="bg-white border border-[var(--border)] rounded-2xl p-7 shadow-sm">
      <h3 className="text-lg font-bold text-[var(--text)] mb-4">分析摘要</h3>

      <div className="grid grid-cols-4 gap-2.5 mb-4 sm:grid-cols-4">
        {summaryItems.map(item => (
          <div key={item.label} className="text-center py-4 px-2 bg-[var(--bg)] rounded-lg">
            <span
              className={`block text-[1.6rem] font-extrabold ${item.cls ? `text-[var(--${item.cls})]` : ''}`}
              style={item.cls ? { color: `var(--${item.cls})` } : {}}
            >
              {item.value}
            </span>
            <span className="text-xs text-[var(--text-muted)] mt-0.5 block">{item.label}</span>
          </div>
        ))}
      </div>

      {stats.errors > 0 && (
        <div className="text-center py-4 px-2 bg-red-50 rounded-lg mb-4">
          <span className="block text-xl font-extrabold text-red-600">{stats.errors}</span>
          <span className="text-xs text-[var(--text-muted)]">失败</span>
        </div>
      )}

      <div className="flex gap-2.5 justify-center">
        <button
          onClick={onExport}
          className="px-4 py-2 border border-[var(--border)] bg-white text-[var(--text-secondary)] rounded-xl text-sm font-medium cursor-pointer transition-all hover:border-primary hover:text-primary hover:bg-[var(--primary-bg)]"
        >
          &#128196; 导出报告
        </button>
        <button
          onClick={onClear}
          className="px-4 py-2 border border-red-200 bg-white text-malignant rounded-xl text-sm font-medium cursor-pointer transition-all hover:bg-malignant hover:text-white"
        >
          &#128465; 清空结果
        </button>
      </div>
    </div>
  );
}
