import React, { useState, useRef, ChangeEvent, DragEvent } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  FileCode2,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Loader2,
  HardDrive,
  BookOpen,
  Columns,
  Layers,
  Info,
  X,
} from 'lucide-react';
import type { FileUploadResponse, FileParseResponse } from '../types';

interface FileUploadProps {
  onUploadSuccess?: (result: FileUploadResponse) => void;
  onParseSuccess?: (result: FileParseResponse) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onParseSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<FileUploadResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Parsing state (P2)
  const [isParsing, setIsParsing] = useState<boolean>(false);
  const [parseResult, setParseResult] = useState<FileParseResponse | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  const getFileFormat = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext || 'unknown';
  };

  const validateFile = (file: File): string | null => {
    const format = getFileFormat(file.name);
    if (!['json', 'csv'].includes(format)) {
      return `Unsupported file format (.${format}). Please select a .json or .csv file.`;
    }
    if (file.size === 0) {
      return 'The selected file is empty (0 bytes). Please choose a valid assessment file.';
    }
    return null;
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const error = validateFile(file);
      setSelectedFile(file);
      setUploadResult(null);
      setParseResult(null);
      setParseError(null);
      setErrorMessage(error);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      const error = validateFile(file);
      setSelectedFile(file);
      setUploadResult(null);
      setParseResult(null);
      setParseError(null);
      setErrorMessage(error);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const validationErr = validateFile(selectedFile);
    if (validationErr) {
      setErrorMessage(validationErr);
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);
    setParseResult(null);
    setParseError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Upload failed with status HTTP ${response.status}`);
      }

      const res = data as FileUploadResponse;
      setUploadResult(res);
      if (onUploadSuccess) {
        onUploadSuccess(res);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'An unexpected error occurred during upload.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReadData = async () => {
    if (!uploadResult) return;

    setIsParsing(true);
    setParseError(null);

    try {
      const url = uploadResult.snapshot_id
        ? `/api/v1/snapshots/${encodeURIComponent(uploadResult.snapshot_id)}/parse`
        : `/api/v1/parse/${encodeURIComponent(uploadResult.saved_filename)}`;
      const response = await fetch(url, {
        method: 'POST',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Failed to read file (HTTP ${response.status})`);
      }

      const res = data as FileParseResponse;
      setParseResult(res);
      if (onParseSuccess) {
        onParseSuccess(res);
      }
    } catch (err: unknown) {
      setParseError(err instanceof Error ? err.message : 'Failed to read and parse assessment file.');
    } finally {
      setIsParsing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setUploadResult(null);
    setParseResult(null);
    setParseError(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full rounded-2xl border border-slate-800 bg-slate-950/70 p-6 sm:p-8 backdrop-blur shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <UploadCloud className="h-5 w-5 text-sky-400" />
            <span>Upload & Read Assessment File</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Ingest and inspect raw workload assessment data (.json or .csv) without modifying source content.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
            JSON / CSV
          </span>
          <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
            Max 10 MB
          </span>
        </div>
      </div>

      {/* Success View (Upload Completed) */}
      {uploadResult ? (
        <div className="space-y-6">
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-emerald-200">
                    File Uploaded Successfully
                  </h3>
                  <p className="text-xs text-emerald-400/80">
                    {uploadResult.message}
                  </p>
                </div>
              </div>
              <button
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>Upload Another File</span>
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
              <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                <span className="text-slate-400 block mb-1">Original Name</span>
                <span className="font-mono text-slate-200 truncate block font-medium" title={uploadResult.filename}>
                  {uploadResult.filename}
                </span>
              </div>
              <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                <span className="text-slate-400 block mb-1">Stored As</span>
                <span className="font-mono text-sky-300 truncate block font-medium" title={uploadResult.saved_filename}>
                  {uploadResult.saved_filename}
                </span>
              </div>
              <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                <span className="text-slate-400 block mb-1">File Format</span>
                <span className="uppercase font-mono text-emerald-300 font-bold">
                  {uploadResult.file_format}
                </span>
              </div>
              <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                <span className="text-slate-400 block mb-1">Size</span>
                <span className="font-mono text-slate-200 font-medium">
                  {formatFileSize(uploadResult.file_size)}
                </span>
              </div>
            </div>

            {uploadResult.snapshot_id && (
              <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
                <span className="font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                  <span className="text-slate-500 mr-1">Snapshot:</span>
                  <span className="text-sky-400">{uploadResult.snapshot_id}</span>
                </span>
                {uploadResult.snapshot?.generated_at && (
                  <span className="font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                    <span className="text-slate-500 mr-1">Generated:</span>
                    <span className="text-emerald-400">
                      {new Date(uploadResult.snapshot.generated_at).toLocaleString()}
                    </span>
                  </span>
                )}
                {uploadResult.snapshot?.content_hash && (
                  <span
                    className="font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800"
                    title={`SHA-256: ${uploadResult.snapshot.content_hash}`}
                  >
                    <span className="text-slate-500 mr-1">SHA-256:</span>
                    <span className="text-slate-300">
                      {uploadResult.snapshot.content_hash.slice(0, 12)}...
                    </span>
                  </span>
                )}
              </div>
            )}

            {/* Read Data Action Button */}
            {!parseResult && (
              <div className="pt-2 flex items-center justify-between border-t border-emerald-500/20">
                <div className="text-xs text-emerald-300/80">
                  Ready to inspect dataset structure and columns.
                </div>
                <button
                  type="button"
                  onClick={handleReadData}
                  disabled={isParsing}
                  className="inline-flex items-center space-x-2 px-5 py-2 rounded-lg text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20 transition disabled:opacity-50"
                >
                  {isParsing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Reading Data...</span>
                    </>
                  ) : (
                    <>
                      <BookOpen className="h-4 w-4" />
                      <span>Read Data</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Parsing Error Feedback */}
          {parseError && (
            <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300 flex items-start space-x-3">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
              <div className="space-y-1 flex-1">
                <p className="font-semibold text-rose-200">Parsing Failed</p>
                <p className="leading-relaxed">{parseError}</p>
              </div>
              <button
                onClick={handleReadData}
                disabled={isParsing}
                className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 font-medium"
              >
                Retry
              </button>
            </div>
          )}

          {/* Parsing Results Summary (P2) */}
          {parseResult && (
            <div className="rounded-xl border border-sky-500/30 bg-slate-900/60 p-6 space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center space-x-3">
                  <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                    <Layers className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">Parsed Data Summary</h3>
                    <p className="text-xs text-slate-400">{parseResult.message}</p>
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {parseResult.parsing_status}
                </span>
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
                  <span className="text-xs text-slate-400 block">File Format</span>
                  <span className="text-2xl font-extrabold text-emerald-400 font-mono mt-1 block uppercase">
                    {parseResult.file_format}
                  </span>
                </div>
                <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800">
                  <span className="text-xs text-slate-400 block">Target File</span>
                  <span className="text-xs font-mono text-slate-300 mt-2 block truncate font-medium" title={parseResult.filename}>
                    {parseResult.filename}
                  </span>
                </div>
              </div>

              {/* Metadata Section (if present) */}
              {Object.keys(parseResult.metadata).length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-wider text-amber-400">
                    <Info className="h-3.5 w-3.5" />
                    <span>File Metadata</span>
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
                  <p className="text-xs text-slate-500 italic">No columns detected in file.</p>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* File Selection & Drop Area */
        <div className="space-y-4">
          <input
            ref={fileInputRef}
            type="file"
            id="worklens-file-input"
            accept=".json,.csv,application/json,text/csv"
            onChange={handleFileChange}
            className="hidden"
          />

          {!selectedFile ? (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer transition flex flex-col items-center justify-center space-y-3 ${
                isDragging
                  ? 'border-sky-400 bg-sky-500/10'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/60'
              }`}
            >
              <div className="h-12 w-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                <UploadCloud className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-200">
                  <span className="text-sky-400 font-semibold hover:underline">Click to browse</span> or drag and drop
                </p>
                <p className="text-xs text-slate-500">
                  Supports JSON or CSV assessment files up to 10 MB
                </p>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 truncate">
                  <div className="h-10 w-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center shrink-0">
                    {getFileFormat(selectedFile.name) === 'json' ? (
                      <FileCode2 className="h-5 w-5 text-amber-400" />
                    ) : (
                      <FileSpreadsheet className="h-5 w-5 text-emerald-400" />
                    )}
                  </div>
                  <div className="truncate">
                    <p className="text-sm font-medium text-white truncate" title={selectedFile.name}>
                      {selectedFile.name}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-slate-400">
                      <span className="uppercase font-mono font-semibold text-slate-300">
                        {getFileFormat(selectedFile.name)}
                      </span>
                      <span>•</span>
                      <span>{formatFileSize(selectedFile.size)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleReset}
                    disabled={isUploading}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
                    title="Remove selected file"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Upload Action */}
              <div className="pt-2 flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleReset}
                  disabled={isUploading}
                  className="px-4 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleUpload}
                  disabled={isUploading || Boolean(errorMessage)}
                  className="inline-flex items-center space-x-2 px-5 py-2 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 shadow-lg shadow-sky-500/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <HardDrive className="h-4 w-4" />
                      <span>Upload File</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Feedback */}
      {errorMessage && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300 flex items-start space-x-3">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
          <div className="space-y-1 flex-1">
            <p className="font-semibold text-rose-200">Upload Issue</p>
            <p className="leading-relaxed">{errorMessage}</p>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-300 p-0.5 rounded"
            title="Dismiss error"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
