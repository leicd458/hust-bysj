import React from 'react';

interface SinglePreviewProps {
  file: File;
  previewUrl: string;
  onChange: () => void;
}

export default function SinglePreview({ file, previewUrl, onChange }: SinglePreviewProps) {
  return (
    <div className="flex flex-col items-center w-full min-h-[200px]">
      <img
        src={previewUrl}
        alt={file.name}
        className="max-w-full h-auto max-h-[480px] rounded-xl shadow-md object-contain"
      />
      <button
        onClick={onChange}
        className="btn-secondary mt-4 bg-white text-primary border border-primary px-6 py-2 text-sm font-medium rounded-full cursor-pointer transition-all hover:bg-primary hover:text-white"
      >
        更换图像
      </button>
    </div>
  );
}
