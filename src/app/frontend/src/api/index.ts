/**
 * API 客户端层
 * 统一封装所有后端 API 调用
 */

import type {
  PredictionResult,
  BatchSummary,
  ApiResponse,
  HistoryRecord,
  HistoryStats,
  ModelInfo,
  HistoryResponse,
  HistoryStatsResponse,
} from '@/types';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const BASE_URL = (import.meta as any).env?.DEV ? '' : '';

// ==================== 工具函数 ====================

function buildUrl(path: string, params?: Record<string, string | number>): string {
  const url = new URL(path, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
  }
  return url.toString();
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, { ...options });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ==================== 预测接口 ====================

/** 标准单图预测 */
export async function predict(file: File): Promise<PredictionResult> {
  const formData = new FormData();
  formData.append('file', file);
  const data = await request<ApiResponse<PredictionResult>>(`${BASE_URL}/predict`, {
    method: 'POST',
    body: formData,
  });
  if (!data.success || !data.result) throw new Error(data.error || '预测失败');
  return data.result;
}

/** TTA 增强单图预测 */
export async function predictTTA(file: File): Promise<{ result: PredictionResult; elapsedMs: number }> {
  const t0 = performance.now();
  const formData = new FormData();
  formData.append('file', file);
  const data = await request<ApiResponse<PredictionResult>>(`${BASE_URL}/predict_tta`, {
    method: 'POST',
    body: formData,
  });
  if (!data.success || !data.result) throw new Error(data.error || 'TTA预测失败');
  return { result: data.result, elapsedMs: Math.round(performance.now() - t0) };
}

/** 批量预测 */
export async function predictBatch(files: File[]): Promise<{
  results: PredictionResult[];
  summary: BatchSummary;
}> {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  const data = await request<ApiResponse<PredictionResult>>(`${BASE_URL}/predict_batch`, {
    method: 'POST',
    body: formData,
  });
  if (!data.success) throw new Error(data.error || '批量预测失败');
  return {
    results: data.results ?? [],
    summary: data.summary!,
  };
}

// ==================== 历史记录 ====================

export async function fetchHistory(limit = 50, offset = 0): Promise<HistoryResponse> {
  return request<HistoryResponse>(buildUrl(`${BASE_URL}/api/history`, { limit, offset }));
}

export async function fetchHistoryStats(): Promise<HistoryStatsResponse> {
  return request<HistoryStatsResponse>(`${BASE_URL}/api/history/stats`);
}

export async function deleteHistoryRecord(id: number): Promise<void> {
  await request<ApiResponse>(`${BASE_URL}/api/history/${id}`, { method: 'DELETE' });
}

export async function clearAllHistory(): Promise<number> {
  const data = await request<ApiResponse>(`${BASE_URL}/api/history/clear`, { method: 'DELETE' });
  return data.deleted ?? 0;
}

// ==================== 模型信息 ====================

export async function fetchModelInfo(): Promise<ModelInfo> {
  return request<ModelInfo>(`${BASE_URL}/api/model_info`);
}

export async function healthCheck() {
  return request<{ status: string; model: string; device: string }>(`${BASE_URL}/health`);
}

// ==================== PDF 报告 ====================

interface PdfReportPayload {
  result: PredictionResult;
  image_base64?: string;
  gradcam_base64?: string;
}

export async function generatePdfReport(payload: PdfReportPayload): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/report/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('PDF生成失败');
  return res.blob();
}
