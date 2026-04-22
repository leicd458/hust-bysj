import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { IconDiagnosis, IconHistory, IconLogo } from '../Icons';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const navItems = [
    { to: '/', label: '智能诊断', icon: <IconDiagnosis /> },
    { to: '/history', label: '历史记录', icon: <IconHistory /> },
  ];

  const handleNavClick = () => {
    if (window.innerWidth <= 768) onClose();
  };

  return (
    <aside
      className={`sidebar-gradient fixed md:sticky top-0 left-0 h-screen w-[250px] md:w-auto flex flex-col z-[999] md:z-auto transition-transform duration-300 ${open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}
      style={{ width: window.innerWidth <= 768 ? '280px' : '250px' }}
    >
      <div className="flex flex-col h-full px-4 py-7 flex-1">
        {/* Brand */}
        <div className="flex items-center gap-3.5 px-1 pb-6 mb-2 border-b border-white/12">
          <div className="w-11 h-11 rounded-xl bg-white/15 flex items-center justify-center flex-shrink-0">
            <IconLogo />
          </div>
          <div>
            <h1 className="text-base font-bold text-white leading-tight">诊断系统</h1>
            <p className="text-xs text-white/55 mt-0.5 tracking-wide">Breast Diagnosis AI</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1 py-4 flex-1">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={handleNavClick}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl no-underline transition-all duration-200 text-sm font-medium ${
                  isActive
                    ? 'bg-white/95 text-primary-dark shadow-md'
                    : 'text-white/70 hover:bg-white/12 hover:text-white'
                }`
              }
            >
              <span className="w-[22px] flex items-center justify-center opacity-85">{item.icon}</span>
              <span className="whitespace-nowrap">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="mt-auto pt-4 border-t border-white/12">
          <div className="flex items-center gap-2 px-3.5 py-2 bg-white/9 rounded-lg mb-2.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,.6)] animate-pulse-dot" />
            <span className="text-xs text-white/75 font-medium">系统运行中</span>
          </div>
          <p className="text-xs text-white/35 text-center">&copy; 2026 HUST 毕业设计</p>
        </div>
      </div>
    </aside>
  );
}
