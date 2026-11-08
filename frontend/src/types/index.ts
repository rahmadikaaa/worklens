export type CalculationStatus =
  | 'CALCULATED'
  | 'NEGATIVE_SAVINGS'
  | 'ZERO_WORKLOAD'
  | 'NEGATIVE_INPUT'
  | 'MISSING_INPUT'
  | 'INVALID_INPUT';

export type EvidenceStatus = 'LINK_PROVIDED' | 'NO_LINK_ATTACHED';

export type ChangeClassification =
  | 'UNCHANGED'
  | 'MODIFIED'
  | 'ADDED'
  | 'DELETED'
  | 'REVIEW_REQUIRED';

export interface HealthInfo {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  mock_mode: boolean;
}

export interface ChangeSummaryCounts {
  total_current_rows: number;
  unchanged: number;
  modified: number;
  added: number;
  deleted: number;
  review_required: number;
  reprocess_count: number;
}

export interface RowChangeItem {
  activity_id: string;
  source_row_index?: number | null;
  classification: string;
  content_hash: string;
  previous_content_hash?: string | null;
  reason?: string | null;
  modified_fields: string[];
}

export interface ChangeReportResponse {
  status: 'NO_CHANGE' | 'CHANGES_DETECTED';
  snapshot_id: string;
  source_id: string;
  baseline_snapshot_id?: string | null;
  identical_content_hash: boolean;
  logic_version: string;
  summary_counts: ChangeSummaryCounts;
  changes: RowChangeItem[];
  reprocess_count: number;
  message: string;
}

export interface IncrementalProcessResponse {
  run_id: string;
  snapshot_id: string;
  source_id: string;
  baseline_snapshot_id?: string | null;
  status: string;
  logic_version: string;
  summary_counts: ChangeSummaryCounts;
  total_active_records: number;
  reprocessed_records: number;
  reused_records: number;
  change_report: ChangeReportResponse;
  created_at: string;
}

export interface SourceSnapshot {
  snapshot_id: string;
  source_id: string;
  original_filename: string;
  stored_filename: string;
  generated_at?: string | null;
  uploaded_at: string;
  file_format: string;
  file_size: number;
  content_hash: string;
  status: string;
}

export interface FileUploadResponse {
  filename: string;
  saved_filename: string;
  file_format: string;
  file_size: number;
  upload_status: string;
  message: string;
  uploaded_at?: string;
  snapshot_id?: string;
  source_id?: string;
  snapshot?: SourceSnapshot;
}

export interface FileParseResponse {
  filename: string;
  file_format: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  metadata: Record<string, unknown>;
  parsing_status: string;
  message: string;
}

export interface WorkloadSummary {
  total_activities: number;
  total_applications: number;
  total_workload_initial_min: number;
  total_workload_after_min: number;
  total_workload_saved_min: number;
  overall_reduction_pct: number;
  evidence_provided_count: number;
  calculation_breakdown: Record<CalculationStatus, number>;
  last_updated?: string;
}

export interface ApplicationProfile {
  application_name: string;
  activity_count: number;
  total_workload_min: number;
  total_saved_min: number;
  avg_reduction_pct: number;
}

export interface ActivityRow {
  activity_id: string;
  activity_name: string;
  application: string;
  type_activity: string;
  workload: number;
  workload_after: number;
  workload_saved: number;
  reduction_pct: number;
  calculation_status: CalculationStatus;
  evidence_status: EvidenceStatus;
  validation_notes?: string;
}

export interface AIFinding {
  finding_id: string;
  activity_ref: string;
  activity_id?: string;
  application: string;
  focus_area: 'DATA_QUALITY' | 'ASSESSMENT_CONSISTENCY' | 'AUTOMATION_OPPORTUNITY';
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  evidence: Record<string, unknown>;
  reasoning: string;
  recommendation: string;
  action_by?: string;
}

export interface EnrichedActivity {
  activity_id: string;
  APPS?: string;
  'ACTIVITY NAME'?: string;
  'TYPE ACTIVITY'?: string;
  Workload?: string | number;
  'Workload after'?: string | number;
  'Link Confluence'?: string;
  'Link Wiki'?: string;
  'Improvement Category'?: string;
  'Category Notes'?: string;
  'Action by'?: string;
  'New Improvement Category Fixed'?: string;
  'Additional Notes'?: string;
  DIV?: string;
  CONCAT?: string;
  DEPT?: string;
  'APP PRIORITY'?: string;
  'Number Activity'?: string | number;
  'Durasi (Menit)'?: string | number;
  'Event Per Month'?: string | number;
  'Durasi after'?: string | number;
  'Automation/Manual'?: string;
  'FMC/Mobile'?: string;
  'Team QC'?: string;
  'SOP Name'?: string;
  Status?: string;
  'Status (Old)'?: string;
  'TYPE ACTIVITY2'?: string;
  'Assessment Status'?: string;
  Tools?: string;
  'Category Action'?: string;
  'Confirmation Tower/L2'?: string;
  'Support Needed'?: string;
  Phase?: string;
  'Ops Activity'?: string;
  'Tools Automation'?: string;
  'Module AO'?: string;
  'Workload Saved Est. (Min/Month)'?: number | string | null;
  'Workload Reduction Est. (%)'?: number | string | null;
  'Workload Calculation Status'?: CalculationStatus;
  'Workload Evidence Status'?: EvidenceStatus;
  'Workload Validation Notes'?: string;
  'Annualized Workload Saved Est. (Min/Year)'?: number | string | null;
  automation_bucket?: string;
  workload_numeric?: number;
  workload_hours?: number;
  is_outlier?: boolean;
  is_quick_win?: boolean;
  is_verified_baseline?: boolean;
  status_triggered?: string;
  benefit_statement?: string | null;
  recommended_technology?: string;
  action_recommendation?: string;
  recommended_technology_detail?: {
    technology: string;
    rationale: string;
    is_final: boolean;
  };
  [key: string]: unknown;
}

export interface RealityCheckSummary {
  theoretical_claimed_hours: number;
  theoretical_claimed_pct: number;
  real_actionable_hours: number;
  real_actionable_pct: number;
  real_savings_estimate_hours: number;
  out_of_scope_workload_hours: number;
  out_of_scope_workload_pct: number;
  breakdown_out_of_scope: Record<string, number>;
  gap_statement: string;
}

export interface QuickWinsSummary {
  total_count: number;
  total_hours: number;
  to_be_automated_count: number;
  to_be_automated_hours: number;
  description: string;
}

export interface TriggerReadinessSummary {
  fully_automated_count: number;
  not_yet_triggered_count: number;
  partial_automated_count: number;
  unmapped_count: number;
  baseline_total: number;
  gap_note: string;
}

export interface CandidateAppItem {
  app: string;
  hours: number;
  count: number;
}

export interface CandidateTechItem {
  technology: string;
  hours: number;
  count: number;
  pct: number;
}

export interface OpportunityKpis {
  total_workload_hours: number;
  measured_activities_count: number;
  candidate_workload_hours: number;
  candidate_activities_count: number;
  candidate_percentage: number;
  indicative_saving_hours: number;
  outlier_max_hours: number;
}

export interface BucketSummaryItem {
  k: string;
  label: string;
  color: string;
  cls: string;
  h: number;
  n: number;
  pct: number;
}

export interface ParetoPoint {
  n: number;
  p: number;
}

export interface CategoryHoursItem {
  k: string;
  h: number;
}

export interface ActivitySummaryMetrics {
  filename: string;
  total_activities: number;
  total_workload_before_min: number;
  total_workload_after_min: number;
  total_workload_saved_min: number;
  total_workload_saved_hours: number;
  annualized_saved_hours: number;
  overall_reduction_pct: number;
  data_quality_issues_count: number;
  assessment_done_count: number;
  evidence_provided_count: number;
  opportunity_kpis?: OpportunityKpis;
  reality_check?: RealityCheckSummary;
  quick_wins_summary?: QuickWinsSummary;
  trigger_readiness_summary?: TriggerReadinessSummary;
  top_candidate_apps?: CandidateAppItem[];
  candidate_technologies?: CandidateTechItem[];
  outliers_summary?: Array<Record<string, unknown>>;
  buckets?: BucketSummaryItem[];
  pareto?: ParetoPoint[];
  types?: CategoryHoursItem[];
  tools?: CategoryHoursItem[];
  teams?: CategoryHoursItem[];
  distribution_criticality: Record<string, number>;
  distribution_automation: Record<string, number>;
  distribution_calculation_status: Record<string, number>;
  distribution_evidence: Record<string, number>;
  distribution_assessment_status: Record<string, number>;
  distribution_category_action: Record<string, number>;
  distribution_top_departments: Record<string, number>;
  distribution_top_applications: Record<string, number>;
}

export interface FilterOptions {
  applications: string[];
  departments: string[];
  criticalities: string[];
  assessment_statuses: string[];
  automation_statuses: string[];
  calculation_statuses: string[];
  category_actions: string[];
  buckets?: string[];
  tools?: string[];
  types?: string[];
  teams?: string[];
}

export interface ActivitiesQueryResponse {
  summary: ActivitySummaryMetrics;
  filtered_stats: {
    total_filtered: number;
    filtered_workload_hours?: number;
    filtered_workload_saved_min: number;
    filtered_workload_saved_hours: number;
  };
  filter_options: FilterOptions;
  page: number;
  page_size: number;
  total_pages: number;
  total_count: number;
  items: EnrichedActivity[];
}


