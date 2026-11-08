import React from 'react';
import { motion } from 'framer-motion';
import { useCountUp } from '../../hooks/useMotion';

interface AnimatedNumberProps {
  value: number;
  decimals?: number;
  durationMs?: number;
  prefix?: string;
  suffix?: string;
  formatter?: (val: number) => string;
}

export const AnimatedNumber: React.FC<AnimatedNumberProps> = ({
  value,
  decimals = 0,
  durationMs = 1000,
  prefix = '',
  suffix = '',
  formatter,
}) => {
  const animatedVal = useCountUp(value, durationMs, decimals);

  const formatted = formatter
    ? formatter(animatedVal)
    : decimals > 0
    ? animatedVal.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    : animatedVal.toLocaleString('en-US');

  return (
    <span>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
};

interface KpiCardProps {
  title: string;
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  trendText?: string;
  trendType?: 'positive' | 'warning' | 'neutral' | 'negative';
  variant?: 'sky' | 'emerald' | 'amber' | 'rose' | 'indigo' | 'purple';
  onClick?: () => void;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  decimals = 0,
  prefix = '',
  suffix = '',
  subtitle,
  icon,
  trendText,
  trendType = 'neutral',
  variant = 'sky',
  onClick,
}) => {
  const variantStyles = {
    sky: {
      borderHover: 'hover:border-sky-500/40 hover:shadow-sky-500/10',
      iconBg: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
      glow: 'group-hover:bg-sky-500/5',
    },
    emerald: {
      borderHover: 'hover:border-emerald-500/40 hover:shadow-emerald-500/10',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      glow: 'group-hover:bg-emerald-500/5',
    },
    amber: {
      borderHover: 'hover:border-amber-500/40 hover:shadow-amber-500/10',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      glow: 'group-hover:bg-amber-500/5',
    },
    rose: {
      borderHover: 'hover:border-rose-500/40 hover:shadow-rose-500/10',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      glow: 'group-hover:bg-rose-500/5',
    },
    indigo: {
      borderHover: 'hover:border-indigo-500/40 hover:shadow-indigo-500/10',
      iconBg: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
      glow: 'group-hover:bg-indigo-500/5',
    },
    purple: {
      borderHover: 'hover:border-purple-500/40 hover:shadow-purple-500/10',
      iconBg: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      glow: 'group-hover:bg-purple-500/5',
    },
  };

  const trendStyles = {
    positive: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    negative: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    neutral: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  const style = variantStyles[variant];

  return (
    <motion.div
      whileHover={{ y: -3, transition: { duration: 0.18, ease: 'easeOut' } }}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      onClick={onClick}
      className={`group relative rounded-xl border border-slate-800 bg-slate-950/70 p-5 shadow-sm transition-all duration-200 backdrop-blur ${
        style.borderHover
      } ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</p>
          <div className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-baseline">
            <AnimatedNumber
              value={value}
              decimals={decimals}
              prefix={prefix}
              suffix={suffix}
              durationMs={900}
            />
          </div>
        </div>
        {icon && (
          <div
            className={`h-9 w-9 rounded-lg flex items-center justify-center border transition-transform duration-200 group-hover:scale-105 ${style.iconBg}`}
          >
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between text-xs">
        {subtitle && <p className="text-slate-400 truncate max-w-[180px]">{subtitle}</p>}
        {trendText && (
          <span
            className={`ml-auto inline-flex items-center px-2 py-0.5 rounded-full border text-[11px] font-medium ${trendStyles[trendType]}`}
          >
            {trendText}
          </span>
        )}
      </div>
    </motion.div>
  );
};

interface AnimatedProgressBarProps {
  value: number;
  max?: number;
  color?: 'emerald' | 'sky' | 'indigo' | 'amber' | 'rose';
  showLabel?: boolean;
  labelPrefix?: string;
  heightClass?: string;
}

export const AnimatedProgressBar: React.FC<AnimatedProgressBarProps> = ({
  value,
  max = 100,
  color = 'sky',
  showLabel = true,
  labelPrefix = '',
  heightClass = 'h-2',
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const colorVariants = {
    emerald: 'bg-emerald-500',
    sky: 'bg-sky-500',
    indigo: 'bg-indigo-500',
    amber: 'bg-amber-500',
    rose: 'bg-rose-500',
  };

  return (
    <div className="w-full space-y-1.5">
      {showLabel && (
        <div className="flex justify-between text-xs font-medium text-slate-400">
          <span>{labelPrefix}</span>
          <span className="font-mono text-slate-200">{percentage.toFixed(1)}%</span>
        </div>
      )}
      <div className={`w-full rounded-full bg-slate-800 overflow-hidden ${heightClass}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${colorVariants[color]}`}
        />
      </div>
    </div>
  );
};

interface AnimatedBadgeProps {
  status: string;
  variant?: 'emerald' | 'sky' | 'amber' | 'rose' | 'slate' | 'indigo';
  pulse?: boolean;
}

export const AnimatedBadge: React.FC<AnimatedBadgeProps> = ({
  status,
  variant = 'slate',
  pulse = false,
}) => {
  const badgeColors = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    sky: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    slate: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  const dotColors = {
    emerald: 'bg-emerald-400',
    sky: 'bg-sky-400',
    amber: 'bg-amber-400',
    rose: 'bg-rose-400',
    indigo: 'bg-indigo-400',
    slate: 'bg-slate-400',
  };

  return (
    <motion.span
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${badgeColors[variant]}`}
    >
      <span className="relative flex h-1.5 w-1.5">
        {pulse && (
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotColors[variant]}`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${dotColors[variant]}`} />
      </span>
      <span>{status}</span>
    </motion.span>
  );
};

export const SkeletonRow: React.FC<{ columns?: number }> = ({ columns = 6 }) => {
  return (
    <tr className="animate-pulse border-b border-slate-800/60">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="py-3.5 px-4">
          <div className="h-4 bg-slate-800 rounded w-3/4" />
        </td>
      ))}
    </tr>
  );
};

export const SkeletonCard: React.FC = () => {
  return (
    <div className="animate-pulse rounded-xl border border-slate-800 bg-slate-950/40 p-5 space-y-3">
      <div className="h-3 bg-slate-800 rounded w-1/3" />
      <div className="h-8 bg-slate-800/80 rounded w-1/2" />
      <div className="h-3 bg-slate-800/50 rounded w-2/3" />
    </div>
  );
};

