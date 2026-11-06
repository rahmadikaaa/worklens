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

