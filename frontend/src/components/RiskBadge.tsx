import React from 'react';
import { RiskLevel } from '../types';

interface RiskBadgeProps {
  level?: RiskLevel | string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function RiskBadge({ level = 'LOW', className = '', size = 'sm' }: RiskBadgeProps) {
  const normLevel = (level || 'LOW').toUpperCase() as RiskLevel;

  const styleMap: Record<RiskLevel, { bg: string; text: string; border: string; dot: string }> = {
    LOW: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-700',
      border: 'border-emerald-300',
      dot: 'bg-emerald-500',
    },
    MEDIUM: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-700',
      border: 'border-amber-300',
      dot: 'bg-amber-500',
    },
    HIGH: {
      bg: 'bg-orange-500/10',
      text: 'text-orange-700',
      border: 'border-orange-300',
      dot: 'bg-orange-500',
    },
    CRITICAL: {
      bg: 'bg-red-500/10',
      text: 'text-red-700',
      border: 'border-red-300',
      dot: 'bg-red-500',
    },
  };

  const style = styleMap[normLevel] || styleMap.LOW;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[11px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-bold uppercase tracking-wider rounded-full border shadow-2xs ${style.bg} ${style.text} ${style.border} ${sizeClasses} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot} ${normLevel === 'CRITICAL' ? 'animate-ping' : ''}`} />
      {normLevel}
    </span>
  );
}
