import React, { useState } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle() {
  const { theme, resolvedTheme, cycleTheme } = useTheme();
  const [showTooltip, setShowTooltip] = useState(false);

  // Icon shape is ALWAYS Sun or Moon:
  // - If light mode: Sun
  // - If dark mode: Moon
  // - In system default: whichever mode is chosen by the OS (Sun if light, Moon if dark)
  const isDarkShape = resolvedTheme === 'dark';

  const themeLabel =
    theme === 'system'
      ? `System (${isDarkShape ? 'Dark' : 'Light'})`
      : theme === 'dark'
      ? 'Dark Mode'
      : 'Light Mode';

  const nextModeLabel =
    theme === 'light' ? 'Dark Mode' : theme === 'dark' ? 'System Default' : 'Light Mode';

  return (
    <div className="relative">
      <button
        onClick={() => {
          cycleTheme();
          setShowTooltip(true);
          setTimeout(() => setShowTooltip(false), 1800);
        }}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/15 flex items-center justify-center text-white text-xs transition-all shadow-xs relative active:scale-95 group"
        title={`Current: ${themeLabel} • Click for ${nextModeLabel}`}
        aria-label="Toggle theme mode"
      >
        {isDarkShape ? (
          <Moon className="w-3.5 h-3.5 text-amber-300 fill-amber-300/20 transition-transform group-hover:-rotate-12 duration-200" />
        ) : (
          <Sun className="w-3.5 h-3.5 text-amber-300 fill-amber-300/30 transition-transform group-hover:rotate-45 duration-200" />
        )}

        {/* Small "A" (Auto) badge only when in System Default */}
        {theme === 'system' && (
          <span className="absolute -bottom-1 -right-1 px-1 py-0.2 bg-purple-950/90 text-purple-200 text-[8px] font-black rounded-full border border-purple-400/50 leading-tight">
            A
          </span>
        )}
      </button>

      {/* Floating Mode Feedback Badge */}
      {showTooltip && (
        <div className="absolute top-10 right-0 px-2.5 py-1 bg-slate-900/95 backdrop-blur-md text-white border border-slate-700/80 rounded-xl text-[10px] font-bold whitespace-nowrap shadow-xl z-50 pointer-events-none animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>{themeLabel}</span>
          </div>
        </div>
      )}
    </div>
  );
}
