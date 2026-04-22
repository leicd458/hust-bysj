import React, { useCallback } from 'react';
import useUpload from '@/hooks/useUpload';
import usePrediction from '@/hooks/usePrediction';

// Components
import ModeSwitch from '@/components/upload/ModeSwitch';
import UploadArea from '@/components/upload/UploadArea';
import SinglePreview from '@/components/upload/SinglePreview';
import BatchPreview from '@/components/upload/BatchPreview';
import DiagnosisCard from '@/components/result/DiagnosisCard';
import GradCAMCard from '@/components/result/GradCAMCard';
import BatchSummary from '@/components/result/BatchSummary';
import BatchResultCard from '@/components/result/BatchResultCard';
import ProgressBar from '@/components/result/ProgressBar';

export default function HomePage() {
  const upload = useUpload();
  const prediction = usePrediction();

  // Hidden file input ref for "add more" and "change image"
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleAnalyze = async () => {
    if (upload.mode === 'single' && upload.singleFile) {
      await prediction.runSingle(upload.singleFile);
    } else if (upload.mode === 'batch' && upload.batchFiles.length > 0) {
      await prediction.runBatch(upload.batchFiles);
    }
  };

  const handleAddMoreClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    fileInputRef.current?.click();
  };

  const handleReset = () => {
    upload.reset();
    prediction.clearResults();
  };

  const showSingleResult = !prediction.loading && prediction.singleResult;
  const showBatchResult = !prediction.loading && prediction.batchResults.length > 0;
  const hasAnyResult = showSingleResult || showBatchResult;

  return (
    <div className="max-w-[1000px]">
      <h2 className="text-[1.45rem] font-bold text-[var(--text)] mb-6 flex items-center gap-2.5 after:content-[''] after:flex-1 after:h-px after:bg-[var(--border)] after:ml-4">
        上传超声图像
      </h2>

      {/* Mode Switch */}
      <ModeSwitch mode={upload.mode} onModeChange={m => { upload.setMode(m); handleReset(); }} />

      {/* Upload Area */}
      <div
        className="mb-10 relative overflow-hidden rounded-2xl border-2 border-dashed p-14 text-center cursor-pointer bg-white transition-all duration-300 hover:border-primary hover:bg-[var(--primary-bg)]"
        style={{ borderColor: '#cbd5e1' }}
        onClick={() => { if (!hasAnyResult) fileInputRef.current?.click(); }}
        onDragOver={e => e.currentTarget.classList.add('scale-[1.005]', e.currentTarget.style.borderColor = 'var(--primary)')}
        onDragLeave={e => { e.currentTarget.classList.remove('scale-[1.005]'); e.currentTarget.style.borderColor = '#cbd5e1'; }}
        onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove('scale-[1.005]'); e.currentTarget.style.borderColor = '#cbd5e1'; upload.handleFilesSelected(Array.from(e.dataTransfer.files)); }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple={upload.mode === 'batch'}
          className="hidden"
          onChange={e => upload.handleFilesSelected(Array.from(e.target.files || []))}
        />

        {/* Placeholder */}
        {!upload.hasFiles && (
          <div id="uploadPlaceholder" className="flex flex-col items-center">
            <div className="w-18 h-18 mx-auto mb-4.5 bg-gradient-to-br from-[var(--primary-bg)] to-cyan-100 rounded-full flex items-center justify-center text-2xl text-primary">
              📁
            </div>
            <p className="text-lg text-[var(--text)] font-semibold mb-1.5">点击或拖拽图像到此处</p>
            <p className="text-sm text-[var(--text-muted)]">
              支持 PNG / JPG / JPEG / BMP，单张最大 16MB / 批量最多 10 张
            </p>
          </div>
        )}

        {/* Single Preview */}
        {upload.mode === 'single' && upload.singlePreviewUrl && (
          <SinglePreview
            file={upload.singleFile!}
            previewUrl={upload.singlePreviewUrl}
            onChange={() => fileInputRef.current?.click()}
          />
        )}

        {/* Batch Preview */}
        {upload.mode === 'batch' && upload.batchFiles.length > 0 && (
          <BatchPreview
            files={upload.batchFiles}
            onRemove={upload.removeBatchItem}
            onAddMore={() => fileInputRef.current?.click()}
          />
        )}
      </div>

      {/* Analyze Button */}
      <div className="mt-7 text-center">
        <button
          onClick={handleAnalyze}
          disabled={!upload.hasFiles || prediction.loading}
          className="bg-gradient-to-br from-primary to-primary-dark text-white border-none px-12 py-3.5 text-base font-semibold rounded-full cursor-pointer transition-all shadow-md hover:-translate-y-0.5 hover:shadow-lg disabled:bg-gray-300 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0 inline-flex items-center justify-center gap-2 min-w-[180px]"
        >
          {prediction.loading ? (
            <>
              <span className="spinner" /> <span>分析中...</span>
            </>
          ) : (
            <span>{upload.mode === 'batch' ? '📊 批量分析' : '🔍 开始分析'}</span>
          )}
        </button>
      </div>

      {/* Progress Bar (batch) */}
      {prediction.loading && prediction.progress.total > 1 && (
        <ProgressBar
          current={prediction.progress.current}
          total={prediction.progress.total}
          filename={prediction.progress.filename}
          pct={prediction.progress.pct}
        />
      )}

      {/* Results Section */}
      {(showSingleResult || showBatchResult) && (
        <div className="mt-12 pt-9 border-t border-[var(--border)]">
          <h2 className="text-[1.45rem] font-bold text-[var(--text)] mb-6 flex items-center gap-2.5 after:content-[''] after:flex-1 after:h-px after:bg-[var(--border)] after:ml-4">
            诊断结果
          </h2>

          <div className="grid gap-6">
            {/* Single Result */}
            {showSingleResult && prediction.singleResult && (
              <>
                <DiagnosisCard
                  result={prediction.singleResult}
                  originalImageUrl={upload.singlePreviewUrl || ''}
                  inferenceTime={`${prediction.singleElapsedMs}ms | TTA`}
                />
                <GradCAMCard
                  originalImageUrl={upload.singlePreviewUrl || ''}
                  gradcamUrl={prediction.singleResult.gradcam}
                />
              </>
            )}

            {/* Batch Result */}
            {showBatchResult && (
              <>
                <BatchSummary
                  results={prediction.batchResults}
                  onExport={() => exportReport(prediction.batchResults)}
                  onClear={handleReset}
                />
                <div className="grid gap-3">
                  {prediction.batchResults.map((r, i) => (
                    <BatchResultCard key={r.index ?? i} result={r} index={r.index ?? i} />
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Disclaimer */}
          <div className="bg-amber-50 border-l-3 border-amber-400 p-3.5 py-4 mt-7 rounded-r-lg">
            <p className="text-amber-800 text-sm leading-relaxed">
              <strong>⚠️ 免责声明：</strong>本系统仅供学术研究和辅助参考，不能替代专业医生的诊断。
              如有疑问请咨询专业医疗人员。
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function exportReport(results: NonNullable<ReturnType<typeof usePrediction>['batchResults']>) {
  const lines = ['乳腺癌超声诊断 - 批量分析报告', '='.repeat(40), ''];
  lines.push(`时间: ${new Date().toLocaleString()}`);
  lines.push(`总数: ${results.length}`);
  lines.push('');
  results.forEach((r, i) => {
    if (r.error) {
      lines.push(`#${i + 1} ${r.filename} - 失败: ${r.error}`);
    } else {
      lines.push(`#${i + 1} ${r.filename} - ${r.predicted_class_cn} (${(r.confidence * 100).toFixed(1)}%)`);
    }
  });
  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `batch_report_${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}
