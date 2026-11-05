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
