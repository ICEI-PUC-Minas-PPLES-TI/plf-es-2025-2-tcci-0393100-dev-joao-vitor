import React from "react";

/* Ícones SVG inline (stroke), sem dependências externas.
   Uso: <Icon name="dashboard" /> */

const PATHS = {
  dashboard: <><rect x="3" y="3" width="7" height="9" rx="1.5" /><rect x="14" y="3" width="7" height="5" rx="1.5" /><rect x="14" y="12" width="7" height="9" rx="1.5" /><rect x="3" y="16" width="7" height="5" rx="1.5" /></>,
  kpi: <><path d="M3 3v18h18" /><path d="M7 14l3-4 3 3 4-6" /></>,
  target: <><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="4" /><circle cx="12" cy="12" r="0.6" fill="currentColor" /></>,
  bell: <><path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" /><path d="M10 20a2 2 0 0 0 4 0" /></>,
  upload: <><path d="M12 15V4" /><path d="m7 9 5-5 5 5" /><path d="M5 17v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" /></>,
  report: <><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z" /><path d="M14 3v5h5" /><path d="M9 13h6M9 17h6" /></>,
  robot: <><rect x="4" y="8" width="16" height="11" rx="2.5" /><path d="M12 8V4M9 4h6" /><circle cx="9" cy="13" r="1.1" fill="currentColor" /><circle cx="15" cy="13" r="1.1" fill="currentColor" /></>,
  users: <><circle cx="9" cy="8" r="3.2" /><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5" /><path d="M16 4.5a3.2 3.2 0 0 1 0 7M21 20c0-2.6-1.5-4.5-3.5-5.2" /></>,
  logs: <><rect x="4" y="3" width="16" height="18" rx="2" /><path d="M8 8h8M8 12h8M8 16h5" /></>,
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" /></>,
};

export default function Icon({ name, size = 18, ...rest }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...rest}
    >
      {PATHS[name] || null}
    </svg>
  );
}

/* Marca: monograma "DV" em quadrado com gradiente âmbar */
export function BrandMark({ size = 38 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="dvg" x1="0" y1="0" x2="40" y2="40">
          <stop offset="0" stopColor="#f5b133" />
          <stop offset="1" stopColor="#e07b2e" />
        </linearGradient>
      </defs>
      <rect width="40" height="40" rx="11" fill="url(#dvg)" />
      <path d="M11 12h6.5c4 0 6.5 3 6.5 8s-2.5 8-6.5 8H11V12Z" fill="#1a1205" opacity="0.92" />
      <path d="M25 12.5l3.4 12 3.4-12" stroke="#1a1205" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" opacity="0.92" fill="none" />
    </svg>
  );
}
