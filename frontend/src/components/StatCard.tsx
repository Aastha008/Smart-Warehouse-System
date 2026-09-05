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

const variantStyles: Record<
  StatCardVariant,
  {
    container: string;
    divider: string;
    title: string;
    value: string;
    subtitle: string;
    chartHeader: string;
    trackBg: string;
    badgeDefault: string;
  }
> = {
  blue: {
    container:
      'bg-[#F0F5FF] dark:bg-[#141C33] border-[#D9E5FD] dark:border-[#223154] hover:border-[#BFD3FB] dark:hover:border-[#32487A] shadow-xs hover:shadow-md hover:shadow-blue-500/5',
    divider: 'border-[#E1ECFE] dark:border-[#1E2B4A]',
    title: 'text-[#2B4375] dark:text-[#A8C5FD]',
    value: 'text-[#111C38] dark:text-white',
    subtitle: 'text-[#5A6F98] dark:text-[#8BA4D6]',
    chartHeader: 'text-[#7E93BE] dark:text-[#6C85B5]',
    trackBg: 'bg-[#DCE7FC] dark:bg-[#1A2542]',
    badgeDefault:
      'bg-[#E2ECFF] dark:bg-[#1C2C52] text-[#2557CA] dark:text-[#85A9FF] border-blue-200/80 dark:border-blue-800/80',
  },
  rose: {
    container:
      'bg-[#FFF0F3] dark:bg-[#30161F] border-[#FDDCE3] dark:border-[#4F222F] hover:border-[#FBBECB] dark:hover:border-[#6E2E3F] shadow-xs hover:shadow-md hover:shadow-rose-500/5',
    divider: 'border-[#FCE3E8] dark:border-[#441C28]',
    title: 'text-[#752B3C] dark:text-[#FDA8BA]',
    value: 'text-[#38111B] dark:text-white',
    subtitle: 'text-[#985A68] dark:text-[#D68B9C]',
    chartHeader: 'text-[#BE7E8D] dark:text-[#B56C7E]',
    trackBg: 'bg-[#FCDCE2] dark:bg-[#3D1822]',
    badgeDefault:
      'bg-[#FFE2E8] dark:bg-[#4E1A27] text-[#CA254B] dark:text-[#FF859F] border-rose-200/80 dark:border-rose-800/80',
  },
  emerald: {
    container:
      'bg-[#EDFAF3] dark:bg-[#11291F] border-[#D1F2E2] dark:border-[#1D4634] hover:border-[#A8E6C8] dark:hover:border-[#265F45] shadow-xs hover:shadow-md hover:shadow-emerald-500/5',
    divider: 'border-[#DCF6E9] dark:border-[#173829]',
    title: 'text-[#236348] dark:text-[#8EE6BE]',
    value: 'text-[#0C2A1E] dark:text-white',
    subtitle: 'text-[#49866B] dark:text-[#72BFA0]',
    chartHeader: 'text-[#69A88C] dark:text-[#529E7D]',
    trackBg: 'bg-[#D3F3E3] dark:bg-[#153A2A]',
    badgeDefault:
      'bg-[#DCF7E9] dark:bg-[#17412E] text-[#168553] dark:text-[#67E2A6] border-emerald-200/80 dark:border-emerald-800/80',
  },
  amber: {
    container:
      'bg-[#FFF9EC] dark:bg-[#302212] border-[#FDEBC8] dark:border-[#4E371B] hover:border-[#FCDA95] dark:hover:border-[#6E4D23] shadow-xs hover:shadow-md hover:shadow-amber-500/5',
    divider: 'border-[#FCEFD3] dark:border-[#432F16]',
    title: 'text-[#755223] dark:text-[#FDD08E]',
    value: 'text-[#38240A] dark:text-white',
    subtitle: 'text-[#987545] dark:text-[#D6AE74]',
    chartHeader: 'text-[#BE9864] dark:text-[#B58D52]',
    trackBg: 'bg-[#FCEAC5] dark:bg-[#3D2B15]',
    badgeDefault:
      'bg-[#FFF0CF] dark:bg-[#4E3618] text-[#B87014] dark:text-[#FFC773] border-amber-200/80 dark:border-amber-800/80',
  },
  purple: {
    container:
      'bg-[#F8F2FF] dark:bg-[#231538] border-[#ECD8FF] dark:border-[#3F2263] hover:border-[#DCB8FF] dark:hover:border-[#592F8D] shadow-xs hover:shadow-md hover:shadow-purple-500/5',
    divider: 'border-[#F2E2FF] dark:border-[#341B50]',
    title: 'text-[#552786] dark:text-[#D9B8FD]',
    value: 'text-[#250F3E] dark:text-white',
    subtitle: 'text-[#7950A7] dark:text-[#B48FDF]',
    chartHeader: 'text-[#9A74C4] dark:text-[#9A73C9]',
    trackBg: 'bg-[#EBD6FF] dark:bg-[#30194B]',
    badgeDefault:
      'bg-[#F1E0FF] dark:bg-[#3C1B60] text-[#7C27D2] dark:text-[#D59BFF] border-purple-200/80 dark:border-purple-800/80',
  },
  default: {
    container:
      'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md',
    divider: 'border-slate-100 dark:border-slate-800',
    title: 'text-slate-800 dark:text-slate-200',
    value: 'text-slate-900 dark:text-white',
    subtitle: 'text-slate-500 dark:text-slate-400',
    chartHeader: 'text-slate-400 dark:text-slate-500',
    trackBg: 'bg-slate-100 dark:bg-slate-800',
    badgeDefault:
      'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700',
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
  colorClass,
  variant = 'default',
}: StatCardProps) {
  const maxVal =
    miniBars && miniBars.length > 0 ? Math.max(...miniBars.map((b) => b.value), 1) : 100;
  const styles = variantStyles[variant] || variantStyles.default;

  const getBadgeStyle = () => {
    if (badgeType === 'success') {
      return 'bg-emerald-100/80 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200/80 dark:border-emerald-800';
    }
    if (badgeType === 'warning') {
      return 'bg-amber-100/80 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200/80 dark:border-amber-800';
    }
    if (badgeType === 'danger') {
      return 'bg-rose-100/80 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border-rose-200/80 dark:border-rose-800';
    }
    if (badgeType === 'info') {
      return 'bg-blue-100/80 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-200/80 dark:border-blue-800';
    }
    return styles.badgeDefault;
  };

  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border transition-all duration-200 p-5 flex flex-col justify-between relative overflow-hidden group ${styles.container} ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {/* Top Header Row */}
      <div className={`flex items-center justify-between pb-2 mb-2 border-b ${styles.divider}`}>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold tracking-tight ${styles.title}`}>{title}</span>
          {badge && (
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getBadgeStyle()}`}
            >
              {badge}
            </span>
          )}
        </div>
        {chartHeader && (
          <span className={`text-[11px] font-semibold ${styles.chartHeader}`}>{chartHeader}</span>
        )}
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
        {/* Left Side: Numeric Value & Delta */}
        <div className={miniBars && miniBars.length > 0 ? 'sm:col-span-7' : 'sm:col-span-12'}>
          <div className="flex items-baseline gap-2">
            <h3 className={`text-2xl lg:text-3xl font-black tracking-tight ${styles.value}`}>
              {value}
            </h3>
            {trend && (
              <span
                className={`inline-flex items-center gap-0.5 text-xs font-bold px-1.5 py-0.5 rounded-md ${
                  trend.isPositive
                    ? 'bg-emerald-100/70 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400'
                    : 'bg-rose-100/70 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400'
                }`}
              >
                {trend.isPositive ? (
                  <TrendingUp className="w-3.5 h-3.5" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5" />
                )}
                {trend.isPositive ? '+' : '-'}
                {Math.abs(trend.value)}%
              </span>
            )}
          </div>
          {subtitle && (
            <p className={`text-[11px] mt-1 font-medium ${styles.subtitle}`}>{subtitle}</p>
          )}
        </div>

        {/* Right Side: Micro Bar Chart (Reference Design Style) */}
        {miniBars && miniBars.length > 0 ? (
          <div className="sm:col-span-5 flex items-end justify-end gap-2 h-14 pt-1">
            {miniBars.map((bar, idx) => {
              const heightPct = Math.max(15, Math.round((bar.value / maxVal) * 100));
              const barColor =
                bar.color ||
                (idx === 0
                  ? 'bg-indigo-300'
                  : idx === 1
                  ? 'bg-sky-300'
                  : 'bg-amber-300');
              return (
                <div key={idx} className="flex flex-col items-center gap-1">
                  <div
                    className={`w-3.5 rounded-md h-10 flex items-end overflow-hidden ${styles.trackBg}`}
                  >
                    <div
                      className={`w-full rounded-md transition-all duration-500 ${barColor}`}
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                  <span className={`text-[9px] font-medium ${styles.chartHeader}`}>
                    {bar.label}
                  </span>
                </div>
              );
            })}
          </div>
        ) : Icon ? (
          <div className="hidden sm:flex justify-end items-center sm:col-span-12">
            <div
              className={`w-9 h-9 rounded-xl border flex items-center justify-center shadow-2xs ${
                iconBgClass ||
                'bg-slate-50 dark:bg-slate-800 border-slate-200/80 dark:border-slate-700 text-blue-600 dark:text-blue-400'
              }`}
            >
              <Icon className="w-4 h-4" />
            </div>
          </div>
        ) : null}
      </div>

      {/* Footer Trend Context */}
      {trend?.label && (
        <div
          className={`mt-3 pt-2 border-t ${styles.divider} flex items-center justify-between text-[11px] ${styles.chartHeader}`}
        >
          <span>{trend.label}</span>
          <span className="text-[10px] font-mono opacity-80">Dock Feed</span>
        </div>
      )}
    </div>
  );
}

