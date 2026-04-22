import React from 'react';

// ==================== SVG Icons ====================

export function IconDiagnosis() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>
    </svg>
  );
}

export function IconHistory() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/>
    </svg>
  );
}

export function IconMenu() {
  return (
    <span className="text-xl">&#9776;</span>
  );
}

export function IconLogo() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="10" fill="rgba(255,255,255,.15)"/>
      <path d="M16 6C12 6 9 9 8 13c-.5 2 .5 4 1.5 5.5C11 20.5 14 24 16 26c2-2 5-5.5 6.5-7.5 1-1.5 2-3.5 1.5-5.5-1-4-4-7-8-7z" fill="white" opacity=".95"/>
      <circle cx="16" cy="14" r="3.5" fill="#0e7490"/>
    </svg>
  );
}
