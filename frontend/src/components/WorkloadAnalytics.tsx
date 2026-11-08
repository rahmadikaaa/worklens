import React, { useState, useEffect } from 'react';
import { motion, type Variants } from 'framer-motion';
import {
  Clock,
  Cpu,
  Percent,
  TrendingDown,
  TrendingUp,
  Workflow,
} from 'lucide-react';
import type { ActivitySummaryMetrics } from '../types';
import { KpiCard, AnimatedProgressBar, SkeletonCard } from './motion/MotionPrimitives';
import { AnimatedBarChart, BarItem } from './motion/AnimatedBarChart';

interface WorkloadAnalyticsProps {
  onNavigateToTab?: (tab: string, filter?: Record<string, string>) => void;
}

export const WorkloadAnalytics: React.FC<WorkloadAnalyticsProps> = ({ onNavigateToTab }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<ActivitySummaryMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      setLoading(true);
      try {
        const res = await fetch('/api/v1/activities/summary');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setSummary(data.summary);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to fetch summary');
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  const topAppBars: BarItem[] = React.useMemo(() => {
    if (!summary?.distribution_top_applications) return [];
    return Object.entries(summary.distribution_top_applications).map(([app, count], idx) => ({
      id: app,
      label: app,
      value: count,
      color: idx % 2 === 0 ? '#10b981' : '#0ea5e9',
      tooltipText: `${count} total activities in this application`,
    }));
  }, [summary]);

  const categoryActionBars: BarItem[] = React.useMemo(() => {
    if (!summary?.distribution_category_action) return [];
    return Object.entries(summary.distribution_category_action).map(([action, count], idx) => ({
      id: action,
      label: action,
      value: count,
      color: idx % 2 === 0 ? '#818cf8' : '#f59e0b',
      tooltipText: `${count} operational tasks`,
    }));
  }, [summary]);

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0, transition: { duration: 0.28, ease: 'easeOut' } },
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="p-8 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
        Failed to load workload analytics: {error || 'No data'}
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Initial Workload"
          value={Math.round(summary.total_workload_before_min / 60.0)}
          suffix=" hrs/mo"
          subtitle={`${summary.total_workload_before_min.toLocaleString()} minutes total`}
          icon={<Clock className="h-5 w-5" />}
          variant="sky"
          trendText="Baseline"
          trendType="neutral"
        />

        <KpiCard
          title="Residual Workload"
          value={Math.round(summary.total_workload_after_min / 60.0)}
          suffix=" hrs/mo"
          subtitle={`${summary.total_workload_after_min.toLocaleString()} minutes after`}
          icon={<TrendingDown className="h-5 w-5" />}
          variant="purple"
          trendText="Post-Automation"
          trendType="neutral"
        />

        <KpiCard
          title="Total Workload Saved"
          value={summary.total_workload_saved_hours}
          decimals={1}
          suffix=" hrs/mo"
          subtitle={`${summary.total_workload_saved_min.toLocaleString()} minutes saved`}
          icon={<TrendingUp className="h-5 w-5" />}
          variant="emerald"
          trendText="M1 Calculated"
          trendType="positive"
        />

        <KpiCard
          title="Overall Reduction"
          value={summary.overall_reduction_pct}
          decimals={1}
          suffix="%"
          subtitle="Net operational reduction"
          icon={<Percent className="h-5 w-5" />}
          variant="indigo"
          trendText="Empirical"
          trendType="positive"
        />
      </div>

      {/* Workload Progress Comparison Bar */}
      <motion.div
        variants={itemVariants}
        className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur space-y-4"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
              <TrendingDown className="h-4 w-4 text-emerald-400" />
              <span>Operational Workload Reduction Progress</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparison between total initial workload before automation vs workload eliminated
            </p>
          </div>
          <span className="text-xs font-mono font-bold text-emerald-400">
            {summary.overall_reduction_pct}% Workload Saved
          </span>
        </div>

        <AnimatedProgressBar
          value={summary.total_workload_saved_min}
          max={summary.total_workload_before_min > 0 ? summary.total_workload_before_min : 100}
          color="emerald"
          labelPrefix="Workload Savings vs Baseline"
          heightClass="h-3.5"
        />

        <div className="flex justify-between items-center text-xs text-slate-400 pt-2 border-t border-slate-800/80">
          <span>
            Initial Baseline:{' '}
            <strong className="text-white font-mono">
              {(summary.total_workload_before_min / 60).toFixed(1)} hrs/mo
            </strong>
          </span>
          <span>
            Saved:{' '}
            <strong className="text-emerald-400 font-mono">
              {summary.total_workload_saved_hours} hrs/mo
            </strong>
          </span>
          <span>
            Residual:{' '}
            <strong className="text-slate-300 font-mono">
              {(summary.total_workload_after_min / 60).toFixed(1)} hrs/mo
            </strong>
          </span>
        </div>
      </motion.div>

      {/* Two Column Charts: Top Applications & Category Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Applications Bar Chart */}
        <motion.div
          variants={itemVariants}
          className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur space-y-4"
        >
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
                <Cpu className="h-4 w-4 text-sky-400" />
                <span>Top Applications by Workload Volume</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Core applications driving L1 operational interventions
              </p>
            </div>
          </div>

          <AnimatedBarChart
            data={topAppBars}
            valueSuffix="tasks"
            onBarClick={(item) =>
              onNavigateToTab && onNavigateToTab('activities', { app: item.label })
            }
          />
        </motion.div>

        {/* Category Actions Bar Chart */}
        <motion.div
          variants={itemVariants}
          className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur space-y-4"
        >
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
                <Workflow className="h-4 w-4 text-indigo-400" />
                <span>Category Actions Breakdown</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Distribution across canonical operational action classes
              </p>
            </div>
          </div>

          <AnimatedBarChart
            data={categoryActionBars}
            valueSuffix="tasks"
            onBarClick={(item) =>
              onNavigateToTab && onNavigateToTab('activities', { category_action: item.label })
            }
          />
        </motion.div>
      </div>
    </motion.div>
  );
};
