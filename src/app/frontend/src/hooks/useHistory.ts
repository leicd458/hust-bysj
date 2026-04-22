import React, { useState, useEffect, useCallback } from 'react';
import type { HistoryRecord, HistoryStats } from '@/types';
import { fetchHistory, fetchHistoryStats, deleteHistoryRecord, clearAllHistory } from '@/api';

const PAGE_SIZE = 20;

interface UseHistoryReturn {
  records: HistoryRecord[];
  stats: HistoryStats | null;
  loading: boolean;
  currentPage: number;
  totalPages: number;
  load: () => Promise<void>;
  deleteRecord: (id: number) => Promise<void>;
  clearAll: () => Promise<void>;
  changePage: (delta: number) => void;
}

export default function useHistory(): UseHistoryReturn {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [stats, setStats] = useState<HistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [historyRes, statsRes] = await Promise.all([
        fetchHistory(PAGE_SIZE, currentPage * PAGE_SIZE),
        fetchHistoryStats(),
      ]);
      setRecords(historyRes.records);
      if (statsRes.success) setStats(statsRes.stats);

      // Calculate pages
      if (statsRes.success) {
        setTotalPages(Math.ceil((statsRes.stats.total || 0) / PAGE_SIZE) || 1);
      }
      if (historyRes.records.length < PAGE_SIZE) {
        setTotalPages(currentPage + 1);
      }
    } finally {
      setLoading(false);
    }
  }, [currentPage]);

  useEffect(() => { load(); }, [load]);

  const deleteRecord = async (id: number) => {
    await deleteHistoryRecord(id);
    await load();
  };

  const clearAll = async () => {
    const count = await clearAllHistory();
    alert(`已删除 ${count} 条记录`);
    setCurrentPage(0);
    await load();
  };

  const changePage = (delta: number) => {
    setCurrentPage(p => Math.max(0, p + delta));
  };

  return { records, stats, loading, currentPage, totalPages, load, deleteRecord, clearAll, changePage };
}
