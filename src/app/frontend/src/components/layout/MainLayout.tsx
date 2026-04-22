import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { IconMenu } from '../Icons';

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close sidebar on desktop resize
  useEffect(() => {
    const handler = () => {
      if (window.innerWidth > 768) setSidebarOpen(false);
    };
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  return (
    <div className="flex min-h-screen">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-[1000] h-14 bg-white border-b border-[var(--border)] flex items-center px-4.5 gap-3 shadow-sm">
        <button
          onClick={() => setSidebarOpen(true)}
          className="w-9.5 h-9.5 rounded-lg bg-[var(--bg)] border-none cursor-pointer text-primary hover:bg-[var(--primary-bg)] flex items-center justify-center text-xl"
        >
          <IconMenu />
        </button>
        <span className="font-bold text-[15px] text-[var(--text)]">乳腺癌诊断系统</span>
      </div>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[899] md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="flex-1 p-9 md:pl-10 md:pr-10 md:pb-12 pt-12 max-w-[calc(100vw-250px)] min-w-0 md:pt-9 md:mt-0 mt-14">
        <Outlet />
      </main>
    </div>
  );
}
