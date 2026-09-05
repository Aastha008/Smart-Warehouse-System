import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

export type StatCardVariant = 'blue' | 'rose' | 'emerald' | 'amber' | 'default';

interface MiniBar {
  label: string;
  value: number;
  color?: string;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  subtitle?: string;
  badge?: string;
  badgeType?: 'neutral' | 'success' | 'warning' | 'danger' | 'info';
  trend?: {
    value: number;
    isPositive: boolean;
    label?: string;
  };
  miniBars?: MiniBar[];
  chartHeader?: string;
  onClick?: () => void;
  iconBgClass?: string;
  variant?: StatCardVariant;
}

const cardThemes: Record<
  StatCardVariant,
  {
    container: string;
    divider: string;
    badgeDefault: string;
    barColor: string;
  }
> = {
  blue: {
    container: 'bg-[#F0F5FF] dark:bg-[#131d33] border-[#D9E5FD] dark:border-[#1e2d4d]',
    divider: 'border-[#E1ECFE] dark:border-[#1e2d4d]',
    badgeDefault: 'bg-[#E2ECFF] dark:bg-[#1C2C52] text-[#2557CA] dark:text-[#85A9FF] border-[#C7DBFE] dark:border-[#2a3d66]',
    barColor: 'bg-blue-500',
  },
  rose: {
    container: 'bg-[#FFF0F3] dark:bg-[#2d151c] border-[#FDDCE3] dark:border-[#461e29]',
    divider: 'border-[#FCE3E8] dark:border-[#461e29]',
    badgeDefault: 'bg-[#FFE2E8] dark:bg-[#4E1A27] text-[#CA254B] dark:text-[#FF859F] border-[#FDC2CD] dark:border-[#632233]',
    barColor: 'bg-rose-500',
  },
  emerald: {
    container: 'bg-[#EDFAF3] dark:bg-[#10261c] border-[#D1F2E2] dark:border-[#193d2c]',
    divider: 'border-[#DCF6E9] dark:border-[#193d2c]',
    badgeDefault: 'bg-[#DCF7E9] dark:bg-[#17412E] text-[#168553] dark:text-[#67E2A6] border-[#B7F0D0] dark:border-[#1f543b]',
    barColor: 'bg-emerald-500',
  },
  amber: {
    container: 'bg-[#FFF9EC] dark:bg-[#2b1f11] border-[#FDEBC8] dark:border-[#423018]',
    divider: 'border-[#FCEFD3] dark:border-[#423018]',
    badgeDefault: 'bg-[#DCF7E9] dark:bg-[#17412E] text-[#168553] dark:text-[#67E2A6] border-[#B7F0D0] dark:border-[#1f543b]',
    barColor: 'bg-amber-500',
  },
  default: {
    container: 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700',
    divider: 'border-slate-100 dark:border-slate-700',
    badgeDefault: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700',
    barColor: 'bg-blue-500',
  },
};

export default function StatCard({
  title,
  value,
  icon: Icon,
  subtitle,
  badge,
  badgeType = 'neutral',
  trend,
  miniBars,
  chartHeader,
  onClick,
  iconBgClass,
  variant = 'default',
}: StatCardProps) {
  const maxVal =
    miniBars && miniBars.length > 0 ? Math.max(...miniBars.map((b) => b.value), 1) : 100;
  const theme = cardThemes[variant] || cardThemes.default;

  const getBadgeStyle = () => {
    if (badgeType === 'success') {
      return 'bg-[#DCF7E9] dark:bg-[#17412E] text-[#168553] dark:text-[#67E2A6] border-[#B7F0D0] dark:border-[#1f543b]';
    }
    if (badgeType === 'danger') {
      return 'bg-[#FFE2E8] dark:bg-[#4E1A27] text-[#CA254B] dark:text-[#FF859F] border-[#FDC2CD] dark:border-[#632233]';
    }
    if (badgeType === 'info') {
      return 'bg-[#E2ECFF] dark:bg-[#1C2C52] text-[#2557CA] dark:text-[#85A9FF] border-[#C7DBFE] dark:border-[#2a3d66]';
    }
    if (badgeType === 'warning') {
      return 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800';
    }
    return theme.badgeDefault;
  };

  // Support splitting "6/6 Live" into two lines
  const stringVal = String(value);
  const isSplitValue = stringVal.includes(' ') && !stringVal.includes('%');
  const [valPrimary, valSecondary] = isSplitValue ? stringVal.split(' ') : [stringVal, null];

  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border ${theme.container} p-5 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between h-full min-h-[175px] ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {/* 1. Header: Title, Badge, and Chart Header */}
      <div className="flex items-center justify-between gap-1 mb-2">
        <span className="text-xs font-bold text-slate-800 dark:text-slate-100 whitespace-nowrap">
          {title}
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {badge && (
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getBadgeStyle()}`}
            >
              {badge}
            </span>
          )}
          {chartHeader && (
            <span className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              {chartHeader}
            </span>
          )}
        </div>
      </div>

      {/* 2. Middle Section: Metric & Micro-Bars */}
      <div className="flex items-end justify-between gap-2 my-auto">
        <div className="min-w-0 flex-1">
          {valSecondary ? (
            <div className="leading-tight">
              <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight block">
                {valPrimary}
              </span>
              <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight block -mt-1">
                {valSecondary}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight leading-none">
                {value}
              </span>
              {trend && (
                <span
                  className={`inline-flex items-center gap-0.5 text-[11px] font-bold px-1.5 py-0.5 rounded-md shrink-0 ${
                    trend.isPositive
                      ? 'bg-[#DCF7E9] dark:bg-[#17412E] text-[#168553] dark:text-[#67E2A6]'
                      : 'bg-[#FFE2E8] dark:bg-[#4E1A27] text-[#CA254B] dark:text-[#FF859F]'
                  }`}
                >
                  {trend.isPositive ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  {trend.isPositive ? '+' : '-'}
                  {Math.abs(trend.value)}%
                </span>
              )}
            </div>
          )}

          {subtitle && (
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-1 leading-snug">
              {subtitle}
            </p>
          )}
        </div>

        {/* Micro Bar Sparkline or Icon */}
        {miniBars && miniBars.length > 0 ? (
          <div className="flex items-end gap-2 shrink-0 pl-1">
            {miniBars.map((bar, idx) => {
              const heightPct = Math.max(22, Math.round((bar.value / maxVal) * 100));
              const barColor = bar.color || theme.barColor;
              return (
                <div key={idx} className="flex flex-col items-center gap-1">
                  <div className="w-2.5 sm:w-3 h-10 rounded-full flex items-end overflow-hidden">
                    <div
                      className={`w-full rounded-full transition-all duration-500 ${barColor}`}
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                  <span className="text-[9px] font-semibold text-slate-400 dark:text-slate-500 text-center whitespace-nowrap">
                    {bar.label}
                  </span>
                </div>
              );
            })}
          </div>
        ) : Icon ? (
          <div className="shrink-0">
            <div
              className={`w-9 h-9 rounded-lg border flex items-center justify-center ${
                iconBgClass ||
                'bg-slate-50 dark:bg-slate-700/50 border-slate-200 dark:border-slate-700 text-blue-600 dark:text-blue-400'
              }`}
            >
              <Icon className="w-4 h-4" />
            </div>
          </div>
        ) : null}
      </div>

      {/* 3. Footer Context Row */}
      <div
        className={`pt-2 mt-2 border-t ${theme.divider} flex items-center justify-between text-[11px] text-slate-400 dark:text-slate-500`}
      >
        <span className="truncate mr-2 font-medium">
          {trend?.label || 'Dock bays streaming'}
        </span>
        <span className="text-[10px] font-mono font-medium shrink-0">
          Dock Feed
        </span>
      </div>
    </div>
  );
}
