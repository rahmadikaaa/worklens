import React, { useState, useEffect } from 'react';
import { motion, type Variants } from 'framer-motion';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  FileQuestion,
  HelpCircle,
  Link2,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';
import type { ActivitySummaryMetrics } from '../types';
import { KpiCard, SkeletonCard } from './motion/MotionPrimitives';
import { AnimatedDonutChart, DonutSegment } from './motion/AnimatedDonutChart';

interface DataQualityProps {
  onNavigateToTab?: (tab: string, filter?: Record<string, string>) => void;
}

export const DataQualityReconciliation: React.FC<DataQualityProps> = ({ onNavigateToTab }) => {
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

  const calcStatusSegments: DonutSegment[] = React.useMemo(() => {
    if (!summary?.distribution_calculation_status) return [];
    const colors: Record<string, string> = {
      CALCULATED: '#10b981',
      ZERO_WORKLOAD: '#0ea5e9',
      INVALID_INPUT: '#f59e0b',
      MISSING_INPUT: '#f43f5e',
      NEGATIVE_INPUT: '#e11d48',
      NEGATIVE_SAVINGS: '#fbbf24',
    };
    return Object.entries(summary.distribution_calculation_status).map(([st, count]) => ({
      id: st,
      label: st,
      value: count,
      color: colors[st] || '#64748b',
    }));
  }, [summary]);

  const evidenceSegments: DonutSegment[] = React.useMemo(() => {
    if (!summary?.distribution_evidence) return [];
    return [
      {
        id: 'LINK_PROVIDED',
        label: 'Link Provided',
        value: summary.distribution_evidence.LINK_PROVIDED || 0,
        color: '#10b981',
      },
      {
        id: 'NO_LINK_ATTACHED',
        label: 'No Link Attached',
        value: summary.distribution_evidence.NO_LINK_ATTACHED || 0,
        color: '#f43f5e',
      },
    ];
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
        Failed to load data quality findings: {error || 'No data'}
      </div>
    );
  }

  const invalidCount = summary.distribution_calculation_status?.INVALID_INPUT || 0;
  const missingCount = summary.distribution_calculation_status?.MISSING_INPUT || 0;
  const zeroCount = summary.distribution_calculation_status?.ZERO_WORKLOAD || 0;
  const calculatedCount = summary.distribution_calculation_status?.CALCULATED || 0;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* Top Quality KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Arithmetic Verified"
          value={calculatedCount}
          subtitle="100% Deterministic M1"
          icon={<CheckCircle2 className="h-5 w-5" />}
          variant="emerald"
          trendText="Verified"
          trendType="positive"
          onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'CALCULATED' })}
        />

        <KpiCard
          title="Comma Decimal Format"
          value={invalidCount}
          subtitle="Contains comma (e.g. '1,5')"
          icon={<AlertTriangle className="h-5 w-5" />}
          variant="amber"
          trendText="Requires Review"
          trendType="warning"
          onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'INVALID_INPUT' })}
        />

        <KpiCard
          title="Missing Inputs"
          value={missingCount}
          subtitle="Workload or after missing"
          icon={<FileQuestion className="h-5 w-5" />}
          variant="rose"
          trendText="Uncalculated"
          trendType="negative"
          onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'MISSING_INPUT' })}
        />

        <KpiCard
          title="Standby / Zero Workload"
          value={zeroCount}
          subtitle="Reactive incident tasks"
          icon={<HelpCircle className="h-5 w-5" />}
          variant="sky"
          trendText="RULE-WL-02"
          trendType="neutral"
          onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'ZERO_WORKLOAD' })}
        />
      </div>

      {/* Two Column Charts: Calculation Status & Evidence Links */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calculation Status Hierarchy Donut */}
        <motion.div
          variants={itemVariants}
          className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur shadow-sm space-y-4"
        >
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                <span>6-Tier Calculation Priority Hierarchy</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Strict adherence to PRD M1 Priority: INVALID &gt; MISSING &gt; NEGATIVE &gt; ZERO &gt; NEGATIVE_SAVINGS &gt; CALCULATED
              </p>
            </div>
          </div>

          <AnimatedDonutChart
            data={calcStatusSegments}
            centerTitle="Total Records"
            centerValue={summary.total_activities}
            onSegmentClick={(seg) =>
              onNavigateToTab && onNavigateToTab('activities', { calcStatus: seg.label })
            }
          />
        </motion.div>

        {/* Evidence Status Donut */}
        <motion.div
          variants={itemVariants}
          className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur shadow-sm space-y-4"
        >
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
                <Link2 className="h-4 w-4 text-sky-400" />
                <span>Evidence & Documentation Attachment</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Confluence Runbook or Wiki documentation link availability
              </p>
            </div>
          </div>

          <AnimatedDonutChart
            data={evidenceSegments}
            centerTitle="Audited"
            centerValue={summary.total_activities}
          />
        </motion.div>
      </div>

      {/* Traceable Findings Table / Cards */}
      <motion.div
        variants={itemVariants}
        className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur space-y-4"
      >
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
              <ShieldAlert className="h-4 w-4 text-amber-400" />
              <span>Traceable Audit Findings & Remediation Register</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Audited findings according to PRD V1 and Business Decisions Q1–Q51
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                  Finding DQ-01: Indonesian Decimal Separator (&quot;1,5&quot;)
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-mono">
                  {invalidCount} Occurrences
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Source fields `Workload after` contain values with commas rather than standard periods.
                Per PRD Section 4 rules, raw source files remain 100% immutable; WORKLENS flags these as INVALID_INPUT rather than making silent alterations.
              </p>
            </div>
            <button
              onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'INVALID_INPUT' })}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-medium border border-amber-500/30 transition shrink-0"
            >
              <span>Inspect rows in Explorer</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl border border-sky-500/30 bg-sky-500/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
                  Finding DQ-02: Standby Incident Interventions (Workload = 0)
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-400 font-mono">
                  {zeroCount} Occurrences
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Initial operational workload is recorded as 0 minutes per month. Governed by RULE-WL-02, these activities represent standby monitoring or reactive interventions.
              </p>
            </div>
            <button
              onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'ZERO_WORKLOAD' })}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 text-xs font-medium border border-sky-500/30 transition shrink-0"
            >
              <span>Inspect rows in Explorer</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">
                  Finding DQ-03: Missing Workload Inputs
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 font-mono">
                  {missingCount} Occurrences
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Either `Workload` or `Workload after` is empty or null in the source assessment.
                Prioritized as MISSING_INPUT (Level 2).
              </p>
            </div>
            <button
              onClick={() => onNavigateToTab && onNavigateToTab('activities', { calcStatus: 'MISSING_INPUT' })}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs font-medium border border-rose-500/30 transition shrink-0"
            >
              <span>Inspect rows in Explorer</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
