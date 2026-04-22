import React, { useEffect } from 'react';

interface BatchPreviewProps {
  files: File[];
  onRemove: (index: number) => void;
  onAddMore: () => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / 1048576).toFixed(1) + 'MB';
}

export default function BatchPreview({ files, onRemove, onAddMore }: BatchPreviewProps) {
  const [previews, setPreviews] = React.useState<string[]>([]);

  useEffect(() => {
    const readers = files.map(f => {
      return new Promise<string>(resolve => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target?.result as string);
        reader.readAsDataURL(f);
      });
    });
    Promise.all(readers).then(setPreviews);
  }, [files]);

  return (
    <div className="p-3 text-left">
      <div className="flex items-center justify-between mb-3.5">
        <h4 className="text-[15px] font-semibold text-[var(--text)]">
          待分析文件 ({files.length})
        </h4>
        <button
          onClick={e => { e.stopPropagation(); onAddMore(); }}
          className="px-3.5 py-1 border-dashed border-primary bg-transparent text-primary rounded-lg text-xs font-medium cursor-pointer transition-all hover:bg-[var(--primary-bg)]"
        >
          + 继续添加
        </button>
      </div>

      <div className="grid grid-cols-[repeat(auto-fill,minmax(110px,1fr))] gap-2.5 max-h-[280px] overflow-y-auto pr-1 custom-scrollbar">
        {files.map((f, i) => (
          <div
            key={i}
            className="bg-[var(--bg)] rounded-md overflow-hidden border border-transparent hover:border-[var(--primary-light)] transition-colors"
          >
            <div className="relative w-full aspect-square bg-[#e2e8f0] flex items-center justify-center">
              {previews[i] ? (
                <img src={previews[i]} alt={f.name} className="w-full h-full object-cover" />
              ) : (
                <span className="text-sm font-bold text-[var(--text-muted)]">IMG</span>
              )}
              <button
                onClick={() => onRemove(i)}
                className="absolute top-1 right-1 w-5.5 h-5.5 bg-black/45 text-white rounded-full border-none cursor-pointer text-base leading-none flex items-center justify-center opacity-0 hover:opacity-100 hover:bg-malignant transition-opacity"
                title="移除"
              >
                &times;
              </button>
            </div>
            <div className="flex items-center justify-between gap-1 p-1.5 p-x-2">
              <span className="text-xs text-[var(--text)] overflow-hidden text-ellipsis whitespace-nowrap font-medium flex-1 min-w-0 block">
                {f.name}
              </span>
              <span className="text-[11px] text-[var(--text-muted)] flex-shrink-0">
                {formatSize(f.size)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
