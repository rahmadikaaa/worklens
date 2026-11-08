import React, { useState, useEffect, useMemo } from 'react';
import { motion, type Variants } from 'framer-motion';
import {
  Download,
  RotateCcw,
  Search,
  Info,
  Sparkles,
  Cpu,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import type {
  ActivitySummaryMetrics,
  EnrichedActivity,
  FilterOptions,
} from '../types';
import { useCountUp } from '../hooks/useMotion';
import { ActivityDetailDrawer } from './ActivityDetailDrawer';

interface ExecutiveOverviewProps {
  onNavigateToTab?: (tab: string, filter?: Record<string, string>) => void;
}

// Formatting helper matching Indonesian locale
const fmt = (v: number | undefined | null, digits: number = 0): string => {
  return Number(v || 0).toLocaleString('id-ID', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};

// Bucket definition metadata matching prototype
const BUCKET_DEFS = [
  { k: 'Kandidat', label: 'Kandidat otomasi', color: '#087f70', cls: 'bg-[#e2f3ed] text-[#087f70]' },
  { k: 'Sudah diotomasi', label: 'Sudah diotomasi', color: '#9aa9a4', cls: 'bg-[#f0f3f2] text-[#63716d]' },
  { k: 'Tidak mungkin diotomasi', label: 'Tidak mungkin diotomasi', color: '#c66f60', cls: 'bg-[#fbeae8] text-[#c66f60]' },
  { k: 'Take Out', label: 'Take Out', color: '#d4973b', cls: 'bg-[#fff3df] text-[#9a6a1c]' },
  { k: 'Dismantled', label: 'Dismantled', color: '#788380', cls: 'bg-[#f1eeee] text-[#796e6b]' },
  { k: 'Lainnya', label: 'Lainnya', color: '#bcc7c4', cls: 'bg-[#edf1ef] text-[#73817e]' },
];

export const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({ onNavigateToTab: _onNavigateToTab }) => {
  const [summary, setSummary] = useState<ActivitySummaryMetrics | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [loadingSummary, setLoadingSummary] = useState<boolean>(true);

  // Table & filter state
  const [search, setSearch] = useState<string>('');
  const [bucketFilter, setBucketFilter] = useState<string>('');
  const [toolFilter, setToolFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [quickWinOnly, setQuickWinOnly] = useState<boolean>(false);
  const [outlierOnly, setOutlierOnly] = useState<boolean>(false);
  const [verifiedBaselineOnly, setVerifiedBaselineOnly] = useState<boolean>(false);
  const [statusTriggeredFilter, setStatusTriggeredFilter] = useState<string>('');
  const [techViewMode, setTechViewMode] = useState<'all' | 'candidates'>('all');

  const [activities, setActivities] = useState<EnrichedActivity[]>([]);
  const [filteredCount, setFilteredCount] = useState<number>(0);
  const [filteredWorkloadHours, setFilteredWorkloadHours] = useState<number>(0);
  const [loadingTable, setLoadingTable] = useState<boolean>(true);
  const [pageSize, setPageSize] = useState<number>(100);

  // Drawer state
  const [selectedActivity, setSelectedActivity] = useState<EnrichedActivity | null>(null);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);

  // Fetch summary metrics on mount
  useEffect(() => {
    const fetchSummary = async () => {
      setLoadingSummary(true);
      try {
        const res = await fetch('/api/v1/activities/summary');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setSummary(data.summary);
        setFilterOptions(data.filter_options);
      } catch (err) {
        console.error('Failed to fetch activities summary:', err);
      } finally {
        setLoadingSummary(false);
      }
    };
    fetchSummary();
  }, []);

  // Fetch filtered activities
  useEffect(() => {
    let isCancelled = false;
    const fetchActivities = async () => {
      setLoadingTable(true);
      try {
        const params = new URLSearchParams();
        params.append('has_workload', 'true');
        params.append('page', '1');
        params.append('page_size', String(pageSize));
        params.append('sort_by', 'Workload');
        params.append('sort_order', 'desc');

        if (search.trim()) params.append('search', search.trim());
        if (bucketFilter) params.append('bucket', bucketFilter);
        if (toolFilter) params.append('tool', toolFilter);
        if (typeFilter) params.append('activity_type', typeFilter);
        if (quickWinOnly) params.append('quick_win_only', 'true');
        if (outlierOnly) params.append('outlier_only', 'true');
        if (verifiedBaselineOnly) params.append('verified_baseline_only', 'true');
        if (statusTriggeredFilter) params.append('status_triggered', statusTriggeredFilter);

        const res = await fetch(`/api/v1/activities?${params.toString()}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!isCancelled) {
          setActivities(data.items || []);
          setFilteredCount(data.total_count || 0);
          setFilteredWorkloadHours(data.filtered_stats?.filtered_workload_hours || 0);
        }
      } catch (err) {
        console.error('Failed to query activities:', err);
      } finally {
        if (!isCancelled) setLoadingTable(false);
      }
    };

    fetchActivities();
    return () => {
      isCancelled = true;
    };
  }, [
    search,
    bucketFilter,
    toolFilter,
    typeFilter,
    quickWinOnly,
    outlierOnly,
    verifiedBaselineOnly,
    statusTriggeredFilter,
    pageSize,
  ]);

  // Animated KPI numbers
  const totalWlAnim = useCountUp(summary?.opportunity_kpis?.total_workload_hours || 3602, 1000);
  const measuredCountAnim = useCountUp(summary?.opportunity_kpis?.measured_activities_count || 1475, 900);
  const candidateWlAnim = useCountUp(summary?.opportunity_kpis?.candidate_workload_hours || 357.5, 1100);
  const saveEstAnim = useCountUp(summary?.opportunity_kpis?.indicative_saving_hours || 321.8, 1100);

  // Stacked workload bucket percentages
  const bucketMap = useMemo(() => {
    if (!summary?.buckets) return {};
    return Object.fromEntries(summary.buckets.map((b) => [b.k, b]));
  }, [summary]);

  const totalH = summary?.opportunity_kpis?.total_workload_hours || 3602.0;

  // Maximum value for bar scales
  const maxTypeH = useMemo(() => {
    if (!summary?.types || summary.types.length === 0) return 1;
    return Math.max(...summary.types.map((t) => t.h));
  }, [summary]);

  const maxToolH = useMemo(() => {
    if (!summary?.tools || summary.tools.length === 0) return 1;
    return Math.max(...summary.tools.map((t) => t.h));
  }, [summary]);

  const maxCandidateTechH = useMemo(() => {
    if (!summary?.candidate_technologies || summary.candidate_technologies.length === 0) return 1;
    return Math.max(...summary.candidate_technologies.map((t) => t.hours));
  }, [summary]);

  // Reset all filters
  const handleResetFilters = () => {
    setSearch('');
    setBucketFilter('');
    setToolFilter('');
    setTypeFilter('');
    setQuickWinOnly(false);
    setOutlierOnly(false);
    setVerifiedBaselineOnly(false);
    setStatusTriggeredFilter('');
    setPageSize(100);
  };

  // Export filtered dataset to CSV
  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams();
      params.append('has_workload', 'true');
      params.append('page', '1');
      params.append('page_size', '1500');
      params.append('sort_by', 'Workload');
      params.append('sort_order', 'desc');

      if (search.trim()) params.append('search', search.trim());
      if (bucketFilter) params.append('bucket', bucketFilter);
      if (toolFilter) params.append('tool', toolFilter);
      if (typeFilter) params.append('activity_type', typeFilter);
      if (quickWinOnly) params.append('quick_win_only', 'true');
      if (outlierOnly) params.append('outlier_only', 'true');
      if (verifiedBaselineOnly) params.append('verified_baseline_only', 'true');
      if (statusTriggeredFilter) params.append('status_triggered', statusTriggeredFilter);

      const res = await fetch(`/api/v1/activities?${params.toString()}`);
      if (!res.ok) return;
      const data = await res.json();
      const rows: EnrichedActivity[] = data.items || [];

      const head = [
        'Activity',
        'Application',
        'Type',
        'Recorded Tool',
        'Recommended Tech',
        'Team QC',
        'Duration Minutes',
        'Events Per Month',
        'Workload Minutes',
        'Bucket',
        'Quick Win',
        'Outlier',
        'Status Triggered',
        'Baseline Verified',
        'Benefit Statement',
      ];

      const lines = [
        head,
        ...rows.map((r) => [
          r['ACTIVITY NAME'] || '',
          r.APPS || '',
          r['TYPE ACTIVITY'] || '',
          r['Tools Automation'] || '',
          r.recommended_technology || '',
          r['Team QC'] || '',
          r['Durasi (Menit)'] || '',
          r['Event Per Month'] || '',
          r.Workload || '',
          r.automation_bucket || '',
          r.is_quick_win ? 'YES' : 'NO',
          r.is_outlier ? 'YES' : 'NO',
          r.status_triggered || '',
          r.is_verified_baseline ? 'YES' : 'NO',
          r.benefit_statement || '',
        ]),
      ];

      const csvContent = lines
        .map((row) => row.map((v) => `"${String(v ?? '').replace(/"/g, '""')}"`).join(','))
        .join('\n');

      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `worklens-meeting-oktober-filtered-${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export CSV error:', err);
    }
  };

  const handleRowClick = (activity: EnrichedActivity) => {
    setSelectedActivity(activity);
    setDrawerOpen(true);
  };

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08 },
    },
  };

  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="max-w-[1440px] mx-auto px-4 sm:px-8 py-7 pb-16 space-y-6 text-[#172321]"
    >
      {/* Hero Header */}
      <motion.header variants={cardVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div>
          <div className="text-[11px] font-extrabold tracking-[0.13em] uppercase text-[#087f70] mb-2 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-[#087f70] animate-pulse" />
            Automation Opportunity · L1 AGIT
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-[-0.04em] text-[#172321] leading-tight m-0">
            Peluang Otomasi
          </h1>
          <p className="text-[#73817e] text-sm sm:text-base mt-2 max-w-2xl leading-relaxed">
            Peta beban kerja operasional untuk membantu menentukan prioritas otomasi, memisahkan klaim teoretis dari peluang nyata, dan menelusuri aktivitas sampai level detail eksekusi.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 self-start md:self-auto">
          <button
            onClick={handleExportCSV}
            className="px-3.5 py-2 border border-[#e6ecea] bg-white text-[#172321] rounded-xl text-xs font-semibold hover:bg-[#edf1ef] transition-colors flex items-center gap-1.5 shadow-xs"
            title="Export filtered activities to CSV"
          >
            <Download className="h-3.5 w-3.5 text-[#087f70]" />
            Export CSV
          </button>
          <button
            onClick={handleResetFilters}
            className="px-3.5 py-2 bg-[#103f38] text-white rounded-xl text-xs font-semibold hover:brightness-95 transition-colors flex items-center gap-1.5 shadow-xs"
            title="Reset all filters"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Reset Filter
          </button>
          <div className="text-left md:text-right text-xs text-[#73817e] bg-white border border-[#e6ecea] px-3.5 py-2 rounded-xl shadow-xs whitespace-nowrap">
            <span className="block text-[10px] text-[#73817e] uppercase font-semibold">Snapshot</span>
            <span className="font-bold text-[#172321]">Breakdown Activity</span> · L1 AGIT
          </div>
        </div>
      </motion.header>

      {/* Top 4 KPI Cards */}
      <motion.section
        variants={cardVariants}
        className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 transition-opacity duration-300 ${loadingSummary ? 'opacity-75' : 'opacity-100'
          }`}
      >
        {/* KPI 1: Total Workload */}
        <div className="bg-white border border-[#e6ecea] rounded-2xl p-5 shadow-[0_8px_28px_rgba(22,42,37,0.055)] hover:shadow-md transition-shadow">
          <div className="text-[11px] font-bold uppercase tracking-[0.09em] text-[#73817e]">Total workload</div>
          <div className="text-3xl font-extrabold tracking-[-0.04em] text-[#172321] my-2 font-tabular">
            {fmt(totalWlAnim, 1)}
          </div>
          <div className="text-xs text-[#73817e]">jam per bulan · seluruh aktivitas terhitung</div>
        </div>

        {/* KPI 2: Aktivitas Terukur */}
        <div className="bg-white border border-[#e6ecea] rounded-2xl p-5 shadow-[0_8px_28px_rgba(22,42,37,0.055)] hover:shadow-md transition-shadow">
          <div className="text-[11px] font-bold uppercase tracking-[0.09em] text-[#73817e]">Aktivitas terukur</div>
          <div className="text-3xl font-extrabold tracking-[-0.04em] text-[#172321] my-2 font-tabular">
            {fmt(measuredCountAnim)}
          </div>
          <div className="text-xs text-[#73817e]">baris memiliki nilai workload</div>
        </div>

        {/* KPI 3: Kandidat Otomasi (Highlight Deep Pine Green) */}
        <div className="bg-[#103f38] text-white border border-[#103f38] rounded-2xl p-5 shadow-[0_8px_28px_rgba(16,63,56,0.2)] hover:brightness-105 transition-all">
          <div className="text-[11px] font-bold uppercase tracking-[0.09em] text-[#b8d8d1]">Kandidat otomasi</div>
          <div className="text-3xl font-extrabold tracking-[-0.04em] text-white my-2 font-tabular flex items-baseline gap-1">
            {fmt(candidateWlAnim, 1)} <span className="text-base font-semibold text-[#b8d8d1]">jam</span>
          </div>
          <div className="text-xs text-[#b8d8d1]">
            {fmt(summary?.opportunity_kpis?.candidate_activities_count || 200)} aktivitas (
            {fmt(summary?.opportunity_kpis?.candidate_percentage || 9.9, 1)}%)
          </div>
        </div>

        {/* KPI 4: Potensi Hemat Indikatif */}
        <div className="bg-white border border-[#e6ecea] rounded-2xl p-5 shadow-[0_8px_28px_rgba(22,42,37,0.055)] hover:shadow-md transition-shadow">
          <div className="text-[11px] font-bold uppercase tracking-[0.09em] text-[#73817e]">Potensi hemat indikatif</div>
          <div className="text-3xl font-extrabold tracking-[-0.04em] text-[#172321] my-2 font-tabular flex items-baseline gap-1">
            {fmt(saveEstAnim, 1)} <span className="text-base font-semibold text-[#73817e]">jam</span>
          </div>
          <div className="text-xs text-[#73817e]">jam per bulan · asumsi efisiensi 90%</div>
        </div>
      </motion.section>

      {/* Scope 1: Reality Check: Klaim vs Peluang Nyata */}
      <motion.section
        variants={cardVariants}
        className="bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)] space-y-4"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#eef2f0] pb-3">
          <div className="flex items-center space-x-2">
            <span className="h-2.5 w-2.5 rounded-full bg-[#087f70]" />
            <h2 className="text-sm font-bold text-[#172321] tracking-tight uppercase">
              Reality Check: Klaim Penghematan Agregat vs Peluang Nyata Siap Eksekusi
            </h2>
          </div>
          <span className="text-[11px] font-semibold text-[#73817e] bg-[#f8fafb] px-3 py-1 rounded-full border border-[#e6ecea] self-start sm:self-auto">
            Strategic Review · L1 AGIT Meeting
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 text-xs">
          {/* Card A: Klaim Teoretis */}
          <div className="p-4 bg-[#f8fafb] rounded-xl border border-[#e6ecea]">
            <div className="text-[#73817e] font-bold uppercase text-[10px] tracking-wider">
              Klaim Penghematan Awal (Dataset)
            </div>
            <div className="text-2xl font-extrabold text-[#73817e] my-1 font-tabular">
              {fmt(summary?.reality_check?.theoretical_claimed_hours || 3156.3, 1)}{' '}
              <span className="text-xs font-semibold">jam/bln</span>
            </div>
            <p className="text-[11px] text-[#73817e] leading-snug m-0">
              Klaim <b>87,6%</b> mengasumsikan efisiensi 90% secara blanket pada seluruh 3.460 baris, tanpa menyaring aktivitas yang sudah otomatis atau dismantled.
            </p>
          </div>

          {/* Card B: Peluang Nyata */}
          <div className="p-4 bg-[#e3f4ef]/70 rounded-xl border border-[#b2e2d7]">
            <div className="text-[#087f70] font-bold uppercase text-[10px] tracking-wider flex items-center justify-between">
              <span>Peluang Nyata (Kandidat L1)</span>
              <span className="px-1.5 py-0.5 rounded bg-[#087f70] text-white text-[9px] font-bold">Siap Eksekusi</span>
            </div>
            <div className="text-2xl font-extrabold text-[#087f70] my-1 font-tabular">
              {fmt(summary?.reality_check?.real_actionable_hours || 357.5, 1)}{' '}
              <span className="text-xs font-semibold">jam beban</span>
            </div>
            <p className="text-[11px] text-[#172321] leading-snug m-0">
              <b>9,9%</b> total beban kerja. Estimasi penghematan realistis: <b>{fmt(summary?.reality_check?.real_savings_estimate_hours || 321.8, 1)} jam/bln</b> (200 aktivitas).
            </p>
          </div>

          {/* Card C: Di Luar Ruang Lingkup */}
          <div className="p-4 bg-[#fff9ec] rounded-xl border border-[#f1e5c9]">
            <div className="text-[#b98227] font-bold uppercase text-[10px] tracking-wider">
              Beban di Luar Cakupan Eksekusi Baru
            </div>
            <div className="text-2xl font-extrabold text-[#745d34] my-1 font-tabular">
              {fmt(summary?.reality_check?.out_of_scope_workload_hours || 3244.5, 1)}{' '}
              <span className="text-xs font-semibold">jam/bln</span>
            </div>
            <p className="text-[11px] text-[#745d34] leading-snug m-0">
              <b>90,1%</b> beban sudah diotomasi ({fmt(summary?.reality_check?.breakdown_out_of_scope?.already_automated_hours || 1993.7, 1)}j), non-otomasi ({fmt(summary?.reality_check?.breakdown_out_of_scope?.not_possible_hours || 811.9, 1)}j), atau takeout.
            </p>
          </div>
        </div>

        <div className="p-3 bg-[#f8fafb] rounded-xl border border-[#e6ecea] text-xs text-[#44524f] flex items-start gap-2.5">
          <Info className="h-4 w-4 text-[#087f70] shrink-0 mt-0.5" />
          <span className="leading-relaxed">
            <b>Kesimpulan Meeting:</b> {summary?.reality_check?.gap_statement || "Klaim awal 87,6% perlu disesuaikan saat presentasi manajemen. Fokus realistis adalah mengeksekusi 200 aktivitas Kandidat (357,5 jam) yang secara langsung berada di bawah domain L1."}
          </span>
        </div>
      </motion.section>

      {/* Grid 2: Komposisi beban kerja & Konsentrasi workload */}
      <motion.section variants={cardVariants} className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Panel: Komposisi Beban Kerja (7 cols) */}
        <div className="lg:col-span-7 bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)] flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between gap-3 mb-4">
              <div>
                <h2 className="text-base font-bold tracking-tight text-[#172321] m-0">Komposisi beban kerja</h2>
                <p className="text-xs text-[#73817e] mt-1 m-0">Distribusi workload bulanan berdasarkan status peluang.</p>
              </div>
              <span className="rounded-full px-2.5 py-1 bg-[#e3f4ef] text-[#087f70] text-[11px] font-bold whitespace-nowrap">
                Jam / bulan
              </span>
            </div>

            {/* Continuous Stacked Progress Bar */}
            <div className="h-3.5 rounded-full overflow-hidden flex bg-[#edf1ef] my-5">
              {BUCKET_DEFS.map((b) => {
                const item = bucketMap[b.k];
                const widthPct = item ? (item.h / totalH) * 100 : 0;
                if (widthPct <= 0) return null;
                return (
                  <motion.div
                    key={b.k}
                    initial={{ width: 0 }}
                    animate={{ width: `${widthPct}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    style={{ backgroundColor: b.color }}
                    className="h-full relative group cursor-pointer"
                    title={`${b.label}: ${fmt(item?.h, 1)} jam (${fmt(widthPct, 1)}%)`}
                    onClick={() => setBucketFilter(b.k === bucketFilter ? '' : b.k)}
                  />
                );
              })}
            </div>

            {/* 2-Column Legend */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-3.5">
              {BUCKET_DEFS.map((b) => {
                const item = bucketMap[b.k] || { h: 0, n: 0 };
                const pct = totalH > 0 ? (item.h / totalH) * 100 : 0;
                const isSelected = bucketFilter === b.k;
                return (
                  <div
                    key={b.k}
                    onClick={() => setBucketFilter(isSelected ? '' : b.k)}
                    className={`flex items-center justify-between text-xs p-1.5 rounded-lg transition-colors cursor-pointer ${isSelected ? 'bg-[#e3f4ef]/60 ring-1 ring-[#087f70]' : 'hover:bg-[#f8fafb]'
                      }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 pr-2">
                      <span className="w-2.5 h-2.5 rounded-[3px] shrink-0" style={{ backgroundColor: b.color }} />
                      <div className="truncate">
                        <span className="font-medium text-[#172321]">{b.label}</span>
                        <small className="block text-[11px] text-[#73817e] font-tabular">
                          {fmt(item.n)} aktivitas · {fmt(pct, 1)}%
                        </small>
                      </div>
                    </div>
                    <span className="font-bold text-[#172321] font-tabular whitespace-nowrap">
                      {fmt(item.h, 1)} jam
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Assumption Callout Note */}
          <div className="mt-5 p-3.5 bg-[#fff9ec] border border-[#f1e5c9] rounded-xl text-xs text-[#745d34] flex items-start gap-2.5">
            <Info className="h-4 w-4 shrink-0 mt-0.5 text-[#b98227]" />
            <div>
              Angka peluang hemat 90% merupakan simulasi asumsi, bukan penghematan aktual yang telah tervalidasi.
              Gunakan bucket <b>Kandidat</b> sebagai titik awal evaluasi.
            </div>
          </div>
        </div>

        {/* Right Panel: Konsentrasi Workload / Pareto (5 cols) + Scope 5: Outlier Detection */}
        <div className="lg:col-span-5 bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)] flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h2 className="text-base font-bold tracking-tight text-[#172321] m-0">Konsentrasi workload</h2>
              <p className="text-xs text-[#73817e] mt-1 m-0">Kontribusi aktivitas teratas terhadap total beban operasional.</p>
            </div>

            <div className="space-y-3 mt-4">
              {(summary?.pareto?.slice(0, 7) || [
                { n: 1, p: 12.7 },
                { n: 10, p: 23.3 },
                { n: 20, p: 27.6 },
                { n: 50, p: 38.9 },
                { n: 100, p: 52.6 },
                { n: 200, p: 70.7 },
                { n: 400, p: 90.4 },
              ]).map((item) => (
                <div key={item.n} className="grid grid-cols-[115px_1fr_50px] items-center gap-3 text-xs">
                  <span className="text-[#44524f] font-medium truncate">Top {fmt(item.n)} aktivitas</span>
                  <div className="h-2.5 rounded-full bg-[#edf1ef] overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.p}%` }}
                      transition={{ duration: 0.7, ease: 'easeOut' }}
                      className="h-full rounded-full bg-[#5d8c80]"
                    />
                  </div>
                  <span className="text-right font-tabular text-[#44524f] font-semibold">{fmt(item.p, 1)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Scope 5: Outlier Alert Box */}
          <div className="mt-5 p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start justify-between gap-2.5">
            <div className="space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-rose-900">
                <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />
                <span>Pencilan Ekstrim: Office 365 OneDrive Backup</span>
              </div>
              <p className="text-[11px] text-rose-700 m-0 leading-snug">
                Menyumbang <b>456,0 jam/bulan</b> (12,7% total seluruh beban L1). Perlu verifikasi manual L1 apakah 19 event x 1.440 menit merupakan anomali input.
              </p>
            </div>
            <button
              onClick={() => {
                setSearch('Backup OneDrive files');
                setOutlierOnly(true);
              }}
              className="px-2.5 py-1.5 bg-white text-rose-700 rounded-lg border border-rose-300 font-semibold text-[11px] hover:bg-rose-100 whitespace-nowrap shrink-0 shadow-xs"
            >
              Periksa
            </button>
          </div>
        </div>
      </motion.section>

      {/* Grid Equal: Beban per tipe aktivitas & Beban per tools (Scope 3: Technology Recommendation) */}
      <motion.section variants={cardVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Panel 1: Beban per tipe aktivitas */}
        <div className="bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)]">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold tracking-tight text-[#172321] m-0">Beban per tipe aktivitas</h2>
              <p className="text-xs text-[#73817e] mt-1 m-0">Komposisi jam kerja berdasarkan TYPE ACTIVITY.</p>
            </div>
            {typeFilter && (
              <button
                onClick={() => setTypeFilter('')}
                className="text-xs text-[#087f70] hover:underline flex items-center gap-1 font-semibold"
              >
                Reset tipe
              </button>
            )}
          </div>

          <div className="space-y-3 mt-4">
            {(summary?.types || []).slice(0, 8).map((t) => {
              const widthPct = maxTypeH > 0 ? (t.h / maxTypeH) * 100 : 0;
              const isSelected = typeFilter === t.k;
              return (
                <div
                  key={t.k}
                  onClick={() => setTypeFilter(isSelected ? '' : t.k)}
                  className={`grid grid-cols-[140px_1fr_65px] items-center gap-3 text-xs p-1 rounded-lg cursor-pointer transition-colors ${isSelected ? 'bg-[#e3f4ef]/60 ring-1 ring-[#087f70]' : 'hover:bg-[#f8fafb]'
                    }`}
                  title={`${t.k}: ${fmt(t.h, 1)} jam`}
                >
                  <span className="text-[#44524f] font-medium truncate">{t.k}</span>
                  <div className="h-2.5 rounded-full bg-[#edf1ef] overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${widthPct}%` }}
                      transition={{ duration: 0.6, ease: 'easeOut' }}
                      className="h-full rounded-full bg-[#5d8c80]"
                    />
                  </div>
                  <span className="text-right font-tabular text-[#44524f] font-semibold">{fmt(t.h, 1)} jam</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Panel 2: Beban per tools automation & Scope 3: Technology Recommendation */}
        <div className="bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)]">
          <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-base font-bold tracking-tight text-[#172321] m-0">
                {techViewMode === 'all' ? 'Beban per tools automation' : 'Rekomendasi teknologi kandidat'}
              </h2>
              <p className="text-xs text-[#73817e] mt-1 m-0">
                {techViewMode === 'all'
                  ? 'Tools yang tercatat pada aktivitas operasional saat ini.'
                  : 'Indikasi rekomendasi teknologi untuk 200 aktivitas Kandidat (357,5 jam).'}
              </p>
            </div>

            {/* Toggle Mode */}
            <div className="flex items-center gap-1 bg-[#f0f3f2] p-1 rounded-xl self-start sm:self-auto text-xs">
              <button
                onClick={() => setTechViewMode('all')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                  techViewMode === 'all' ? 'bg-white text-[#172321] shadow-xs' : 'text-[#73817e] hover:text-[#172321]'
                }`}
              >
                Tools Saat Ini
              </button>
              <button
                onClick={() => setTechViewMode('candidates')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors flex items-center gap-1 ${
                  techViewMode === 'candidates'
                    ? 'bg-[#103f38] text-white shadow-xs'
                    : 'text-[#73817e] hover:text-[#172321]'
                }`}
              >
                <Cpu className="h-3 w-3" />
                Target Kandidat
              </button>
            </div>
          </div>

          <div className="space-y-3 mt-4">
            {techViewMode === 'all'
              ? (summary?.tools || []).slice(0, 8).map((tool) => {
                  const widthPct = maxToolH > 0 ? (tool.h / maxToolH) * 100 : 0;
                  const isSelected = toolFilter === tool.k;
                  return (
                    <div
                      key={tool.k}
                      onClick={() => setToolFilter(isSelected ? '' : tool.k)}
                      className={`grid grid-cols-[140px_1fr_65px] items-center gap-3 text-xs p-1 rounded-lg cursor-pointer transition-colors ${
                        isSelected ? 'bg-[#e3f4ef]/60 ring-1 ring-[#087f70]' : 'hover:bg-[#f8fafb]'
                      }`}
                      title={`${tool.k}: ${fmt(tool.h, 1)} jam`}
                    >
                      <span className="text-[#44524f] font-medium truncate">{tool.k}</span>
                      <div className="h-2.5 rounded-full bg-[#edf1ef] overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${widthPct}%` }}
                          transition={{ duration: 0.6, ease: 'easeOut' }}
                          className="h-full rounded-full bg-[#5d8c80]"
                        />
                      </div>
                      <span className="text-right font-tabular text-[#44524f] font-semibold">{fmt(tool.h, 1)} jam</span>
                    </div>
                  );
                })
              : (summary?.candidate_technologies || []).map((tech) => {
                  const widthPct = maxCandidateTechH > 0 ? (tech.hours / maxCandidateTechH) * 100 : 0;
                  return (
                    <div
                      key={tech.technology}
                      onClick={() => {
                        setBucketFilter('Kandidat');
                        setSearch(tech.technology.replace(' / AION', '').replace(' Platform', ''));
                      }}
                      className="grid grid-cols-[150px_1fr_65px] items-center gap-3 text-xs p-1 rounded-lg cursor-pointer hover:bg-[#f8fafb] transition-colors"
                      title={`${tech.technology}: ${fmt(tech.hours, 1)} jam (${tech.count} aktivitas)`}
                    >
                      <div className="truncate">
                        <span className="text-[#172321] font-semibold">{tech.technology}</span>
                        <small className="block text-[10px] text-[#73817e]">{tech.count} SOP</small>
                      </div>
                      <div className="h-2.5 rounded-full bg-[#edf1ef] overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${widthPct}%` }}
                          transition={{ duration: 0.6, ease: 'easeOut' }}
                          className="h-full rounded-full bg-[#087f70]"
                        />
                      </div>
                      <span className="text-right font-tabular text-[#087f70] font-bold">
                        {fmt(tech.hours, 1)} jam
                      </span>
                    </div>
                  );
                })}
          </div>

          {techViewMode === 'candidates' && (
            <small className="block text-[10px] text-[#73817e] pt-3 border-t border-[#e6ecea] mt-3">
              *Indikasi rekomendasi teknologi berdasarkan taksonomi operasional, bukan keputusan implementasi final.
            </small>
          )}
        </div>
      </motion.section>

      {/* Scope 6: Trigger Readiness Summary Panel */}
      <motion.section
        variants={cardVariants}
        className="bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)] space-y-3"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#eef2f0] pb-3">
          <div>
            <h2 className="text-base font-bold tracking-tight text-[#172321] m-0">
              Kesiapan Trigger Otomasi (Trigger Analysis · 667 Baseline)
            </h2>
            <p className="text-xs text-[#73817e] mt-0.5 m-0">
              Tingkat kesiapan eksekusi pemicu otomatis yang dipetakan dari baseline Agent Harness.
            </p>
          </div>
          <span className="text-[11px] font-semibold text-[#087f70] bg-[#e3f4ef] px-3 py-1 rounded-full">
            667 Verified Baseline
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
          <div
            onClick={() => setStatusTriggeredFilter(statusTriggeredFilter === 'Fully Automated' ? '' : 'Fully Automated')}
            className={`p-3.5 rounded-xl border cursor-pointer transition-colors ${
              statusTriggeredFilter === 'Fully Automated'
                ? 'bg-emerald-100/80 border-emerald-400'
                : 'bg-emerald-50/50 border-emerald-200 hover:bg-emerald-100/50'
            }`}
          >
            <div className="text-emerald-800 font-bold uppercase text-[10px]">Fully Automated</div>
            <div className="text-2xl font-extrabold text-emerald-900 my-1 font-tabular">
              {fmt(summary?.trigger_readiness_summary?.fully_automated_count || 389)}
            </div>
            <span className="text-[11px] text-emerald-700">Trigger aktif di produksi</span>
          </div>

          <div
            onClick={() =>
              setStatusTriggeredFilter(
                statusTriggeredFilter === 'Not Yet Triggered Automated' ? '' : 'Not Yet Triggered Automated'
              )
            }
            className={`p-3.5 rounded-xl border cursor-pointer transition-colors ${
              statusTriggeredFilter === 'Not Yet Triggered Automated'
                ? 'bg-amber-100/80 border-amber-400'
                : 'bg-amber-50/50 border-amber-200 hover:bg-amber-100/50'
            }`}
          >
            <div className="text-amber-800 font-bold uppercase text-[10px]">Not Yet Triggered</div>
            <div className="text-2xl font-extrabold text-amber-900 my-1 font-tabular">
              {fmt(summary?.trigger_readiness_summary?.not_yet_triggered_count || 256)}
            </div>
            <span className="text-[11px] text-amber-700">Siap dipasang pemicu</span>
          </div>

          <div
            onClick={() =>
              setStatusTriggeredFilter(statusTriggeredFilter === 'Partial Automated' ? '' : 'Partial Automated')
            }
            className={`p-3.5 rounded-xl border cursor-pointer transition-colors ${
              statusTriggeredFilter === 'Partial Automated'
                ? 'bg-blue-100/80 border-blue-400'
                : 'bg-blue-50/50 border-blue-200 hover:bg-blue-100/50'
            }`}
          >
            <div className="text-blue-800 font-bold uppercase text-[10px]">Partial Automated</div>
            <div className="text-2xl font-extrabold text-blue-900 my-1 font-tabular">
              {fmt(summary?.trigger_readiness_summary?.partial_automated_count || 22)}
            </div>
            <span className="text-[11px] text-blue-700">Otomasi sebagian</span>
          </div>

          <div
            onClick={() =>
              setStatusTriggeredFilter(statusTriggeredFilter === 'Unmapped in Baseline' ? '' : 'Unmapped in Baseline')
            }
            className={`p-3.5 rounded-xl border cursor-pointer transition-colors ${
              statusTriggeredFilter === 'Unmapped in Baseline'
                ? 'bg-slate-200 border-slate-400'
                : 'bg-slate-50 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <div className="text-slate-700 font-bold uppercase text-[10px]">Unmapped in Baseline</div>
            <div className="text-2xl font-extrabold text-slate-800 my-1 font-tabular">
              {fmt(summary?.trigger_readiness_summary?.unmapped_count || 2793)}
            </div>
            <span className="text-[11px] text-slate-500">Tidak ada kolom pemicu</span>
          </div>
        </div>

        <p className="text-[11px] text-[#73817e] m-0 pt-2 border-t border-[#e6ecea]">
          {summary?.trigger_readiness_summary?.gap_note ||
            'Status Triggered terverifikasi pada 667 use case baseline dari Agent Harness. 2.793 aktivitas lainnya berstatus Unmapped in Baseline karena sheet Breakdown Activity tidak memuat kolom pemicu langsung.'}
        </p>
      </motion.section>

      {/* Table Section: Eksplorasi aktivitas */}
      <motion.section
        variants={cardVariants}
        className="bg-white border border-[#e6ecea] rounded-2xl shadow-[0_8px_28px_rgba(22,42,37,0.055)] overflow-hidden"
      >
        <div className="p-5 sm:p-6 pb-4">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-4">
            <div>
              <h2 className="text-base font-bold tracking-tight text-[#172321] m-0">Eksplorasi aktivitas</h2>
              <p className="text-xs text-[#73817e] mt-1 m-0">
                Cari aktivitas, filter segmentasi quick-win, status trigger, dan inspeksi detail benefit.
              </p>
            </div>
            <div className="flex items-center gap-2 self-start sm:self-auto">
              <span className="rounded-full px-3 py-1 bg-[#e3f4ef] text-[#087f70] text-xs font-bold whitespace-nowrap">
                {fmt(filteredCount)} records
              </span>
            </div>
          </div>

          {/* Quick-Filter Pills */}
          <div className="flex flex-wrap items-center gap-2 pb-3 mb-3 border-b border-[#eef2f0]">
            <span className="text-xs font-bold text-[#73817e] mr-1">Quick Filters:</span>

            {/* Quick Win Filter */}
            <button
              onClick={() => setQuickWinOnly(!quickWinOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors ${
                quickWinOnly
                  ? 'bg-amber-500 text-white shadow-xs'
                  : 'bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100'
              }`}
            >
              <Zap className="h-3 w-3" />
              ⚡ Quick-Win Automation ({summary?.quick_wins_summary?.total_count || 103})
            </button>

            {/* Outlier Filter */}
            <button
              onClick={() => setOutlierOnly(!outlierOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors ${
                outlierOnly
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100'
              }`}
            >
              <AlertTriangle className="h-3 w-3" />
              ⚠️ Pencilan Ekstrim (1)
            </button>

            {/* Baseline Verified Filter */}
            <button
              onClick={() => setVerifiedBaselineOnly(!verifiedBaselineOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                verifiedBaselineOnly
                  ? 'bg-[#087f70] text-white shadow-xs'
                  : 'bg-[#e3f4ef] text-[#087f70] border border-[#b2e2d7] hover:bg-[#d6f0e8]'
              }`}
            >
              <Sparkles className="h-3 w-3" />
              ✓ 667 Baseline Verified
            </button>
          </div>

          {/* Filters Bar */}
          <div className="flex flex-wrap gap-2.5 pt-1">
            <div className="relative flex-1 min-w-[240px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#73817e]" />
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cari aktivitas, aplikasi, rekomendasi tech, atau benefit…"
                className="w-full pl-9 pr-3 py-2 bg-[#f8fafb] border border-[#e6ecea] rounded-xl text-xs text-[#172321] placeholder-[#73817e] focus:outline-none focus:border-[#78a99d] focus:ring-2 focus:ring-[#e5f2ee] transition-all"
              />
            </div>

            {/* Bucket Filter */}
            <select
              value={bucketFilter}
              onChange={(e) => setBucketFilter(e.target.value)}
              className="min-w-[150px] px-3 py-2 bg-[#f8fafb] border border-[#e6ecea] rounded-xl text-xs text-[#172321] focus:outline-none focus:border-[#78a99d] focus:ring-2 focus:ring-[#e5f2ee] transition-all"
            >
              <option value="">Semua bucket</option>
              {BUCKET_DEFS.map((b) => (
                <option key={b.k} value={b.k}>
                  {b.label}
                </option>
              ))}
            </select>

            {/* Tool Filter */}
            <select
              value={toolFilter}
              onChange={(e) => setToolFilter(e.target.value)}
              className="min-w-[140px] px-3 py-2 bg-[#f8fafb] border border-[#e6ecea] rounded-xl text-xs text-[#172321] focus:outline-none focus:border-[#78a99d] focus:ring-2 focus:ring-[#e5f2ee] transition-all"
            >
              <option value="">Semua tools</option>
              {(filterOptions?.tools || []).map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>

            {/* Trigger Status Filter */}
            <select
              value={statusTriggeredFilter}
              onChange={(e) => setStatusTriggeredFilter(e.target.value)}
              className="min-w-[150px] px-3 py-2 bg-[#f8fafb] border border-[#e6ecea] rounded-xl text-xs text-[#172321] focus:outline-none focus:border-[#78a99d] focus:ring-2 focus:ring-[#e5f2ee] transition-all"
            >
              <option value="">Semua status trigger</option>
              <option value="Fully Automated">Fully Automated</option>
              <option value="Not Yet Triggered Automated">Not Yet Triggered</option>
              <option value="Partial Automated">Partial Automated</option>
              <option value="Unmapped in Baseline">Unmapped in Baseline</option>
            </select>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="min-w-[140px] px-3 py-2 bg-[#f8fafb] border border-[#e6ecea] rounded-xl text-xs text-[#172321] focus:outline-none focus:border-[#78a99d] focus:ring-2 focus:ring-[#e5f2ee] transition-all"
            >
              <option value="">Semua tipe</option>
              {(filterOptions?.types || []).map((tp) => (
                <option key={tp} value={tp}>
                  {tp}
                </option>
              ))}
            </select>

            {/* Reset Filter Button */}
            {(search ||
              bucketFilter ||
              toolFilter ||
              typeFilter ||
              quickWinOnly ||
              outlierOnly ||
              verifiedBaselineOnly ||
              statusTriggeredFilter) && (
              <button
                onClick={handleResetFilters}
                className="px-3 py-2 text-xs font-semibold text-[#c66f60] bg-[#fbeae8] rounded-xl hover:bg-[#f6d7d4] transition-colors flex items-center gap-1.5"
              >
                <RotateCcw className="h-3 w-3" />
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Table Meta */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 px-5 sm:px-6 pb-3 text-xs text-[#73817e]">
          <span>
            Menampilkan <b className="text-[#172321] font-tabular">{fmt(activities.length)}</b> dari{' '}
            <b className="text-[#172321] font-tabular">{fmt(filteredCount)}</b> aktivitas
          </span>
          <span>
            Total workload hasil filter:{' '}
            <b className="text-[#172321] font-tabular">{fmt(filteredWorkloadHours, 1)}</b> jam/bulan
          </span>
        </div>

        {/* Interactive Data Table */}
        <div className="overflow-x-auto max-h-[580px] border-t border-[#e6ecea]">
          <table className="w-full min-w-[960px] text-left text-xs border-collapse">
            <thead>
              <tr className="sticky top-0 bg-[#f8faf9] z-10 border-b border-[#e6ecea] text-[10px] uppercase font-bold tracking-[0.07em] text-[#72807c]">
                <th className="py-3 px-4">Aktivitas / Aplikasi</th>
                <th className="py-3 px-3">Type</th>
                <th className="py-3 px-3">Tools & Target</th>
                <th className="py-3 px-3">Team QC</th>
                <th className="py-3 px-3 text-right">Durasi</th>
                <th className="py-3 px-3 text-right">Event/bln</th>
                <th className="py-3 px-3 text-right">Workload</th>
                <th className="py-3 px-4">Bucket</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#eef2f0]">
              {loadingTable ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#73817e]">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-[#087f70] border-t-transparent mb-2" />
                    <div>Memuat aktivitas...</div>
                  </td>
                </tr>
              ) : activities.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#73817e]">
                    Tidak ada aktivitas yang sesuai dengan filter.
                  </td>
                </tr>
              ) : (
                activities.map((row) => {
                  const bName = row.automation_bucket || 'Lainnya';
                  const bDef = BUCKET_DEFS.find((x) => x.k === bName) || BUCKET_DEFS[5];
                  const durVal = Number(row['Durasi (Menit)'] || 0);
                  const evVal = Number(row['Event Per Month'] || 0);
                  const wlHours = Number(row.Workload || 0) / 60.0;

                  return (
                    <tr
                      key={row.activity_id}
                      onClick={() => handleRowClick(row)}
                      className="hover:bg-[#f8fbfa] cursor-pointer transition-colors group"
                    >
                      <td className="py-3 px-4 min-w-[260px]">
                        <div className="flex flex-wrap items-center gap-1.5 mb-1">
                          {row.is_outlier && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-extrabold bg-rose-100 text-rose-800 border border-rose-300">
                              ⚠️ Outlier 456j
                            </span>
                          )}
                          {row.is_quick_win && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                              ⚡ Quick Win
                            </span>
                          )}
                          {row.is_verified_baseline && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                              ✓ 667 Baseline
                            </span>
                          )}
                        </div>
                        <div className="font-semibold text-[#172321] group-hover:text-[#087f70] transition-colors leading-snug">
                          {row['ACTIVITY NAME']}
                        </div>
                        <span className="block text-[11px] text-[#73817e] font-normal mt-0.5">{row.APPS}</span>
                      </td>
                      <td className="py-3 px-3 text-[#44524f]">{row['TYPE ACTIVITY'] || '—'}</td>
                      <td className="py-3 px-3 text-[#44524f]">
                        <div className="font-medium text-[#172321]">{row['Tools Automation'] || '—'}</div>
                        {row.recommended_technology && row.recommended_technology !== row['Tools Automation'] && (
                          <span className="text-[10px] text-[#087f70] font-semibold block mt-0.5">
                            Target: {row.recommended_technology}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-[#44524f]">{row['Team QC'] || '—'}</td>
                      <td className="py-3 px-3 text-right font-tabular text-[#44524f]">{fmt(durVal)}</td>
                      <td className="py-3 px-3 text-right font-tabular text-[#44524f]">
                        {fmt(evVal, evVal % 1 !== 0 ? 2 : 0)}
                      </td>
                      <td className="py-3 px-3 text-right font-tabular whitespace-nowrap">
                        <b className="text-[#172321]">{fmt(wlHours, 2)}</b>{' '}
                        <span className="text-[#73817e]">jam</span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-semibold whitespace-nowrap ${bDef.cls}`}
                        >
                          {bDef.k}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer */}
        <div className="p-4 px-5 sm:px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs bg-[#f8faf9] border-t border-[#e6ecea]">
          <span className="text-[#73817e]">Urut berdasarkan workload terbesar</span>
          {filteredCount > pageSize && (
            <button
              onClick={() => setPageSize((prev) => prev + 100)}
              className="px-4 py-2 border border-[#e6ecea] bg-white text-[#172321] rounded-xl font-semibold hover:bg-[#edf1ef] transition-colors self-start sm:self-auto"
            >
              Muat 100 lagi ({fmt(filteredCount - pageSize)} tersisa)
            </button>
          )}
        </div>
      </motion.section>

      {/* Panel: Catatan kualitas & interpretasi data */}
      <motion.section
        variants={cardVariants}
        className="bg-white border border-[#e6ecea] rounded-2xl p-5 sm:p-6 shadow-[0_8px_28px_rgba(22,42,37,0.055)]"
      >
        <h2 className="text-base font-bold tracking-tight text-[#172321] m-0 mb-3">
          Catatan kualitas & interpretasi data (Meeting L1 AGIT)
        </h2>
        <ul className="list-disc pl-5 space-y-1.5 text-xs text-[#73817e]">
          <li>
            <b>Reality Check:</b> 90,1% beban kerja terhitung (3.245 jam) berada di luar cakupan otomasi baru L1. Peluang nyata yang siap dieksekusi adalah <b>357,5 jam beban Kandidat</b> dengan potensi hemat sekitar <b>321,8 jam/bulan</b>.
          </li>
          <li>
            <b>Quick-Win Segmentasi:</b> Terdapat <b>{summary?.quick_wins_summary?.total_count || 103} aktivitas</b> berkategori Quick-Win ({fmt(summary?.quick_wins_summary?.total_hours || 266.9, 1)} jam) dengan frekuensi tinggi dan durasi ringkas yang ideal untuk sprint awal otomasi.
          </li>
          <li>
            <b>Pencilan Ekstrim (Outlier):</b> Aktivitas <i>Office 365 Backup OneDrive</i> mencatat <b>456,0 jam/bulan</b> (12,7% beban total organisasi). Disarankan untuk klarifikasi input frekuensi (19 event x 1.440 menit) saat meeting L1/L2.
          </li>
          <li>
            <b>Kesiapan Trigger:</b> Sebanyak <b>389 aktivitas</b> telah Fully Triggered dan <b>256 aktivitas</b> Not Yet Triggered terverifikasi pada baseline 667 use case Agent Harness. Sebanyak 2.793 aktivitas lainnya belum memuat kolom pemicu langsung pada data mentah.
          </li>
        </ul>
        <p className="text-[11px] text-[#73817e] mt-4 pt-3 border-t border-[#e6ecea]/60 m-0">
          Catatan: Sistem WORKLENS memproses data operasional secara deterministik tanpa manipulasi. Seluruh rekomendasi teknologi berstatus indikasi analitis dan bukan keputusan implementasi final.
        </p>
      </motion.section>

      {/* Slide-in Detail Drawer */}
      <ActivityDetailDrawer
        activity={selectedActivity}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </motion.div>
  );
};
