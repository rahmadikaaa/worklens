import React, { useEffect } from 'react';
import { motion, AnimatePresence, type Variants } from 'framer-motion';
import {
  Clock,
  Copy,
  ExternalLink,
  Workflow,
  X,
  FileText,
  Sparkles,
  Cpu,
  CheckCircle2,
  Lightbulb,
} from 'lucide-react';
import type { EnrichedActivity } from '../types';

interface ActivityDetailDrawerProps {
  activity: EnrichedActivity | null;
  isOpen: boolean;
  onClose: () => void;
}

const fmt = (v: number | string | undefined | null, digits: number = 0): string => {
  return Number(v || 0).toLocaleString('id-ID', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};

export const ActivityDetailDrawer: React.FC<ActivityDetailDrawerProps> = ({
  activity,
  isOpen,
  onClose,
}) => {
  // Close drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const calcStatus = activity?.['Workload Calculation Status'] || 'CALCULATED';
  const isHealthyCalc = calcStatus === 'CALCULATED' || calcStatus === 'ZERO_WORKLOAD';
  const bucketName = String(activity?.automation_bucket || 'Lainnya');
  const triggerStatus = String(activity?.status_triggered || 'Unmapped in Baseline');

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.05,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 8 },
    show: { opacity: 1, y: 0, transition: { duration: 0.22, ease: 'easeOut' } },
  };

  const durVal = Number(activity?.['Durasi (Menit)'] || 0);
  const evVal = Number(activity?.['Event Per Month'] || 0);
  const wlMin = Number(activity?.Workload || 0);
  const wlHours = wlMin / 60.0;

  return (
    <AnimatePresence>
      {isOpen && activity && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onClick={onClose}
            className="absolute inset-0 bg-[#172321]/40 backdrop-blur-sm"
          />

          {/* Drawer container */}
          <div className="fixed inset-y-0 right-0 max-w-full flex pl-8 sm:pl-10">
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
              className="w-screen max-w-2xl bg-white border-l border-[#e6ecea] shadow-2xl flex flex-col text-[#172321]"
            >
              {/* Header */}
              <div className="p-6 border-b border-[#e6ecea] bg-[#f8fafb] flex items-start justify-between">
                <div className="space-y-2 pr-4">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#e3f4ef] text-[#087f70]">
                      {String(activity.APPS || 'Application')}
                    </span>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#edf1ef] text-[#44524f]">
                      {String(activity['APP PRIORITY'] || 'Standard')}
                    </span>
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#103f38] text-white">
                      {bucketName}
                    </span>

                    {/* Quick-Win and Outlier badges */}
                    {activity.is_quick_win && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                        ⚡ Quick Win
                      </span>
                    )}
                    {activity.is_outlier && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 border border-rose-200">
                        ⚠️ Pencilan Ekstrim (456j)
                      </span>
                    )}
                    {activity.is_verified_baseline && (
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                        ✓ 667 Baseline
                      </span>
                    )}
                  </div>

                  <h2 className="text-lg font-bold text-[#172321] tracking-tight leading-snug">
                    {String(activity['ACTIVITY NAME'] || activity.activity_id)}
                  </h2>

                  <div className="flex items-center space-x-2 text-xs text-[#73817e] font-mono">
                    <span className="truncate max-w-[360px]" title={String(activity.activity_id)}>
                      ID: {String(activity.activity_id)}
                    </span>
                    <button
                      onClick={() => copyToClipboard(String(activity.activity_id))}
                      title="Copy Activity ID"
                      className="p-1 hover:text-[#172321] hover:bg-[#eef2f0] rounded transition"
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-[#73817e] hover:text-[#172321] hover:bg-[#eef2f0] transition"
                  aria-label="Close drawer"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Scrollable Body with Staggered Sections */}
              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="flex-1 overflow-y-auto p-6 space-y-6"
              >
                {/* Section 1: Benefit Statement & Rekomendasi Tindakan (Meeting Review) */}
                <motion.div
                  variants={itemVariants}
                  className="rounded-2xl border border-[#b2e2d7] bg-[#f0f9f6] p-5 space-y-4"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center space-x-2 text-sm font-bold text-[#103f38]">
                      <Sparkles className="h-4 w-4 text-[#087f70]" />
                      <span>Benefit Statement & Rekomendasi Eksekusi</span>
                    </div>

                    <span
                      className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                        triggerStatus === 'Fully Automated'
                          ? 'bg-[#10b981]/20 text-[#065f46] border border-[#10b981]/30'
                          : triggerStatus === 'Not Yet Triggered Automated'
                          ? 'bg-amber-100 text-amber-800 border border-amber-300'
                          : triggerStatus === 'Partial Automated'
                          ? 'bg-blue-100 text-blue-800 border border-blue-200'
                          : 'bg-[#e2e8f0] text-[#475569]'
                      }`}
                    >
                      {triggerStatus}
                    </span>
                  </div>

                  {/* Benefit Sentence */}
                  {activity.benefit_statement ? (
                    <blockquote className="m-0 pl-3 border-l-2 border-[#087f70] text-xs text-[#172321] leading-relaxed italic bg-white/70 p-2.5 rounded-r-xl">
                      "{activity.benefit_statement}"
                    </blockquote>
                  ) : (
                    <div className="text-xs text-[#73817e] italic bg-white/60 p-2.5 rounded-xl">
                      Belum memiliki narasi benefit terverifikasi (Unmapped in Baseline).
                    </div>
                  )}

                  {/* Technology Recommendation & Action Guidance */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="bg-white p-3 rounded-xl border border-[#e6ecea] space-y-1">
                      <div className="flex items-center space-x-1.5 text-[11px] font-bold uppercase tracking-wider text-[#087f70]">
                        <Cpu className="h-3.5 w-3.5" />
                        <span>Rekomendasi Teknologi</span>
                      </div>
                      <div className="font-extrabold text-sm text-[#172321]">
                        {activity.recommended_technology || 'AION / Script'}
                      </div>
                      <p className="text-[11px] text-[#73817e] leading-tight m-0">
                        {activity.recommended_technology_detail?.rationale ||
                          'Indikasi rekomendasi otomatis berdasarkan profil operasional.'}
                      </p>
                      <small className="block text-[10px] text-[#94a3b8] pt-1">
                        *Indikasi rekomendasi teknis (bukan keputusan final).
                      </small>
                    </div>

                    <div className="bg-white p-3 rounded-xl border border-[#e6ecea] space-y-1">
                      <div className="flex items-center space-x-1.5 text-[11px] font-bold uppercase tracking-wider text-[#b98227]">
                        <Lightbulb className="h-3.5 w-3.5" />
                        <span>Agenda Review Meeting</span>
                      </div>
                      <p className="text-xs font-semibold text-[#172321] leading-snug m-0">
                        {activity.action_recommendation || 'Validasi kesiapan use case bersama tower owner.'}
                      </p>
                      <div className="pt-2 flex items-center space-x-1 text-[11px] text-[#087f70]">
                        <CheckCircle2 className="h-3 w-3 shrink-0" />
                        <span>Status: Siap dievaluasi di review L1</span>
                      </div>
                    </div>
                  </div>
                </motion.div>

                {/* Section 2: Workload Metrics (M1 Deterministic) */}
                <motion.div
                  variants={itemVariants}
                  className="rounded-2xl border border-[#e6ecea] bg-[#f8fafb] p-5 space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm font-bold text-[#172321]">
                      <Clock className="h-4 w-4 text-[#087f70]" />
                      <span>Deterministic Workload Analysis (M1)</span>
                    </div>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                        isHealthyCalc ? 'bg-[#e2f3ed] text-[#087f70]' : 'bg-[#fff3df] text-[#9a6a1c]'
                      }`}
                    >
                      {calcStatus}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="bg-white p-3 rounded-xl border border-[#e6ecea]">
                      <span className="text-[11px] text-[#73817e] uppercase font-semibold">
                        Durasi
                      </span>
                      <p className="text-base font-extrabold text-[#172321] mt-1 font-tabular">
                        {fmt(durVal)} <span className="text-xs font-normal text-[#73817e]">menit</span>
                      </p>
                    </div>

                    <div className="bg-white p-3 rounded-xl border border-[#e6ecea]">
                      <span className="text-[11px] text-[#73817e] uppercase font-semibold">
                        Frekuensi
                      </span>
                      <p className="text-base font-extrabold text-[#172321] mt-1 font-tabular">
                        {fmt(evVal, evVal % 1 !== 0 ? 2 : 0)}{' '}
                        <span className="text-xs font-normal text-[#73817e]">ev/bln</span>
                      </p>
                    </div>

                    <div className="bg-white p-3 rounded-xl border border-[#e6ecea]">
                      <span className="text-[11px] text-[#73817e] uppercase font-semibold">
                        Workload Menit
                      </span>
                      <p className="text-base font-extrabold text-[#172321] mt-1 font-tabular">
                        {fmt(wlMin, 1)} <span className="text-xs font-normal text-[#73817e]">min</span>
                      </p>
                    </div>

                    <div className="bg-[#103f38] text-white p-3 rounded-xl border border-[#103f38]">
                      <span className="text-[11px] text-[#b8d8d1] uppercase font-semibold">
                        Workload Jam
                      </span>
                      <p className="text-base font-extrabold text-white mt-1 font-tabular">
                        {fmt(wlHours, 2)} <span className="text-xs font-normal text-[#b8d8d1]">jam</span>
                      </p>
                    </div>
                  </div>

                  {activity['Workload Validation Notes'] && (
                    <div className="p-3 bg-white rounded-xl border border-[#e6ecea] text-xs text-[#73817e]">
                      <span className="font-semibold text-[#172321]">Validation Notes: </span>
                      {String(activity['Workload Validation Notes'])}
                    </div>
                  )}
                </motion.div>

                {/* Section 3: Operational Classification */}
                <motion.div variants={itemVariants} className="space-y-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#73817e] flex items-center space-x-1.5">
                    <Workflow className="h-3.5 w-3.5 text-[#087f70]" />
                    <span>Operational Attributes</span>
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3.5 bg-white rounded-xl border border-[#e6ecea]">
                      <span className="text-[#73817e] block mb-1">Type Activity</span>
                      <span className="font-semibold text-[#172321]">{String(activity['TYPE ACTIVITY'] || '—')}</span>
                    </div>

                    <div className="p-3.5 bg-white rounded-xl border border-[#e6ecea]">
                      <span className="text-[#73817e] block mb-1">Tools Automation (Tercatat)</span>
                      <span className="font-semibold text-[#172321]">{String(activity['Tools Automation'] || '—')}</span>
                    </div>

                    <div className="p-3.5 bg-white rounded-xl border border-[#e6ecea]">
                      <span className="text-[#73817e] block mb-1">Team QC</span>
                      <span className="font-semibold text-[#172321]">{String(activity['Team QC'] || '—')}</span>
                    </div>

                    <div className="p-3.5 bg-white rounded-xl border border-[#e6ecea]">
                      <span className="text-[#73817e] block mb-1">Department / Division</span>
                      <span className="font-semibold text-[#172321]">
                        {String(activity.DEPT || '—')} {activity.DIV ? `(${String(activity.DIV)})` : ''}
                      </span>
                    </div>

                    <div className="p-3.5 bg-white rounded-xl border border-[#e6ecea]">
                      <span className="text-[#73817e] block mb-1">Category Notes</span>
                      <span className="font-semibold text-[#172321]">{String(activity['Category Notes'] || '—')}</span>
                    </div>

                    <div className="p-3.5 bg-white rounded-xl border border-[#e6ecea]">
                      <span className="text-[#73817e] block mb-1">Assessment Status</span>
                      <span className="font-semibold text-[#172321]">{String(activity.Status || activity['Assessment Status'] || '—')}</span>
                    </div>
                  </div>
                </motion.div>

                {/* Section 4: SOP & Evidence Links */}
                <motion.div variants={itemVariants} className="space-y-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#73817e] flex items-center space-x-1.5">
                    <FileText className="h-3.5 w-3.5 text-[#087f70]" />
                    <span>Documentation & Evidence Links</span>
                  </h3>

                  <div className="p-4 bg-white rounded-xl border border-[#e6ecea] space-y-3 text-xs">
                    <div>
                      <span className="text-[#73817e] block mb-0.5">SOP Name</span>
                      <span className="font-medium text-[#172321]">{String(activity['SOP Name'] || 'No SOP Recorded')}</span>
                    </div>

                    <div className="flex flex-wrap gap-2 pt-1">
                      {activity['Link Confluence'] && (
                        <a
                          href={String(activity['Link Confluence'])}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#edf1ef] text-[#172321] hover:bg-[#e3f4ef] hover:text-[#087f70] transition-colors font-medium text-xs"
                        >
                          <ExternalLink className="h-3 w-3" />
                          Confluence SOP
                        </a>
                      )}

                      {activity['Link Wiki'] && (
                        <a
                          href={String(activity['Link Wiki'])}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#edf1ef] text-[#172321] hover:bg-[#e3f4ef] hover:text-[#087f70] transition-colors font-medium text-xs"
                        >
                          <ExternalLink className="h-3 w-3" />
                          Wiki Documentation
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
};
