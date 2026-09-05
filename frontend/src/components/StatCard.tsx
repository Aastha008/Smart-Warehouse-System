import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

export type StatCardVariant = 'blue' | 'rose' | 'emerald' | 'amber' | 'purple' | 'default';

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
  colorClass?: string;
  variant?: StatCardVariant;
}

const variantTheme: Record<
  StatCardVariant,
  {
    topBorder: string;
    badgeDefault: string;
    barDefault: string;
  }
> = {
  blue: {
    topBorder: 'border-t-blue-500',
    badgeDefault: 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    barDefault: 'bg-blue-500',
  },
  rose: {
    topBorder: 'border-t-rose-500',
    badgeDefault: 'bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800',
    barDefault: 'bg-rose-500',
  },
  emerald: {
    topBorder: 'border-t-emerald-500',
    badgeDefault: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
    barDefault: 'bg-emerald-500',
  },
  amber: {
    topBorder: 'border-t-amber-500',
    badgeDefault: 'bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800',
    barDefault: 'bg-amber-500',
  },
  purple: {
    topBorder: 'border-t-purple-500',
    badgeDefault: 'bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800',
    barDefault: 'bg-purple-500',
  },
  default: {
    topBorder: 'border-t-slate-400',
    badgeDefault: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700',
    barDefault: 'bg-slate-500',
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
  const theme = variantTheme[variant] || variantTheme.default;

  const getBadgeStyle = () => {
    if (badgeType === 'success') {
      return 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800';
    }
    if (badgeType === 'warning') {
      return 'bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800';
    }
    if (badgeType === 'danger') {
      return 'bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800';
    }
    if (badgeType === 'info') {
      return 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800';
    }
    return theme.badgeDefault;
  };

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-slate-800/95 border border-slate-200/90 dark:border-slate-700/80 border-t-2 ${theme.topBorder} rounded-xl p-5 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between h-full min-h-[175px] ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {/* 1. Top Header Row: Clean full title & status pill */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {title}
        </span>
        {badge && (
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border shrink-0 ${getBadgeStyle()}`}
          >
            {badge}
          </span>
        )}
      </div>

      {/* 2. Middle Row: Bold metric with subtitle & sparkline microbars */}
      <div className="flex items-end justify-between gap-3 my-auto">
        <div className="min-w-0 flex-1">
          <div className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white leading-none">
            {value}
          </div>
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1.5 leading-snug">
              {subtitle}
            </p>
          )}
        </div>

        {/* Micro Bar Sparkline or Icon */}
        {miniBars && miniBars.length > 0 ? (
          <div className="flex items-end gap-1.5 shrink-0 pl-3">
            {miniBars.map((bar, idx) => {
              const heightPct = Math.max(18, Math.round((bar.value / maxVal) * 100));
              const barColor = bar.color || theme.barDefault;
              return (
                <div key={idx} className="flex flex-col items-center w-5 gap-1">
                  <div className="w-2.5 h-10 rounded-full bg-slate-100 dark:bg-slate-700/60 flex items-end overflow-hidden">
                    <div
                      className={`w-full rounded-full transition-all duration-500 ${barColor}`}
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                  <span className="text-[9px] font-semibold text-slate-400 dark:text-slate-500 text-center truncate w-full">
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

      {/* 3. Bottom Footer Row: Standardized across all 4 cards for perfect alignment */}
      <div className="pt-2.5 mt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs">
        {trend ? (
          <div className="flex items-center gap-1.5 min-w-0">
            <span
              className={`inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-md shrink-0 ${
                trend.isPositive
                  ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200/80 dark:border-emerald-800/80'
                  : 'bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200/80 dark:border-rose-800/80'
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
            {trend.label && (
              <span className="text-slate-500 dark:text-slate-400 text-[11px] font-medium truncate">
                {trend.label}
              </span>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-500 dark:text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
            <span>Telemetry active</span>
          </div>
        )}

        <span className="text-[10px] font-mono font-medium text-slate-400 dark:text-slate-500 shrink-0 ml-2">
          Dock Feed
        </span>
      </div>
    </div>
  );
}

