import React from 'react';
import { Link } from 'react-router-dom';
import useHistory from '@/hooks/useHistory';

const CLASS_BADGE: Record<string, string> = {
  benign: 'bg-[var(--benign-bg)] text-benign',
  malignant: 'bg-[var(--malignant-bg)] text-malignant',
  normal: 'bg-[var(--normal-bg)] text-normal',
};

function formatTime(s: string): string {
  if (!s) return '';
  try { return s.replace('T', ' ').slice(0, 16); } catch { return s; }
}

export default function HistoryPage() {
  const {
    records, stats, loading, currentPage, totalPages,
    load, deleteRecord, clearAll, changePage,
  } = useHistory();

  return (
    <div className="max-w-[1000px]">
      <h2 className="text-[1.45rem] font-bold text-[var(--text)] mb-6 flex items-center gap-2.5 after:content-[''] after:flex-1 after:h-px after:bg-[var(--border)] after:ml-4">
        诊断历史记录
      </h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-3.5 mb-6 sm:grid-cols-4 md:grid-cols-4">
        <div className="bg-white border border-[var(--border)] rounded-xl p-5 text-center shadow-sm">
          <span className="block text-[1.75rem] font-extrabold text-[var(--text-secondary)]">{stats?.total ?? 0}</span>
          <span className="text-xs text-[var(--text-muted)] mt-1 block">总次数</span>
        </div>
        <div className="bg-white border border-[var(--border)] rounded-xl p-5 text-center shadow-sm">
          <span className="block text-[1.75rem] font-extrabold" style={{ color: 'var(--benign)' }}>
            {stats?.class_distribution?.benign ?? 0}
          </span>
          <span className="text-xs text-[var(--text-muted)] mt-1 block">良性</span>
        </div>
        <div className="bg-white border border-[var(--border)] rounded-xl p-5 text-center shadow-sm">
          <span className="block text-[1.75rem] font-extrabold" style={{ color: 'var(--malignant)' }}>
            {stats?.class_distribution?.malignant ?? 0}
          </span>
          <span className="text-xs text-[var(--text-muted)] mt-1 block">恶性</span>
        </div>
        <div className="bg-white border border-[var(--border)] rounded-xl p-5 text-center shadow-sm">
          <span className="block text-[1.75rem] font-extrabold" style={{ color: 'var(--normal)' }}>
            {stats?.class_distribution?.normal ?? 0}
          </span>
          <span className="text-xs text-[var(--text-muted)] mt-1 block">正常</span>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex gap-2.5 mb-5 items-center flex-wrap">
        <button
          onClick={() => load()}
          className="bg-white text-primary border border-[var(--border)] px-4 py-1.75 rounded-full cursor-pointer text-sm font-medium transition-all hover:bg-[var(--primary-bg)] hover:border-primary"
        >
          &#8635; 刷新
        </button>
        <button
          onClick={() => confirm('确定清空所有历史记录？此操作不可撤销！') && clearAll()}
          className="bg-malignant-bg text-malignant border border-red-200 px-4 py-1.75 rounded-full cursor-pointer text-sm font-medium transition-all hover:bg-malignant hover:text-white"
        >
          &#128465; 清空全部
        </button>
        <Link
          to="/"
          className="bg-transparent text-[var(--text-secondary)] no-underline px-4 py-1.75 text-sm ml-auto transition-all hover:text-primary"
        >
          &larr; 返回诊断
        </Link>
      </div>

      {/* List */}
      <div className="grid gap-3.5">
        {loading ? (
          <p className="text-center text-[var(--text-muted)] py-12 text-[15px]">加载中...</p>
        ) : !records.length ? (
          <p className="text-center text-[#cbd5e1] py-12">暂无记录</p>
        ) : (
          records.map(r => (
            <div
              key={r.id}
              className="flex items-center gap-4 bg-white border border-[var(--border)] rounded-xl p-4 px-5 transition-all hover:shadow-md"
            >
              {/* Class Badge */}
              <div
                className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xs text-white text-center leading-tight flex-shrink-0 ${CLASS_BADGE[r.predicted_class] || ''}`}
                style={{
                  background: r.predicted_class === 'benign'
                    ? 'linear-gradient(135deg,#06b6d4,var(--benign))'
                    : r.predicted_class === 'malignant'
                      ? 'linear-gradient(135deg,#ef4444,var(--malignant))'
                      : 'linear-gradient(135deg,#34d399,var(--normal))',
                  color: 'white'
                }}
              >
                {r.predicted_class_cn}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm text-[var(--text)] truncate">{r.filename || '未命名'}</div>
                <div className="text-xs text-[var(--text-muted)] mt-1 flex items-center gap-2.5 flex-wrap">
                  <span>{r.image_size || ''}</span>
                  {r.use_tta && <span>| TTA增强</span>}
                  {r.inference_time_ms && <span>| {r.inference_time_ms}ms</span>}
                </div>
              </div>

              {/* Confidence & Time */}
              <div className="text-right min-w-[80px] flex-shrink-0">
                <div className="text-xl font-extrabold text-primary">{(r.confidence * 100).toFixed(1)}%</div>
                <div className="text-xs text-[var(--text-muted)] mt-0.5">{formatTime(r.created_at)}</div>
              </div>

              {/* Delete */}
              <button
                onClick={() => confirm('确定删除这条记录？') && deleteRecord(r.id)}
                className="bg-transparent border-none text-[#cbd5e1] cursor-pointer text-lg px-2 py-1.5 rounded-lg leading-none transition-all hover:text-malignant hover:bg-malignant-bg flex-shrink-0"
              >
                &times;
              </button>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center gap-2 mt-8">
        <button
          onClick={() => changePage(-1)}
          disabled={currentPage === 0}
          className="px-4 py-2 border border-[var(--border)] bg-white rounded-xl cursor-pointer text-sm font-medium text-[var(--text-secondary)] transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:border-primary hover:text-primary"
        >
          上一页
        </button>
        <span className="text-sm text-[var(--text-secondary)]">
          第 {currentPage + 1} / {totalPages} 页
        </span>
        <button
          onClick={() => changePage(1)}
          disabled={currentPage >= totalPages - 1}
          className="px-4 py-2 border border-[var(--border)] bg-white rounded-xl cursor-pointer text-sm font-medium text-[var(--text-secondary)] transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:border-primary hover:text-primary"
        >
          下一页
        </button>
      </div>
    </div>
  );
}
