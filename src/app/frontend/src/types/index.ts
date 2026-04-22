// ==================== 诊断类别 ====================
export type DiagnosisClass = 'benign' | 'malignant' | 'normal';

// ==================== 预测结果 ====================
export interface Probabilities {
  benign: number;
  malignant: number;
  normal: number;
}

export interface PredictionResult {
  predicted_class: DiagnosisClass;
  predicted_class_cn: string;
  confidence: number;
  probabilities: Probabilities;
  gradcam?: string;           // base64 data URL
  tta_augments?: number;
}

export interface BatchResult extends PredictionResult {
  filename: string;
  elapsed_ms: number;
  index: number;
  error?: string;
}

export interface BatchSummary {
  total: number;
  class_distribution: Record<DiagnosisClass, number>;
  malignant_ratio: number;
}

// ==================== 历史记录 ====================
export interface HistoryRecord {
  id: number;
  filename: string;
  image_size: string;
  predicted_class: DiagnosisClass;
  predicted_class_cn: string;
  confidence: number;
  probabilities: Probabilities;
  gradcam_path: string;
  model_type: string;
  use_tta: number;          // 0 | 1
  inference_time_ms: number;
  created_at: string;
}

export interface HistoryStats {
  total: number;
  class_distribution: Record<DiagnosisClass, number>;
  avg_inference_time: number;
  daily_counts: { date: string; count: number }[];
}

export interface HistoryResponse {
  success: boolean;
  records: HistoryRecord[];
}

export interface HistoryStatsResponse {
  success: boolean;
  stats: HistoryStats;
}

// ==================== 模型信息 ====================
export interface ModelInfo {
  name: string;
  test_acc: string;
  params: string;
  input_size: number;
  description: string;
  type: string;
  device: string;
  supports_tta: boolean;
}

// ==================== API 通用响应 ====================
export interface ApiResponse<T = unknown> {
  success: boolean;
  result?: T;
  results?: T[];
  summary?: BatchSummary;
  errors?: Array<{ filename: string; error: string }>;
  error?: string;
  deleted?: number;
}

// ==================== 模式 ====================
export type AnalysisMode = 'single' | 'batch';
