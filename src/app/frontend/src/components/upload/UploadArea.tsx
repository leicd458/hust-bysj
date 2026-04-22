import React, { useCallback, useRef } from 'react';

interface UploadAreaProps {
  onFilesSelected: (files: File[]) => void;
  multiple?: boolean;
}

export default function UploadArea({ onFilesSelected, multiple = false }: UploadAreaProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = React.useState(false);

  const handleClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.btn-secondary') || (e.target as HTMLElement).closest('.btn-add-more')) return;
    inputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length) onFilesSelected(files);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter(f =>
      /\.(png|jpg|jpeg|bmp)$/i.test(f.name)
    );
    if (files.length) onFilesSelected(files);
  }, [onFilesSelected]);

  return (
    <div
      className={`border-2 border-dashed rounded-2xl p-14 text-center cursor-pointer transition-all duration-300 bg-white relative overflow-hidden ${
        isDragOver ? 'border-primary bg-[var(--primary-bg)] scale-[1.005]' : 'border-[#cbd5e1]'
      } hover:border-[var(--primary)] hover:bg-[var(--primary-bg)]`}
      onClick={handleClick}
      onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple={multiple}
        className="hidden"
        onChange={handleChange}
      />
    </div>
  );
}
