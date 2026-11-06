import React, { useEffect, useState, useMemo } from 'react';
import {
  History,
  BookOpen,
  Download,
  Search,
  RefreshCw,
  AlertCircle,
  FileCode2,
  FileSpreadsheet,
  Clock,
  Calendar,
  Layers,
  Columns,
  Info,
  X,
  Loader2,
  HardDrive,
  Copy,
  Check,
  GitCompare,
  ShieldCheck,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import type {
  SourceSnapshot,
  FileParseResponse,
  IncrementalProcessResponse,
} from '../types';

interface SourceHistoryProps {
  refreshTrigger?: number;
  onSelectSnapshot?: (snapshot: SourceSnapshot) => void;
  onParseSuccess?: (result: FileParseResponse, snapshot: SourceSnapshot) => void;
}

export const SourceHistory: React.FC<SourceHistoryProps> = ({
  refreshTrigger = 0,
  onSelectSnapshot,
  onParseSuccess,
}) => {
  const [snapshots, setSnapshots] = useState<SourceSnapshot[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter/search
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Selected snapshot for inspection
  const [selectedSnapshot, setSelectedSnapshot] = useState<SourceSnapshot | null>(null);

  // Parsing state (P2)
  const [parsingId, setParsingId] = useState<string | null>(null);
  const [parseResult, setParseResult] = useState<FileParseResponse | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);

  // Change Detection & Incremental Processing state (P4)
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [processResult, setProcessResult] = useState<IncrementalProcessResponse | null>(null);
  const [processError, setProcessError] = useState<string | null>(null);

  // Copied hash tooltip state
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const fetchSnapshots = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/snapshots');
      if (!response.ok) {
        throw new Error(`Failed to load snapshots (HTTP ${response.status})`);
      }
      const data: SourceSnapshot[] = await response.json();
      setSnapshots(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error fetching snapshot history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSnapshots();
  }, [refreshTrigger]);

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash).then(() => {
      setCopiedHash(hash);
      setTimeout(() => setCopiedHash(null), 2000);
    });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  const formatDate = (isoString?: string | null): string => {
    if (!isoString) return 'N/A';
    try {
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return isoString;
      return d.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const handleReadData = async (snapshot: SourceSnapshot) => {
    setSelectedSnapshot(snapshot);
    setParsingId(snapshot.snapshot_id);
    setParseError(null);
    setParseResult(null);

    if (onSelectSnapshot) {
      onSelectSnapshot(snapshot);
    }

    try {
      const response = await fetch(`/api/v1/snapshots/${encodeURIComponent(snapshot.snapshot_id)}/parse`, {
        method: 'POST',
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `Parsing failed with HTTP ${response.status}`);
      }

      const parsed = data as FileParseResponse;
      setParseResult(parsed);
      if (onParseSuccess) {
        onParseSuccess(parsed, snapshot);
      }
    } catch (err: unknown) {
      setParseError(err instanceof Error ? err.message : 'Failed to read snapshot data.');
    } finally {
      setParsingId(null);
    }
  };

  const handleProcessIncremental = async (snapshot: SourceSnapshot) => {
    setSelectedSnapshot(snapshot);
    setProcessingId(snapshot.snapshot_id);
    setProcessError(null);
    setProcessResult(null);

    if (onSelectSnapshot) {
      onSelectSnapshot(snapshot);
    }

    try {
      const response = await fetch(`/api/v1/snapshots/${encodeURIComponent(snapshot.snapshot_id)}/process`, {
        method: 'POST',
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `Incremental processing failed with HTTP ${response.status}`);
      }

      const procData = data as IncrementalProcessResponse;
      setProcessResult(procData);
    } catch (err: unknown) {
      setProcessError(err instanceof Error ? err.message : 'Incremental processing failed.');
    } finally {
      setProcessingId(null);
    }
  };

  const filteredSnapshots = useMemo(() => {
    if (!searchQuery.trim()) return snapshots;
    const q = searchQuery.toLowerCase();
    return snapshots.filter(
      (s) =>
        s.original_filename.toLowerCase().includes(q) ||
        s.stored_filename.toLowerCase().includes(q) ||
        s.source_id.toLowerCase().includes(q) ||
        s.snapshot_id.toLowerCase().includes(q)
    );
  }, [snapshots, searchQuery]);

  return (
    <div className="w-full rounded-2xl border border-slate-800 bg-slate-950/70 p-6 sm:p-8 backdrop-blur shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <History className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
                <span>Source History & Versioning</span>
                <span className="text-xs font-mono font-normal px-2 py-0.5 rounded-full bg-slate-800 text-sky-400 border border-slate-700">
                  {snapshots.length} {snapshots.length === 1 ? 'Snapshot' : 'Snapshots'}
                </span>
              </h2>
              <p className="text-sm text-slate-400 mt-0.5">
                Audit-ready immutable snapshots with M2 change detection and incremental processing.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Search bar */}
          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter snapshots..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50 w-44 sm:w-56"
            />
          </div>

          {/* Refresh button */}
          <button
            onClick={fetchSnapshots}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition disabled:opacity-50"
            title="Refresh snapshot list"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300 flex items-start justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchSnapshots}
            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 font-medium"
          >
            Retry
          </button>
        </div>
      )}

      {/* Snapshots Table */}
      {loading && snapshots.length === 0 ? (
        <div className="py-12 flex flex-col items-center justify-center space-y-3 text-slate-400 text-xs">
          <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
          <span>Loading snapshot records...</span>
        </div>
      ) : snapshots.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 p-10 text-center space-y-3">
          <div className="h-10 w-10 rounded-full bg-slate-900 border border-slate-800 mx-auto flex items-center justify-center text-slate-500">
            <HardDrive className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-300">No source snapshots available</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Upload an assessment file (.json or .csv) above to create an audit-grade immutable snapshot.
            </p>
          </div>
        </div>
      ) : filteredSnapshots.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-500 border border-slate-800/60 rounded-xl">
          No snapshots matching &ldquo;{searchQuery}&rdquo;. Try another filter query.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800/80 bg-slate-900/40">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">File Name & Source</th>
                <th className="py-3 px-4">Format & Size</th>
                <th className="py-3 px-4">Uploaded / Server Time</th>
                <th className="py-3 px-4">Generated Time</th>
                <th className="py-3 px-4">Content Hash (SHA-256)</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredSnapshots.map((s) => {
                const isSelected = selectedSnapshot?.snapshot_id === s.snapshot_id;
                const isParsing = parsingId === s.snapshot_id;
                const isProcessing = processingId === s.snapshot_id;

                return (
                  <tr
                    key={s.snapshot_id}
                    className={`transition hover:bg-slate-800/40 ${
                      isSelected ? 'bg-sky-500/10 border-l-2 border-sky-400' : ''
                    }`}
                  >
                    {/* Filename & Source ID */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-start space-x-2.5">
                        <div className="mt-0.5 shrink-0">
                          {s.file_format === 'json' ? (
                            <FileCode2 className="h-4 w-4 text-amber-400" />
                          ) : (
                            <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
                          )}
                        </div>
                        <div className="space-y-0.5 max-w-[220px] sm:max-w-[280px]">
                          <span
                            className="font-medium text-slate-100 truncate block font-mono"
                            title={s.original_filename}
                          >
                            {s.original_filename}
                          </span>
                          <div className="flex items-center space-x-2 text-[10px] text-slate-500">
                            <span className="font-mono truncate" title={s.stored_filename}>
                              stored: {s.stored_filename}
                            </span>
                            <span>•</span>
                            <span className="font-semibold text-slate-400">
                              src: {s.source_id}
                            </span>
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Format & Size */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="space-y-1">
                        <span
                          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold font-mono uppercase ${
                            s.file_format === 'json'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          }`}
                        >
                          {s.file_format}
                        </span>
                        <div className="text-[11px] font-mono text-slate-400">
                          {formatFileSize(s.file_size)}
                        </div>
                      </div>
                    </td>

                    {/* Uploaded At */}
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-300">
                      <div className="flex items-center space-x-1.5 text-slate-400">
                        <Clock className="h-3 w-3 text-slate-500 shrink-0" />
                        <span className="font-mono text-[11px]">{formatDate(s.uploaded_at)}</span>
                      </div>
                    </td>

                    {/* Generated At */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {s.generated_at ? (
                        <div className="flex items-center space-x-1.5 text-sky-400">
                          <Calendar className="h-3 w-3 text-sky-400 shrink-0" />
                          <span className="font-mono text-[11px]">{formatDate(s.generated_at)}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500 font-mono text-[11px] italic">
                          Null (Manual)
                        </span>
                      )}
                    </td>

                    {/* Content Hash */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="flex items-center space-x-1.5">
                        <span
                          className="font-mono text-[11px] text-slate-400 hover:text-slate-200 cursor-help"
                          title={`SHA-256: ${s.content_hash}`}
                        >
                          {s.content_hash.slice(0, 10)}...{s.content_hash.slice(-6)}
                        </span>
                        <button
                          onClick={() => handleCopyHash(s.content_hash)}
                          className="text-slate-500 hover:text-slate-300 p-0.5 rounded transition"
                          title="Copy full SHA-256 hash"
                        >
                          {copiedHash === s.content_hash ? (
                            <Check className="h-3 w-3 text-emerald-400" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </button>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        {s.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 whitespace-nowrap text-right">
                      <div className="inline-flex items-center space-x-2">
                        {/* Compare & Process (P4) */}
                        <button
                          type="button"
                          onClick={() => handleProcessIncremental(s)}
                          disabled={isProcessing}
                          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 shadow-sm shadow-sky-500/20 transition disabled:opacity-50"
                          title="Run M2 Change Detection and Incremental Processing"
                        >
                          {isProcessing ? (
                            <>
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              <span>Processing...</span>
                            </>
                          ) : (
                            <>
                              <GitCompare className="h-3.5 w-3.5" />
                              <span>Compare & Process</span>
                            </>
                          )}
                        </button>

                        {/* Read Data (P2) */}
                        <button
                          type="button"
                          onClick={() => handleReadData(s)}
                          disabled={isParsing}
                          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-sm shadow-emerald-500/20 transition disabled:opacity-50"
                          title="Parse and inspect snapshot schema"
                        >
                          {isParsing ? (
                            <>
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              <span>Reading...</span>
                            </>
                          ) : (
                            <>
                              <BookOpen className="h-3.5 w-3.5" />
                              <span>Read Data</span>
                            </>
                          )}
                        </button>

                        {/* Download */}
                        <a
                          href={`/api/v1/snapshots/${encodeURIComponent(s.snapshot_id)}/download`}
                          download={s.original_filename}
                          className="inline-flex items-center p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800 transition"
                          title="Download original file"
                        >
                          <Download className="h-3.5 w-3.5" />
                        </a>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Processing Error Alert */}
      {processError && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300 flex items-start space-x-3">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
          <div className="space-y-1 flex-1">
            <p className="font-semibold text-rose-200">Change Detection / Incremental Processing Failed</p>
            <p className="leading-relaxed">{processError}</p>
          </div>
          {selectedSnapshot && (
            <button
              onClick={() => handleProcessIncremental(selectedSnapshot)}
              disabled={Boolean(processingId)}
              className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 font-medium"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Change Report & Incremental Processing Results (P4) */}
      {processResult && selectedSnapshot && (
        <div className="rounded-xl border border-indigo-500/30 bg-slate-900/80 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <GitCompare className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <span>Change Detection & Incremental Processing Report</span>
                </h3>
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 mt-0.5">
                  <span className="font-mono text-sky-400 font-semibold">{selectedSnapshot.original_filename}</span>
                  <span>•</span>
                  <span>
                    Baseline:{' '}
                    {processResult.baseline_snapshot_id ? (
                      <span className="font-mono text-slate-300">{processResult.baseline_snapshot_id}</span>
                    ) : (
                      <span className="italic text-slate-500">None (Initial Baseline Run)</span>
                    )}
                  </span>
                  <span>•</span>
                  <span className="text-[11px] font-mono text-slate-500">Run ID: {processResult.run_id}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {processResult.change_report.identical_content_hash && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  <Zap className="h-3 w-3 mr-1" />
                  Identical Hash Bypass
                </span>
              )}
              <span
                className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase ${
                  processResult.status === 'NO_CHANGE'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-sky-500/10 text-sky-400 border border-sky-500/30'
                }`}
              >
                {processResult.status}
              </span>
              <button
                onClick={() => setProcessResult(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
                title="Dismiss change report"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Status Message */}
          <div className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
            <span className="flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
              <span>{processResult.change_report.message}</span>
            </span>
            <span className="font-mono text-[11px] text-slate-500">
              Logic Version: v{processResult.logic_version}
            </span>
          </div>

          {/* Counts Grid (M2 Statuses + Incremental Execution KPIs) */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            <div className="rounded-lg bg-slate-950/60 p-3 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Total Evaluated</span>
              <span className="text-xl font-extrabold text-white font-mono mt-0.5 block">
                {processResult.summary_counts.total_current_rows}
              </span>
            </div>
            <div className="rounded-lg bg-emerald-950/20 p-3 border border-emerald-500/30">
              <span className="text-[11px] text-emerald-400 block">Unchanged (Reused)</span>
              <span className="text-xl font-extrabold text-emerald-300 font-mono mt-0.5 block">
                {processResult.summary_counts.unchanged}
              </span>
            </div>
            <div className="rounded-lg bg-sky-950/20 p-3 border border-sky-500/30">
              <span className="text-[11px] text-sky-400 block">Modified (Processed)</span>
              <span className="text-xl font-extrabold text-sky-300 font-mono mt-0.5 block">
                {processResult.summary_counts.modified}
              </span>
            </div>
            <div className="rounded-lg bg-indigo-950/20 p-3 border border-indigo-500/30">
              <span className="text-[11px] text-indigo-400 block">Added (Processed)</span>
              <span className="text-xl font-extrabold text-indigo-300 font-mono mt-0.5 block">
                {processResult.summary_counts.added}
              </span>
            </div>
            <div className="rounded-lg bg-rose-950/20 p-3 border border-rose-500/30">
              <span className="text-[11px] text-rose-400 block">Deleted (Archived)</span>
              <span className="text-xl font-extrabold text-rose-300 font-mono mt-0.5 block">
                {processResult.summary_counts.deleted}
              </span>
            </div>
            <div className="rounded-lg bg-amber-950/20 p-3 border border-amber-500/30">
              <span className="text-[11px] text-amber-400 block">Review Required</span>
              <span className="text-xl font-extrabold text-amber-300 font-mono mt-0.5 block">
                {processResult.summary_counts.review_required}
              </span>
            </div>
            <div className="rounded-lg bg-sky-500/10 p-3 border border-sky-500/40">
              <span className="text-[11px] text-sky-300 font-semibold block">Activities Reprocessed</span>
              <span className="text-xl font-black text-sky-400 font-mono mt-0.5 block">
                {processResult.reprocessed_records}
              </span>
            </div>
          </div>

          {/* Change Details Table */}
          {processResult.change_report.changes.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <Columns className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Activity Change Breakdown ({processResult.change_report.changes.length})</span>
                </span>
                <span className="text-[11px] text-slate-500">
                  Active Dataset Size: {processResult.total_active_records} rows
                </span>
              </div>

              <div className="max-h-64 overflow-y-auto rounded-lg border border-slate-800 bg-slate-950/40">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400 uppercase text-[10px] font-semibold sticky top-0">
                      <th className="py-2.5 px-3">Activity ID</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Change Details / Reason</th>
                      <th className="py-2.5 px-3">Content Hash</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                    {processResult.change_report.changes.map((change, idx) => {
                      const badgeColor =
                        change.classification === 'UNCHANGED'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : change.classification === 'MODIFIED'
                          ? 'bg-sky-500/10 text-sky-400 border-sky-500/20'
                          : change.classification === 'ADDED'
                          ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                          : change.classification === 'DELETED'
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/20';

                      return (
                        <tr key={`${change.activity_id}-${idx}`} className="hover:bg-slate-800/30">
                          <td className="py-2 px-3 font-semibold text-slate-200">
                            {change.activity_id || <span className="text-rose-400 italic font-sans">[MISSING]</span>}
                          </td>
                          <td className="py-2 px-3">
                            <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] border ${badgeColor}`}>
                              {change.classification}
                            </span>
                          </td>
                          <td className="py-2 px-3 font-sans text-xs text-slate-300">
                            {change.classification === 'MODIFIED' && change.modified_fields.length > 0 ? (
                              <div className="flex flex-wrap gap-1">
                                <span className="text-slate-400 mr-1 text-[11px]">Fields:</span>
                                {change.modified_fields.map((f) => (
                                  <span key={f} className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 font-mono text-[10px] text-sky-300">
                                    {f}
                                  </span>
                                ))}
                              </div>
                            ) : change.reason ? (
                              <span className="text-amber-400 font-mono text-[11px] flex items-center space-x-1">
                                <AlertTriangle className="h-3 w-3 inline" />
                                <span>{change.reason}</span>
                              </span>
                            ) : change.classification === 'DELETED' ? (
                              <span className="text-rose-400/80 text-[11px]">Removed from active dataset</span>
                            ) : change.classification === 'ADDED' ? (
                              <span className="text-indigo-400/80 text-[11px]">New activity ingested</span>
                            ) : (
                              <span className="text-slate-500 text-[11px]">Identical to baseline</span>
                            )}
                          </td>
                          <td className="py-2 px-3 text-slate-500 text-[10px]">
                            {change.content_hash ? `${change.content_hash.slice(0, 8)}...` : '—'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Parsing Error for selected snapshot */}
      {parseError && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300 flex items-start space-x-3">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
          <div className="space-y-1 flex-1">
            <p className="font-semibold text-rose-200">Snapshot Parsing Failed</p>
            <p className="leading-relaxed">{parseError}</p>
          </div>
          {selectedSnapshot && (
            <button
              onClick={() => handleReadData(selectedSnapshot)}
              disabled={Boolean(parsingId)}
              className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 font-medium"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Parsed Snapshot Inspector Details (P2 Integration) */}
      {parseResult && selectedSnapshot && (
        <div className="rounded-xl border border-sky-500/30 bg-slate-900/70 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                <Layers className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <span>Parsed Snapshot:</span>
                  <span className="font-mono text-sky-400">{selectedSnapshot.original_filename}</span>
                </h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  ID: {selectedSnapshot.snapshot_id} • SHA-256: {selectedSnapshot.content_hash.slice(0, 16)}...
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {parseResult.parsing_status}
              </span>
              <button
                onClick={() => setParseResult(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
                title="Dismiss parsed summary"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Counts Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800">
              <span className="text-xs text-slate-400 block">Total Records</span>
              <span className="text-2xl font-extrabold text-white font-mono mt-1 block">
                {parseResult.total_rows.toLocaleString()}
              </span>
            </div>
            <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800">
              <span className="text-xs text-slate-400 block">Total Columns</span>
              <span className="text-2xl font-extrabold text-sky-400 font-mono mt-1 block">
                {parseResult.total_columns}
              </span>
            </div>
            <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800">
              <span className="text-xs text-slate-400 block">Format</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono mt-1 block uppercase">
                {parseResult.file_format}
              </span>
            </div>
            <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800">
              <span className="text-xs text-slate-400 block">Target File</span>
              <span
                className="text-xs font-mono text-slate-300 mt-2 block truncate font-medium"
                title={parseResult.filename}
              >
                {parseResult.filename}
              </span>
            </div>
          </div>

          {/* Metadata Section (if present) */}
          {Object.keys(parseResult.metadata).length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-wider text-amber-400">
                <Info className="h-3.5 w-3.5" />
                <span>File Metadata Envelope</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                {Object.entries(parseResult.metadata).map(([key, value]) => (
                  <div key={key} className="bg-slate-950/40 rounded-lg p-2.5 border border-slate-800/80">
                    <span className="text-slate-400 block font-mono text-[11px]">{key}</span>
                    <span className="text-slate-200 font-medium break-all block mt-0.5">
                      {typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detected Columns List */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
              <Columns className="h-3.5 w-3.5 text-sky-400" />
              <span>Detected Columns ({parseResult.columns.length})</span>
            </div>
            {parseResult.columns.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {parseResult.columns.map((col, index) => (
                  <span
                    key={`${col}-${index}`}
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono bg-slate-950 border border-slate-800 text-slate-300 hover:border-sky-500/40 transition"
                  >
                    <span className="text-slate-500 mr-1.5 text-[10px]">{index + 1}.</span>
                    <span>{col}</span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No columns detected in snapshot file.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
