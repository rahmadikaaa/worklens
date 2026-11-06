import React, { useEffect, useState } from 'react';
import { Activity, BookOpen, Cpu, Database, RefreshCw, ShieldCheck, Sparkles } from 'lucide-react';
import { FileUpload } from './components/FileUpload';
import { SourceHistory } from './components/SourceHistory';
import { EnrichmentDiscovery } from './components/EnrichmentDiscovery';
import type { HealthInfo, FileUploadResponse } from './types';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'pipeline' | 'discovery'>('discovery');
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [latestUpload, setLatestUpload] = useState<FileUploadResponse | null>(null);
  const [historyRefreshKey, setHistoryRefreshKey] = useState<number>(0);

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
          <div className="flex items-center space-x-6">
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

            <nav className="hidden sm:flex items-center space-x-1">
              <button
                onClick={() => setCurrentView('discovery')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  currentView === 'discovery'
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <BookOpen className="h-3.5 w-3.5 text-sky-400" />
                <span>Enrichment Discovery</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">
                  667 Validated
                </span>
              </button>
              <button
                onClick={() => setCurrentView('pipeline')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  currentView === 'pipeline'
                    ? 'bg-slate-800 text-slate-100 border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Database className="h-3.5 w-3.5" />
                <span>Ingestion & Pipelines</span>
              </button>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {latestUpload && (
              <div className="hidden md:flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800">
                <span className="text-slate-500">Active File:</span>
                <span className="font-mono text-sky-400 truncate max-w-[160px]" title={latestUpload.saved_filename}>
                  {latestUpload.saved_filename}
                </span>
              </div>
            )}
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

      {/* Main Content View Switcher */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
        {currentView === 'discovery' ? (
          <EnrichmentDiscovery />
        ) : (
          <>
            {/* Hero Header */}
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

            {/* Manual Assessment File Upload (P1) */}
            <section aria-label="File Upload">
              <FileUpload
                onUploadSuccess={(res) => {
                  setLatestUpload(res);
                  setHistoryRefreshKey((prev) => prev + 1);
                }}
              />
            </section>

            {/* Source History & Versioning (P3) */}
            <section aria-label="Source History">
              <SourceHistory
                refreshTrigger={historyRefreshKey}
                onSelectSnapshot={(snapshot) => {
                  setLatestUpload({
                    filename: snapshot.original_filename,
                    saved_filename: snapshot.stored_filename,
                    file_format: snapshot.file_format,
                    file_size: snapshot.file_size,
                    upload_status: 'success',
                    message: 'Loaded from source snapshot history',
                    uploaded_at: snapshot.uploaded_at,
                    snapshot_id: snapshot.snapshot_id,
                    source_id: snapshot.source_id,
                    snapshot: snapshot,
                  });
                }}
              />
            </section>
          </>
        )}
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

