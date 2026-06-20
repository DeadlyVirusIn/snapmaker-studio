// The frozen v1.0 brand mark as a lightweight inline SVG (Intelligence Layer Asset
// Pack): multi-material colour ribbons flow left → into a glowing transform CORE
// (portal ring) → and emerge as a finished multicolor CUBE. The spectrum is used
// here because this IS the primary mark — one of the only two places (mark +
// status badges) the spectrum is permitted.
export function HeroMark({ className = "" }: { className?: string }) {
  const ribbons = [
    { y: 26, c: "#00E1FF" }, // cyan
    { y: 38, c: "#FF00FF" }, // magenta
    { y: 50, c: "#FFFF00" }, // yellow
    { y: 62, c: "#32CD32" }, // green
    { y: 74, c: "#FF8300" }, // orange
  ];
  return (
    <svg viewBox="0 0 220 100" className={className} role="img" aria-label="Snapmaker Studio mark: ribbons into core into cube" fill="none">
      <defs>
        <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#00E1FF" stopOpacity="0.9" />
          <stop offset="60%" stopColor="#0061FF" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#0061FF" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="cubeGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#00E1FF" />
          <stop offset="50%" stopColor="#8000FF" />
          <stop offset="100%" stopColor="#FF8300" />
        </linearGradient>
      </defs>

      {/* ribbons flowing into the core */}
      {ribbons.map((r, i) => (
        <path key={i}
          d={`M0 ${r.y} C 40 ${r.y}, 60 50, 100 50`}
          stroke={r.c} strokeWidth="3" strokeLinecap="round" opacity="0.9" />
      ))}

      {/* the transform core / portal */}
      <circle cx="110" cy="50" r="30" fill="url(#coreGlow)" />
      <circle cx="110" cy="50" r="22" stroke="#0831FF" strokeWidth="2.5" opacity="0.95" />
      <circle cx="110" cy="50" r="14" stroke="#00E1FF" strokeWidth="1.5" opacity="0.7" />

      {/* the finished multicolor cube emerging */}
      <g transform="translate(150 32)">
        <path d="M20 6 L36 14 L36 32 L20 40 L4 32 L4 14 Z" fill="url(#cubeGrad)" opacity="0.9" />
        <path d="M20 6 L36 14 L20 22 L4 14 Z" fill="#ffffff" opacity="0.25" />
        <path d="M20 22 L20 40 L4 32 L4 14 Z" fill="#000000" opacity="0.15" />
      </g>
    </svg>
  );
}
