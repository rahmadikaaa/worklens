import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Search,
  X,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Info,
  RefreshCw,
} from 'lucide-react';
import type { EnrichedActivity, ActivitiesQueryResponse, FilterOptions } from '../types';
import { AnimatedBadge, SkeletonRow } from './motion/MotionPrimitives';
import { ActivityDetailDrawer } from './ActivityDetailDrawer';

interface ActivityExplorerProps {
  initialFilter?: {
    app?: string;
    criticality?: string;
    calcStatus?: string;
    automationStatus?: string;
  };
}

export const ActivityExplorer: React.FC<ActivityExplorerProps> = ({ initialFilter }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<ActivitiesQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Filter & Search states
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [selectedApp, setSelectedApp] = useState<string>(initialFilter?.app || '');
  const [selectedDept, setSelectedDept] = useState<string>('');
  const [selectedCrit, setSelectedCrit] = useState<string>(initialFilter?.criticality || '');
  const [selectedCalcStatus, setSelectedCalcStatus] = useState<string>(initialFilter?.calcStatus || '');
  const [selectedAutoStatus, setSelectedAutoStatus] = useState<string>(initialFilter?.automationStatus || '');

  // Pagination & Sorting
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);
  const [sortBy, setSortBy] = useState<string>('activity_id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Drawer & Selection state
  const [selectedActivity, setSelectedActivity] = useState<EnrichedActivity | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);

  // Debounce search term
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1);
    }, 280);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  // Fetch activities from API
  const fetchActivities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
        sort_by: sortBy,
        sort_order: sortOrder,
      });

      if (debouncedSearch) params.set('search', debouncedSearch);
      if (selectedApp) params.set('app', selectedApp);
      if (selectedDept) params.set('dept', selectedDept);
      if (selectedCrit) params.set('criticality', selectedCrit);
      if (selectedCalcStatus) params.set('calc_status', selectedCalcStatus);
      if (selectedAutoStatus) params.set('automation_status', selectedAutoStatus);

      const res = await fetch(`/api/v1/activities?${params.toString()}`);
      if (!res.ok) {
        throw new Error(`API returned HTTP ${res.status}`);
      }
      const json: ActivitiesQueryResponse = await res.json();
      setData(json);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query activities');
    } finally {
      setLoading(false);
    }
  }, [
    page,
    pageSize,
    sortBy,
    sortOrder,
    debouncedSearch,
    selectedApp,
    selectedDept,
    selectedCrit,
    selectedCalcStatus,
    selectedAutoStatus,
  ]);

  useEffect(() => {
    fetchActivities();
  }, [fetchActivities]);

  const handleRowClick = (act: EnrichedActivity) => {
    setSelectedActivity(act);
    setIsDrawerOpen(true);
  };

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
    setPage(1);
  };

  const clearAllFilters = () => {
    setSearchTerm('');
    setDebouncedSearch('');
    setSelectedApp('');
    setSelectedDept('');
    setSelectedCrit('');
    setSelectedCalcStatus('');
    setSelectedAutoStatus('');
    setPage(1);
  };

  const hasActiveFilters = Boolean(
    debouncedSearch ||
      selectedApp ||
      selectedDept ||
      selectedCrit ||
      selectedCalcStatus ||
      selectedAutoStatus
  );

  const filterOptions: FilterOptions = data?.filter_options || {
    applications: [],
    departments: [],
    criticalities: [],
    assessment_statuses: [],
    automation_statuses: [],
    calculation_statuses: [],
    category_actions: [],
  };

  return (
    <div className="space-y-6">
      {/* Control Bar: Search & Filters */}
      <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-5 backdrop-blur space-y-4">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          {/* Animated Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by Activity Name, ID, Application, SOP..."
              className="w-full pl-10 pr-9 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 transition-all duration-200"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Quick Stats on filter matches */}
          <div className="flex items-center space-x-3 text-xs text-slate-400 shrink-0">
            <span>
              Showing <strong className="text-white font-mono">{data?.filtered_stats?.total_filtered ?? 0}</strong> of{' '}
              <span className="font-mono">{data?.summary?.total_activities ?? 3460}</span> activities
            </span>
            <button
              onClick={fetchActivities}
              disabled={loading}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition"
              title="Refresh dataset"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Dropdowns Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {/* App filter */}
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Application
            </label>
            <select
              value={selectedApp}
              onChange={(e) => {
                setSelectedApp(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:ring-1 focus:ring-sky-500 focus:outline-none transition-colors duration-150"
            >
              <option value="">All Applications</option>
              {filterOptions.applications.map((app) => (
                <option key={app} value={app}>
                  {app}
                </option>
              ))}
            </select>
          </div>

          {/* Dept filter */}
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Department
            </label>
            <select
              value={selectedDept}
              onChange={(e) => {
                setSelectedDept(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:ring-1 focus:ring-sky-500 focus:outline-none transition-colors duration-150"
            >
              <option value="">All Departments</option>
              {filterOptions.departments.map((dept) => (
                <option key={dept} value={dept}>
                  {dept}
                </option>
              ))}
            </select>
          </div>

          {/* Criticality filter */}
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Criticality
            </label>
            <select
              value={selectedCrit}
              onChange={(e) => {
                setSelectedCrit(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:ring-1 focus:ring-sky-500 focus:outline-none transition-colors duration-150"
            >
              <option value="">All Criticalities</option>
              {filterOptions.criticalities.map((crit) => (
                <option key={crit} value={crit}>
                  {crit}
                </option>
              ))}
            </select>
          </div>

          {/* Calculation Status filter */}
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Calc Status
            </label>
            <select
              value={selectedCalcStatus}
              onChange={(e) => {
                setSelectedCalcStatus(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:ring-1 focus:ring-sky-500 focus:outline-none transition-colors duration-150"
            >
              <option value="">All Statuses</option>
              {filterOptions.calculation_statuses.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          {/* Automation Status filter */}
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Automation
            </label>
            <select
              value={selectedAutoStatus}
              onChange={(e) => {
                setSelectedAutoStatus(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:ring-1 focus:ring-sky-500 focus:outline-none transition-colors duration-150"
            >
              <option value="">All Types</option>
              {filterOptions.automation_statuses.map((auto) => (
                <option key={auto} value={auto}>
                  {auto}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Active Filter Pills Bar */}
        <AnimatePresence>
          {hasActiveFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80"
            >
              <span className="text-[11px] text-slate-400 font-medium">Active Filters:</span>

              {debouncedSearch && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs">
                  <span>Search: &quot;{debouncedSearch}&quot;</span>
                  <button onClick={() => setSearchTerm('')} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {selectedApp && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs">
                  <span>App: {selectedApp}</span>
                  <button onClick={() => setSelectedApp('')} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {selectedDept && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs">
                  <span>Dept: {selectedDept}</span>
                  <button onClick={() => setSelectedDept('')} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {selectedCrit && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                  <span>Criticality: {selectedCrit}</span>
                  <button onClick={() => setSelectedCrit('')} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {selectedCalcStatus && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs">
                  <span>Calc: {selectedCalcStatus}</span>
                  <button onClick={() => setSelectedCalcStatus('')} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {selectedAutoStatus && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
                  <span>Auto: {selectedAutoStatus}</span>
                  <button onClick={() => setSelectedAutoStatus('')} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              <button
                onClick={clearAllFilters}
                className="text-xs text-slate-400 hover:text-white underline ml-2 transition"
              >
                Clear all
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
          <span>Failed to load activities: {error}. Ensure backend is running.</span>
          <button onClick={fetchActivities} className="underline text-rose-200 hover:text-white">Retry</button>
        </div>
      )}

      {/* Main Interactive Table */}
      <div className="bg-slate-950/70 border border-slate-800 rounded-2xl shadow-xl overflow-hidden backdrop-blur">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 border-b border-slate-800 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <tr>
                <th
                  onClick={() => handleSort('activity_id')}
                  className="py-3 px-4 cursor-pointer hover:text-white transition select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>Activity ID / Name</span>
                    {sortBy === 'activity_id' ? (
                      sortOrder === 'asc' ? <ArrowUp className="h-3 w-3 text-sky-400" /> : <ArrowDown className="h-3 w-3 text-sky-400" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-600" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('APPS')}
                  className="py-3 px-4 cursor-pointer hover:text-white transition select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>Application</span>
                    {sortBy === 'APPS' ? (
                      sortOrder === 'asc' ? <ArrowUp className="h-3 w-3 text-sky-400" /> : <ArrowDown className="h-3 w-3 text-sky-400" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-600" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('APP PRIORITY')}
                  className="py-3 px-4 cursor-pointer hover:text-white transition select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>Criticality</span>
                    {sortBy === 'APP PRIORITY' ? (
                      sortOrder === 'asc' ? <ArrowUp className="h-3 w-3 text-sky-400" /> : <ArrowDown className="h-3 w-3 text-sky-400" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-600" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('Workload')}
                  className="py-3 px-4 text-right cursor-pointer hover:text-white transition select-none"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Workload (Min)</span>
                    {sortBy === 'Workload' ? (
                      sortOrder === 'asc' ? <ArrowUp className="h-3 w-3 text-sky-400" /> : <ArrowDown className="h-3 w-3 text-sky-400" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-600" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('Workload Saved Est. (Min/Month)')}
                  className="py-3 px-4 text-right cursor-pointer hover:text-white transition select-none"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Saved (Min)</span>
                    {sortBy === 'Workload Saved Est. (Min/Month)' ? (
                      sortOrder === 'asc' ? <ArrowUp className="h-3 w-3 text-sky-400" /> : <ArrowDown className="h-3 w-3 text-sky-400" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-600" />
                    )}
                  </div>
                </th>
                <th className="py-3 px-4">Calculation Status</th>
                <th className="py-3 px-4">Evidence</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/60 font-sans">
              {loading ? (
                Array.from({ length: 10 }).map((_, i) => <SkeletonRow key={i} columns={7} />)
              ) : data && data.items.length > 0 ? (
                data.items.map((row) => {
                  const isSelected = selectedActivity?.activity_id === row.activity_id;
                  const calcSt = row['Workload Calculation Status'] || 'CALCULATED';

                  return (
                    <motion.tr
                      key={row.activity_id}
                      onClick={() => handleRowClick(row)}
                      whileHover={{ backgroundColor: 'rgba(30, 41, 59, 0.5)' }}
                      className={`cursor-pointer transition-colors duration-150 select-none ${
                        isSelected ? 'bg-sky-500/10 border-l-2 border-l-sky-500' : ''
                      }`}
                    >
                      <td className="py-3 px-4 max-w-[280px]">
                        <div className="font-semibold text-white truncate" title={row['ACTIVITY NAME'] || row.activity_id}>
                          {row['ACTIVITY NAME'] || row.activity_id}
                        </div>
                        <div className="text-[11px] text-slate-500 font-mono truncate" title={row.activity_id}>
                          {row.activity_id}
                        </div>
                      </td>

                      <td className="py-3 px-4 font-medium text-slate-300 truncate max-w-[140px]">
                        {row.APPS || '—'}
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap">
                        <AnimatedBadge
                          status={String(row['APP PRIORITY'] || 'Standard')}
                          variant={
                            row['APP PRIORITY'] === 'Mission Critical'
                              ? 'rose'
                              : row['APP PRIORITY'] === 'Business Critical'
                              ? 'amber'
                              : 'sky'
                          }
                        />
                      </td>

                      <td className="py-3 px-4 text-right font-mono text-slate-200">
                        {row.Workload !== undefined && row.Workload !== '' ? String(row.Workload) : '—'}
                      </td>

                      <td className="py-3 px-4 text-right font-mono font-semibold text-emerald-400">
                        {typeof row['Workload Saved Est. (Min/Month)'] === 'number'
                          ? row['Workload Saved Est. (Min/Month)'].toLocaleString()
                          : '—'}
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap">
                        <AnimatedBadge
                          status={calcSt}
                          variant={
                            calcSt === 'CALCULATED'
                              ? 'emerald'
                              : calcSt === 'ZERO_WORKLOAD'
                              ? 'sky'
                              : 'amber'
                          }
                          pulse={calcSt === 'INVALID_INPUT'}
                        />
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center text-[11px] font-medium ${
                            row['Workload Evidence Status'] === 'LINK_PROVIDED'
                              ? 'text-emerald-400'
                              : 'text-slate-500'
                          }`}
                        >
                          {row['Workload Evidence Status'] === 'LINK_PROVIDED' ? '✓ Link Attached' : '— No Link'}
                        </span>
                      </td>
                    </motion.tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <Info className="h-6 w-6 mx-auto mb-2 text-slate-500" />
                    <p className="font-medium text-sm">No activities matched your search criteria.</p>
                    <button
                      onClick={clearAllFilters}
                      className="mt-2 text-xs text-sky-400 hover:underline"
                    >
                      Reset all filters
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Interactive Pagination Footer */}
        {data && (
          <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
            <div className="flex items-center space-x-2">
              <span>Rows per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-200 focus:outline-none"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span className="ml-2">
                Page <strong className="text-white">{data.page}</strong> of{' '}
                <strong className="text-white">{data.total_pages}</strong>
              </span>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-850 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 transition"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>

              <span className="px-3 font-mono text-slate-300">
                {((page - 1) * pageSize + 1).toLocaleString()} -{' '}
                {Math.min(page * pageSize, data.total_count).toLocaleString()} of{' '}
                {data.total_count.toLocaleString()}
              </span>

              <button
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                disabled={page >= data.total_pages}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-850 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 transition"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Activity Detail Drawer */}
      <ActivityDetailDrawer
        activity={selectedActivity}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  );
};
