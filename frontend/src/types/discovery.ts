export type ConfidenceStatus = 'CONFIRMED' | 'INFERRED' | 'UNRESOLVED';

export interface RuleItem {
  id: string;
  category: string;
  name: string;
  confidence: ConfidenceStatus;
  logic: string;
  preconditions: string;
  verification: string;
  sample: string;
}

export interface DecisionTableRow {
  status_triggered: string;
  workload_range: string;
  event_condition: string;
  tools_automation: string;
  category_action: string;
  template: string;
  sample: string;
}

export interface ExceptionItem {
  activity_id: string;
  type: string;
  field: string;
  source_value: string;
  benchmark_value: string;
  reason: string;
  confidence: string;
}

export interface DistributionItem {
  name: string;
  count: number;
  percentage: number;
}

export interface DiscoveryReport {
  executive_summary: {
    title: string;
    status: string;
    headline: string;
    total_benchmark_records: number;
    total_source_activities: number;
    match_rate_percent: number;
    workload_formula_accuracy_percent: number;
    benefit_text_accuracy_percent: number;
    total_workload_hours_per_month: number;
    total_workload_minutes_per_month: number;
    deterministic_assurance: string;
  };
  dataset_overview: {
    source_json: {
      path: string;
      filename: string;
      total_records: number;
      columns_detected: number;
      scope: string;
      extracted_at: string;
    };
    benchmark_csv: {
      path: string;
      filename: string;
      total_records: number;
      columns: string[];
      scope: string;
    };
  };
  matching_results: {
    total_evaluated: number;
    exact_matches: number;
    stripped_matches: number;
    unmatched_count: number;
    linkage_key: string;
    match_percentage: number;
    whitespace_edge_cases: string[];
  };
  confidence_summary: {
    CONFIRMED: {
      count: number;
      status: string;
      description: string;
      rules: string[];
    };
    INFERRED: {
      count: number;
      status: string;
      description: string;
      rules: string[];
    };
    UNRESOLVED: {
      count: number;
      status: string;
      description: string;
      rules: string[];
    };
  };
  rule_catalog: RuleItem[];
  decision_table: DecisionTableRow[];
  exception_analysis: ExceptionItem[];
  validation_results: {
    workload_formula_match_rate: number;
    benefit_text_match_rate: number;
    total_benchmark_records: number;
    category_action_distribution: DistributionItem[];
    tools_automation_distribution: DistributionItem[];
    status_triggered_distribution: DistributionItem[];
  };
}

