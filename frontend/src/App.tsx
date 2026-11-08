import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  BookOpen,
  Cpu,
  Database,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Table,
  TrendingDown,
} from 'lucide-react';
import { FileUpload } from './components/FileUpload';
import { SourceHistory } from './components/SourceHistory';
import { EnrichmentDiscovery } from './components/EnrichmentDiscovery';
import { ExecutiveOverview } from './components/ExecutiveOverview';
import { WorkloadAnalytics } from './components/WorkloadAnalytics';
import { ActivityExplorer } from './components/ActivityExplorer';
import { DataQualityReconciliation } from './components/DataQualityReconciliation';
import type { HealthInfo } from './types';

export type DashboardTab =
  | 'overview'
  | 'workload'
  | 'activities'
  | 'quality'
  | 'pipeline'
  | 'discovery';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<DashboardTab>('overview');
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [historyRefreshKey, setHistoryRefreshKey] = useState<number>(0);

  // Active filter state passed to Activity Explorer when drilling down
  const [explorerFilter, setExplorerFilter] = useState<{
    app?: string;
    criticality?: string;
    calcStatus?: string;
    automationStatus?: string;
    dept?: string;
  }>({});

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/health');
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }
      const data: HealthInfo = await res.json();
      setHealth(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleNavigateToTab = (tab: string, filter?: Record<string, string>) => {
    if (filter) {
      setExplorerFilter(filter);
    }
    setCurrentView(tab as DashboardTab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navItems = [
    { id: 'overview', label: 'Peluang Otomasi', icon: <Activity className="h-3.5 w-3.5" /> },
    { id: 'workload', label: 'Workload Analytics', icon: <TrendingDown className="h-3.5 w-3.5" /> },
    { id: 'activities', label: 'Activity Explorer', icon: <Table className="h-3.5 w-3.5" /> },
    { id: 'quality', label: 'Data Quality', icon: <ShieldAlert className="h-3.5 w-3.5" /> },
    { id: 'discovery', label: 'Discovery Baseline', icon: <BookOpen className="h-3.5 w-3.5" />, badge: '667 Verified' },
    { id: 'pipeline', label: 'Pipelines & Upload', icon: <Database className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="min-h-screen bg-[#f5f7f8] text-[#172321] flex flex-col font-sans selection:bg-[#e3f4ef] selection:text-[#087f70]">
      {/* Topbar matching reference */}
      <header className="border-b border-[#e6ecea] bg-white/95 backdrop-blur sticky top-0 z-40 shadow-xs">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8 h-18 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center space-x-6">
            {/* Brand Logo & Title */}
            <div
              onClick={() => setCurrentView('overview')}
              className="flex items-center gap-3 cursor-pointer group select-none"
            >
              <div className="w-[38px] h-[38px] rounded-xl bg-[#103f38] text-white grid place-items-center font-extrabold text-base tracking-tighter shadow-sm group-hover:scale-105 transition-transform duration-200">
                W
              </div>
              <div>
                <div className="font-extrabold tracking-wide text-sm text-[#172321] leading-none">
                  WORKLENS
                </div>
                <small className="block text-[#73817e] text-[10px] font-semibold tracking-[0.12em] uppercase mt-1">
                  Operational Intelligence
                </small>
              </div>
            </div>

            {/* Sliding Active Navigation Tabs */}
            <nav className="hidden xl:flex items-center space-x-1 pl-4 border-l border-[#e6ecea]">
              {navItems.map((item) => {
                const isActive = currentView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentView(item.id as DashboardTab)}
                    className={`relative px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors duration-150 ${
                      isActive ? 'text-[#087f70]' : 'text-[#73817e] hover:text-[#172321] hover:bg-[#edf1ef]/60'
                    }`}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="activeNavTab"
                        transition={{ type: 'spring', stiffness: 450, damping: 35 }}
                        className="absolute inset-0 bg-[#e3f4ef] border border-[#b2e2d7] rounded-xl shadow-xs"
                      />
                    )}
                    <span className="relative z-10">{item.icon}</span>
                    <span className="relative z-10">{item.label}</span>
                    {item.badge && (
                      <span className="relative z-10 text-[10px] px-1.5 py-0.2 rounded-full bg-white text-[#087f70] font-bold border border-[#b2e2d7]">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Header Status Bar & Actions */}
          <div className="flex items-center space-x-2.5">
            <div className="hidden sm:flex items-center space-x-2 text-xs text-[#73817e] bg-[#f8fafb] px-3 py-1.5 rounded-xl border border-[#e6ecea]">
              <span className="text-[11px]">Snapshot:</span>
              <span className="font-semibold text-[#172321]">3.460 SOPs</span>
            </div>

            <button
              onClick={fetchHealth}
              disabled={loading}
              className="inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-[#edf1ef] text-[#172321] border border-[#e6ecea] transition shadow-xs"
              title="Refresh health and dataset connection"
            >
              <RefreshCw className={`h-3 w-3 mr-1.5 text-[#087f70] ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Sync</span>
            </button>

            <div className="flex items-center space-x-1.5 text-xs bg-white border border-[#e6ecea] px-2.5 py-1.5 rounded-xl">
              <span
                className={`h-2 w-2 rounded-full ${
                  health?.status === 'ok' ? 'bg-[#087f70] shadow-sm shadow-[#087f70]/50' : 'bg-amber-400'
                }`}
              />
              <span className="text-[#73817e] text-[11px] font-medium hidden md:inline">
                {health ? `${health.environment}` : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Horizontal Navigation */}
        <div className="xl:hidden flex overflow-x-auto px-4 py-2 border-t border-[#e6ecea] space-x-2 scrollbar-none bg-[#f8fafb]">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id as DashboardTab)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 shrink-0 transition-colors ${
                currentView === item.id
                  ? 'bg-[#103f38] text-white'
                  : 'bg-white text-[#73817e] border border-[#e6ecea]'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </header>

      {/* Main Content Area with Page Transitions */}
      <main className="flex-1 w-full">
        <AnimatePresence mode="wait">
          {currentView === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
            >
              <ExecutiveOverview onNavigateToTab={handleNavigateToTab} />
            </motion.div>
          )}

          {currentView === 'workload' && (
            <motion.div
              key="workload"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="max-w-[1440px] mx-auto px-4 sm:px-8 py-7"
            >
              <WorkloadAnalytics onNavigateToTab={handleNavigateToTab} />
            </motion.div>
          )}

          {currentView === 'activities' && (
            <motion.div
              key="activities"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="max-w-[1440px] mx-auto px-4 sm:px-8 py-7"
            >
              <ActivityExplorer initialFilter={explorerFilter} />
            </motion.div>
          )}

          {currentView === 'quality' && (
            <motion.div
              key="quality"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="max-w-[1440px] mx-auto px-4 sm:px-8 py-7"
            >
              <DataQualityReconciliation onNavigateToTab={handleNavigateToTab} />
            </motion.div>
          )}

          {currentView === 'discovery' && (
            <motion.div
              key="discovery"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="max-w-[1440px] mx-auto px-4 sm:px-8 py-7"
            >
              <EnrichmentDiscovery />
            </motion.div>
          )}

          {currentView === 'pipeline' && (
            <motion.div
              key="pipeline"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="max-w-[1440px] mx-auto px-4 sm:px-8 py-7 space-y-8"
            >
              {/* Hero Header */}
              <div className="relative overflow-hidden rounded-2xl border border-[#e6ecea] bg-white p-8 shadow-sm">
                <div className="max-w-3xl space-y-3">
                  <div className="inline-flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-[#087f70] bg-[#e3f4ef] px-3 py-1 rounded-full">
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Workload Intelligence Platform</span>
                  </div>
                  <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-[#172321]">
                    Deterministic Processing & Change Detection
                  </h1>
                  <p className="text-[#73817e] text-sm sm:text-base leading-relaxed">
                    WORKLENS ingests automation assessments, strictly calculates 6 derived workload metrics, tracks deltas via SHA-256 content hashing, and generates actionable AI qualitative reviews without touching source data.
                  </p>
                </div>

                {error && (
                  <div className="mt-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
                    <ShieldCheck className="h-4 w-4 shrink-0 text-rose-500" />
                    <span>Backend connection status: {error} (ensure backend is running on port 8000).</span>
                  </div>
                )}
              </div>

              {/* Feature Grid / Core Modules */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="rounded-2xl border border-[#e6ecea] bg-white p-6 space-y-3 shadow-sm">
                  <div className="h-8 w-8 rounded-lg bg-[#e3f4ef] text-[#087f70] flex items-center justify-center">
                    <Cpu className="h-4 w-4" />
                  </div>
                  <h3 className="font-bold text-[#172321] text-sm">M1 — Deterministic Enrichment</h3>
                  <p className="text-xs text-[#73817e] leading-relaxed">
                    Calculates Workload Saved, Reduction %, and Annualized Savings following strict 6-priority rules. Zero arithmetic guessing.
                  </p>
                  <div className="text-[11px] font-semibold text-[#087f70] pt-2">✓ Business logic locked</div>
                </div>

                <div className="rounded-2xl border border-[#e6ecea] bg-white p-6 space-y-3 shadow-sm">
                  <div className="h-8 w-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
                    <Database className="h-4 w-4" />
                  </div>
                  <h3 className="font-bold text-[#172321] text-sm">M2 — Change Detection</h3>
                  <p className="text-xs text-[#73817e] leading-relaxed">
                    Strict row identity gate by activity_id and SHA-256 hashing. Classifies rows into UNCHANGED, MODIFIED, ADDED, DELETED, or REVIEW_REQUIRED.
                  </p>
                  <div className="text-[11px] font-semibold text-[#087f70] pt-2">✓ Contract verified</div>
                </div>

                <div className="rounded-2xl border border-[#e6ecea] bg-white p-6 space-y-3 shadow-sm">
                  <div className="h-8 w-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <h3 className="font-bold text-[#172321] text-sm">M3 — AI Qualitative Reviewer</h3>
                  <p className="text-xs text-[#73817e] leading-relaxed">
                    Audits Data Quality, Assessment Consistency, and Automation Opportunities. Offline mock mode enabled by default.
                  </p>
                  <div className="text-[11px] font-semibold text-[#087f70] pt-2">✓ Sanitization & privacy ready</div>
                </div>
              </div>

              {/* Manual Assessment File Upload (P1) */}
              <section aria-label="File Upload">
                <FileUpload
                  onUploadSuccess={() => {
                    setHistoryRefreshKey((prev) => prev + 1);
                  }}
                />
              </section>

              {/* Source History & Versioning (P3) */}
              <section aria-label="Source History">
                <SourceHistory
                  refreshTrigger={historyRefreshKey}
                  onSelectSnapshot={() => {
                    // Selection callback
                  }}
                />
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#e6ecea] py-5 bg-white mt-auto">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-[#73817e]">
          <span>WORKLENS — Workload & Automation Intelligence</span>
          <span className="font-medium">Clean Architecture • L1 Operations</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
