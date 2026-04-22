import React, { useState, useCallback } from 'react';
import type { AnalysisMode } from '@/types';

const MAX_BATCH_FILES = 10;
const MAX_FILE_SIZE = 16 * 1024 * 1024; // 16MB
const ALLOWED_EXTS = ['.png', '.jpg', '.jpeg', '.bmp'];

interface UseUploadReturn {
  mode: AnalysisMode;
  setMode: (mode: AnalysisMode) => void;
  singleFile: File | null;
  batchFiles: File[];
  singlePreviewUrl: string | null;
  setSinglePreviewUrl: (url: string | null) => void;
  handleFilesSelected: (files: File[]) => void;
  removeBatchItem: (index: number) => void;
  addMoreFiles: (files: File[]) => void;
  reset: () => void;
  hasFiles: boolean;
}

function validateFile(file: File): boolean {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!ALLOWED_EXTS.includes(ext)) return false;
  if (file.size > MAX_FILE_SIZE) return false;
  return true;
}

export default function useUpload(): UseUploadReturn {
  const [mode, setMode] = useState<AnalysisMode>('single');
  const [singleFile, setSingleFile] = useState<File | null>(null);
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [singlePreviewUrl, setSinglePreviewUrl] = useState<string | null>(null);

  const handleFilesSelected = useCallback((files: File[]) => {
    const valid = files.filter(validateFile);
    if (!valid.length) return;

    if (mode === 'single') {
      const f = valid[0];
      setSingleFile(f);
      const reader = new FileReader();
      reader.onload = e => setSinglePreviewUrl(e.target?.result as string);
      reader.readAsDataURL(f);
    } else {
      setBatchFiles(prev => {
        const existingNames = prev.map(f => f.name);
        const newFiles = valid.filter(f => !existingNames.includes(f.name));
        const merged = [...prev, ...newFiles].slice(0, MAX_BATCH_FILES);
        return merged;
      });
    }
  }, [mode]);

  const removeBatchItem = useCallback((index: number) => {
    setBatchFiles(prev => {
      const next = [...prev];
      next.splice(index, 1);
      if (next.length === 0) return [];
      return next;
    });
  }, []);

  const addMoreFiles = useCallback((files: File[]) => {
    const valid = files.filter(validateFile);
    setBatchFiles(prev => {
      const existingNames = prev.map(f => f.name);
      const newFiles = valid.filter(f => !existingNames.includes(f.name));
      return [...prev, ...newFiles].slice(0, MAX_BATCH_FILES);
    });
  }, []);

  const reset = useCallback(() => {
    setSingleFile(null);
    setBatchFiles([]);
    setSinglePreviewUrl(null);
  }, []);

  const hasFiles = mode === 'single' ? !!singleFile : batchFiles.length > 0;

  return {
    mode, setMode,
    singleFile, batchFiles,
    singlePreviewUrl, setSinglePreviewUrl,
    handleFilesSelected, removeBatchItem, addMoreFiles,
    reset, hasFiles,
  };
}
