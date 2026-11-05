import React, { useEffect, useState } from 'react';
import { Activity, Cpu, Database, FileSpreadsheet, ShieldCheck, Sparkles, RefreshCw } from 'lucide-react';
import type { HealthInfo } from './types';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <Activity className="h-5 w-5" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-white">WORKLENS</span>
              <span className="ml-2 text-xs uppercase px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono">
                v1.0.0
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={fetchHealth}
              disabled={loading}
              className="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh Status
            </button>
            <div className="flex items-center space-x-2 text-xs">
              <span
                className={`h-2 w-2 rounded-full ${
                  health?.status === 'ok' ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-amber-400'
                }`}
              />
              <span className="text-slate-400">
                {health ? `${health.environment} (${health.mock_mode ? 'mock' : 'live'})` : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Header */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
        <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-950 to-slate-900/60 p-8">
          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-sky-400 bg-sky-500/10 px-3 py-1 rounded-full border border-sky-500/20">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Workload Intelligence Platform</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              Deterministic Processing & Qualitative Assessment
            </h1>
            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              WORKLENS ingests automation assessments, strictly calculates 6 derived workload metrics, tracks deltas via SHA-256 content hashing, and generates actionable AI qualitative reviews without touching source data.
            </p>
          </div>

          {error && (
            <div className="mt-6 p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 shrink-0 text-rose-400" />
              <span>Backend connection status: {error} (ensure backend is running on port 8000).</span>
            </div>
          )}
        </div>

        {/* Feature Grid / Core Modules */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-6 space-y-3">
            <div className="h-8 w-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
              <Cpu className="h-4 w-4" />
            </div>
            <h3 className="font-semibold text-white text-sm">M1 — Deterministic Enrichment</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Calculates Workload Saved, Reduction %, and Annualized Savings following strict 6-priority rules. Zero arithmetic guessing.
            </p>
            <div className="text-[11px] font-mono text-emerald-400 pt-2">✓ Business logic locked</div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-6 space-y-3">
            <div className="h-8 w-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center border border-amber-500/20">
              <Database className="h-4 w-4" />
            </div>
            <h3 className="font-semibold text-white text-sm">M2 — Change Detection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Strict row identity gate by activity_id and SHA-256 hashing. Classifies rows into UNCHANGED, MODIFIED, ADDED, DELETED, or REVIEW_REQUIRED.
            </p>
            <div className="text-[11px] font-mono text-emerald-400 pt-2">✓ Contract verified</div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-6 space-y-3">
            <div className="h-8 w-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
              <Sparkles className="h-4 w-4" />
            </div>
            <h3 className="font-semibold text-white text-sm">M3 — AI Qualitative Reviewer</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Audits Data Quality, Assessment Consistency, and Automation Opportunities. Offline mock mode enabled by default.
            </p>
            <div className="text-[11px] font-mono text-emerald-400 pt-2">✓ Sanitization & privacy ready</div>
          </div>
        </div>

        {/* Manual Upload Preview */}
        <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <FileSpreadsheet className="h-5 w-5 text-sky-400" />
              <h2 className="font-semibold text-sm text-white">Manual Assessment Ingestion</h2>
            </div>
            <span className="text-xs text-slate-500 font-mono">Manual JSON / CSV</span>
          </div>
          <div className="py-8 text-center border-2 border-dashed border-slate-800 rounded-lg mt-4 bg-slate-900/30">
            <p className="text-xs text-slate-400">
              Drag & drop assessment JSON/CSV here, or click to browse.
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              Source data remains 100% immutable. No OneDrive sync required.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between text-xs text-slate-500">
          <span>WORKLENS — Workload Intelligence Platform</span>
          <span className="font-mono">Clean Architecture Baseline</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
