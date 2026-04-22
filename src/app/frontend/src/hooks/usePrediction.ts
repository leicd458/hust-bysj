import React, { useState, useCallback } from 'react';
import type { PredictionResult, BatchResult } from '@/types';
import { predictTTA, predictBatch } from '@/api';

interface UsePredictionReturn {
  loading: boolean;
  singleResult: PredictionResult | null;
  singleElapsedMs: number;
  batchResults: BatchResult[];
  progress: { current: number; total: number; filename: string; pct: number };
  runSingle: (file: File) => Promise<void>;
  runBatch: (files: File[]) => Promise<void>;
  clearResults: () => void;
}

export default function usePrediction(): UsePredictionReturn {
  const [loading, setLoading] = useState(false);
  const [singleResult, setSingleResult] = useState<PredictionResult | null>(null);
  const [singleElapsedMs, setSingleElapsedMs] = useState(0);
  const [batchResults, setBatchResults] = useState<BatchResult[]>([]);
  const [progress, setProgress] = useState({ current: 0, total: 0, filename: '', pct: 0 });

  const runSingle = useCallback(async (file: File) => {
    setLoading(true);
    try {
      const { result, elapsedMs } = await predictTTA(file);
      setSingleResult(result);
      setSingleElapsedMs(elapsedMs);
    } catch (err) {
      alert('分析失败: ' + (err instanceof Error ? err.message : String(err)));
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const runBatch = useCallback(async (files: File[]) => {
    setLoading(true);
    const results: BatchResult[] = [];
    const total = files.length;

    for (let i = 0; i < total; i++) {
      const f = files[i];
      setProgress({ current: i + 1, total, filename: f.name, pct: Math.round(((i + 1) / total) * 100) });

      try {
        const t0 = performance.now();
        // Call TTA for each file in batch mode
        const { result } = await predictTTA(f);
        results.push({
          ...result,
          filename: f.name,
          elapsed_ms: Math.round(performance.now() - t0),
          index: i,
        });
      } catch (err) {
        results.push({
          filename: f.name,
          error: err instanceof Error ? err.message : '分析失败',
          elapsed_ms: 0,
          index: i,
          predicted_class: 'benign',
          predicted_class_cn: '',
          confidence: 0,
          probabilities: { benign: 0, malignant: 0, normal: 0 },
        });
      }
    }

    setBatchResults(results);
    setLoading(false);
  }, []);

  const clearResults = useCallback(() => {
    setSingleResult(null);
    setSingleElapsedMs(0);
    setBatchResults([]);
    setProgress({ current: 0, total: 0, filename: '', pct: 0 });
  }, []);

  return { loading, singleResult, singleElapsedMs, batchResults, progress, runSingle, runBatch, clearResults };
}
