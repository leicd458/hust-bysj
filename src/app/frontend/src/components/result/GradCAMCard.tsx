import React from 'react';

interface GradCAMCardProps {
  originalImageUrl: string;
  gradcamUrl?: string;
}

export default function GradCAMCard({ originalImageUrl, gradcamUrl }: GradCAMCardProps) {
  return (
    <div className="bg-white border border-[var(--border)] rounded-2xl p-7 shadow-sm">
      <h3 className="text-lg font-bold text-[var(--text)] mb-1">注意力热力图</h3>
      <p className="text-sm text-[var(--text-muted)] mb-4">模型关注的区域（暖色 = 高关注度）</p>

      {gradcamUrl ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mt-4">
          <div className="text-center">
            <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2.5">原始图像</h4>
            <img
              src={originalImageUrl}
              alt="原始"
              className="w-full h-auto rounded-xl shadow-sm object-contain"
            />
          </div>
          <div className="text-center">
            <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2.5">热力图叠加</h4>
            <img
              src={gradcamUrl}
              alt="Grad-CAM"
              className="w-full h-auto rounded-xl shadow-sm object-contain"
            />
          </div>
        </div>
      ) : (
        originalImageUrl && (
          <div className="text-center mt-4">
            <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2.5">原始图像</h4>
            <img src={originalImageUrl} alt="原始" className="max-w-full h-auto rounded-xl shadow-sm mx-auto" />
          </div>
        )
      )}
    </div>
  );
}
