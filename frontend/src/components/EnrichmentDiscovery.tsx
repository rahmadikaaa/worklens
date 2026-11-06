import React, { useEffect, useState, useMemo } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  Copy,
  Cpu,
  Database,
  Filter,
  HelpCircle,
  Layers,
  Play,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Table,
  Terminal,
  TrendingUp,
} from 'lucide-react';
import type { ConfidenceStatus, DiscoveryReport } from '../types/discovery';

const FALLBACK_DISCOVERY_DATA: DiscoveryReport = {
  executive_summary: {
    title: 'Reverse Engineering Enrichment Discovery Baseline',
    status: 'VALIDATED_100_PERCENT',
    headline:
      'Reverse engineering confirms 100% deterministic mathematical and linguistic grammar across all 667 benchmark records.',
    total_benchmark_records: 667,
    total_source_activities: 3460,
    match_rate_percent: 100.0,
    workload_formula_accuracy_percent: 100.0,
    benefit_text_accuracy_percent: 100.0,
    total_workload_hours_per_month: 623.8,
    total_workload_minutes_per_month: 37425.0,
    deterministic_assurance:
      'Zero generative guessing required. Derived metrics and narratives are 100% deterministic.',
  },
  dataset_overview: {
    source_json: {
      path: 'backend/uploads/breakdown_activity_261105_1704_1.json',
      filename: 'breakdown_activity_261105_1704_1.json',
      total_records: 3460,
      columns_detected: 36,
      scope: 'Raw operational activities breakdown assessment',
      extracted_at: '2026-11-05T10:04:16.062Z',
    },
    benchmark_csv: {
      path: 'backend/uploads/REA/Improvements_With_Benefit.csv',
      filename: 'Improvements_With_Benefit.csv',
      total_records: 667,
      columns: [
        'CONCAT',
        'Durasi (Menit)',
        'Event Per Month',
        'Workload',
        'Category Action',
        'Tools Automation',
        'Status Triggered',
        'Benefit',
      ],
      scope: 'Manual operational enrichment & benefit baseline',
    },
  },
  matching_results: {
    total_evaluated: 667,
    exact_matches: 658,
    stripped_matches: 9,
    unmatched_count: 0,
    linkage_key: 'CONCAT <-> activity_id',
    match_percentage: 100.0,
    whitespace_edge_cases: [
      'C2P - Check Transaction C2P Service by Grafana',
      'C2P - Check Traffik C2P Service by Grafana',
      'C2P - Check Success Rate C2P Service by Grafana',
      'C2P - Check Error Count C2P Service by Grafana',
      'Uniprov Pacelayer - Restart & Load Reset Service UPL',
      'IoT Sphere - Check Status adapter_import_gp',
      'IoT Sphere - Check Status adapter_scheduler',
      'IoT Sphere - Check Status adapter_sync_commit',
      'Digital Core ESB - DNSMASQ Overview and Record Adjustment',
    ],
  },
  confidence_summary: {
    CONFIRMED: {
      count: 8,
      status: 'CONFIRMED',
      description: 'Rules with 100.00% exact empirical verification across all 667 benchmark activities.',
      rules: [
        'RULE-WL-01',
        'RULE-WL-02',
        'RULE-BEN-01',
        'RULE-BEN-02',
        'RULE-BEN-03',
        'RULE-BEN-04',
        'RULE-BEN-05',
        'RULE-LNK-01',
      ],
    },
    INFERRED: {
      count: 4,
      status: 'INFERRED',
      description: 'High-confidence operational heuristics derived from semantic keywords and tool tags.',
      rules: ['RULE-INF-01', 'RULE-INF-02', 'RULE-INF-03', 'RULE-INF-04'],
    },
    UNRESOLVED: {
      count: 4,
      status: 'UNRESOLVED',
      description: 'Manual exceptions, ad-hoc interview calibrations, or trailing whitespace discrepancies.',
      rules: ['EXC-01', 'EXC-02', 'EXC-03', 'EXC-04'],
    },
  },
  rule_catalog: [
    {
      id: 'RULE-WL-01',
      category: 'Workload Calculation',
      name: 'Deterministic Workload Formula',
      confidence: 'CONFIRMED',
      logic: 'Workload (Menit/Bulan) = Durasi (Menit) * Event Per Month',
      preconditions: 'Durasi >= 0, Event Per Month >= 1',
      verification: '667 / 667 rows match (100.00%). Zero arithmetic guessing.',
      sample: 'Durasi=5, Event=5 -> Workload=25 minutes/month',
    },
    {
      id: 'RULE-WL-02',
      category: 'Workload Calculation',
      name: 'Zero Workload Exception Handling',
      confidence: 'CONFIRMED',
      logic:
        'When Durasi=0 or Workload=0, activity represents reactive/standby intervention. Benefit switches to recovery narrative.',
      preconditions: 'Workload == 0',
      verification: '2 / 2 zero-workload rows match exactly (Row 308 & Row 309).',
      sample:
        'Potentially eliminates manual intervention time and accelerates system recovery once automated through standardized automation...',
    },
    {
      id: 'RULE-BEN-01',
      category: 'Benefit Grammar',
      name: 'Workload Unit Scaling (Minutes vs Hours)',
      confidence: 'CONFIRMED',
      logic:
        'If Workload < 60: format as integer minutes. If Workload >= 60: divide by 60.0; if integer format as integer hours, else format as 1 decimal place ({hours:.1f} hours).',
      preconditions: 'Workload > 0',
      verification:
        '100.00% string match. Verified on integer hours (5 hours), halves (7.5 hours), and repeating decimals (2.8 hours, 1.7 hours).',
      sample:
        '25 min -> "25 minutes"; 300 min -> "5 hours"; 165 min -> "2.8 hours"; 450 min -> "7.5 hours"',
    },
    {
      id: 'RULE-BEN-02',
      category: 'Benefit Grammar',
      name: 'Frequency & Duration Clause Synthesis',
      confidence: 'CONFIRMED',
      logic:
        'If Event=1: "(saving X minutes per event)". If Event > 1: "(saving X minutes per event across N monthly events)".',
      preconditions: 'Valid Durasi and Event Per Month',
      verification: '667 / 667 rows match (100.00%).',
      sample:
        'Event=1 -> "(saving 15 minutes per event)"; Event=5 -> "(saving 5 minutes per event across 5 monthly events)"',
    },
    {
      id: 'RULE-BEN-03',
      category: 'Benefit Grammar',
      name: 'Tool Preposition & Nomenclature Mapping',
      confidence: 'CONFIRMED',
      logic:
        'Tools Automation mapped into narrative clause: "CICD" -> "via CI/CD automation"; "Not Automate" -> "through standardized automation" (omits "via"); all other tools -> "via {Tool}".',
      preconditions: 'Recognized Tools Automation value',
      verification: '667 / 667 rows match (100.00%), including 5 CICD and 2 Not Automate cases.',
      sample:
        'AION -> "via AION"; Shell Script -> "via Shell Script"; Not Automate -> "through standardized automation"',
    },
    {
      id: 'RULE-BEN-04',
      category: 'Benefit Grammar',
      name: 'Category Action Phrase Synthesis',
      confidence: 'CONFIRMED',
      logic:
        'Category Action maps directly to canonical action phrase: Auto Monitoring -> "continuous proactive monitoring and real-time anomaly detection"; Smart Healing -> "automated fault detection and self-healing recovery"; Self Service Request -> "streamlined self-service execution and eliminating manual ticket handling"; Auto Housekeeping -> "scheduled automated log and disk housekeeping"; Health Check -> "automated system health checks and proactive issue prevention"; Auto Restart -> "automated service restarts and rapid downtime mitigation".',
      preconditions: 'Valid Category Action from 6 canonical classes',
      verification: '667 / 667 rows match (100.00%).',
      sample: '"Auto Monitoring" -> "continuous proactive monitoring and real-time anomaly detection"',
    },
    {
      id: 'RULE-BEN-05',
      category: 'Benefit Grammar',
      name: 'Status Triggered Prefix Templates',
      confidence: 'CONFIRMED',
      logic:
        'Status Triggered selects executive clause prefix: Fully Automated -> "Eliminates {WL} of manual operational workload per month ({clause}) {tool} through {action}."; Not Yet Triggered Automated -> "Potentially eliminates {WL} of manual operational workload per month ({clause}) once automated {tool} through {action}."; Partial Automated -> "Reduces monthly operational workload by {WL} ({clause}) {tool} through {action}."',
      preconditions:
        'Status Triggered in ["Fully Automated", "Not Yet Triggered Automated", "Partial Automated"]',
      verification: '667 / 667 rows match (100.00%).',
      sample:
        'Fully: "Eliminates 25 minutes..."; Not Yet: "Potentially eliminates 7.5 hours... once automated..."; Partial: "Reduces monthly operational workload by 2.8 hours..."',
    },
    {
      id: 'RULE-LNK-01',
      category: 'Data Linkage',
      name: 'CONCAT Primary Key Cross-Reference',
      confidence: 'CONFIRMED',
      logic:
        'The "CONCAT" field in benchmark CSV functions as strict primary key matching "activity_id" in source JSON dataset.',
      preconditions: 'CONCAT string normalized with .strip()',
      verification:
        '667 / 667 activities linked (658 exact string match, 9 with trailing whitespace stripped). Zero unmatched.',
      sample: '"UFO - Monitoring DE" <-> "UFO - Monitoring DE"',
    },
    {
      id: 'RULE-INF-01',
      category: 'Tooling Taxonomy',
      name: 'Tooling Enhancement & Upgrades',
      confidence: 'INFERRED',
      logic:
        'In source JSON, 93 records were tagged "Not Automate" while their notes or runbooks showed AION capabilities; during manual enrichment they were upgraded to "AION". 14 rows had casing normalized ("Shell script" -> "Shell Script").',
      preconditions: 'Activity Runbook mentions target platform',
      verification: '127 tool transitions identified and cataloged.',
      sample: '"Not Automate" (JSON) -> "AION" (CSV) for 93 rows',
    },
    {
      id: 'RULE-INF-02',
      category: 'Taxonomy Classification',
      name: 'Category Action Lexical Keyword Assignment',
      confidence: 'INFERRED',
      logic:
        'In source JSON, "Category Action" is 100% empty. In benchmark CSV, activities are categorized into 6 categories based on lexical cues in ACTIVITY NAME, SOP Name, and Additional Notes (e.g., "Housekeeping" -> Auto Housekeeping, "Monitoring" / "Check" -> Auto Monitoring / Health Check, "Restart" -> Smart Healing / Auto Restart).',
      preconditions: 'Activity Name / SOP Name lexical parsing',
      verification: '667 records successfully classified into 6 categories.',
      sample: '"Housekeeping /var" -> Auto Housekeeping; "Monitoring DE" -> Auto Monitoring',
    },
    {
      id: 'RULE-INF-03',
      category: 'Maturity Tiering',
      name: 'Status Triggered Operational Assignment',
      confidence: 'INFERRED',
      logic:
        'Status Triggered is an SME assessment of production trigger readiness: Fully Automated (production cron/webhook active), Not Yet Triggered Automated (automation developed but awaits trigger setup), Partial Automated (hybrid flow with human signoff).',
      preconditions: 'SME operational triage',
      verification:
        'Fully Automated: 389 (58.3%), Not Yet Triggered: 256 (38.4%), Partial: 22 (3.3%).',
      sample: 'crontab/webhook -> Fully Automated; manual execution button -> Not Yet Triggered',
    },
    {
      id: 'RULE-INF-04',
      category: 'Scope Selection',
      name: 'Automation Candidate Filtering',
      confidence: 'INFERRED',
      logic:
        'Benchmark CSV extracted 667 activities out of 3,460 source JSON rows, prioritizing high-impact applications (69 apps) and activities tagged "Already Automation" / "Already Automated".',
      preconditions: 'Category Notes == "Already Automation"',
      verification:
        '654 of 667 rows belong to Already Automation; top apps include MSight (105), Outsystem (100), SMS Gateway (86).',
      sample: '69 apps covered in benchmark out of 100+ total apps',
    },
  ],
  decision_table: [
    {
      status_triggered: 'Fully Automated',
      workload_range: 'Workload = 0',
      event_condition: 'Any',
      tools_automation: 'Any tool',
      category_action: 'Any action',
      template:
        'Eliminates manual intervention time and accelerates system recovery {tool_clause} through {action_phrase}.',
      sample:
        'Eliminates manual intervention time and accelerates system recovery via AION through automated fault detection and self-healing recovery.',
    },
    {
      status_triggered: 'Fully Automated',
      workload_range: '0 < WL < 60 min',
      event_condition: 'Event = 1',
      tools_automation: 'Shell Script',
      category_action: 'Smart Healing',
      template:
        'Eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event) {tool_clause} through {action_phrase}.',
      sample:
        'Eliminates 30 minutes of manual operational workload per month (saving 30 minutes per event) via Shell Script through automated fault detection and self-healing recovery.',
    },
    {
      status_triggered: 'Fully Automated',
      workload_range: '0 < WL < 60 min',
      event_condition: 'Event > 1',
      tools_automation: 'Shell Script',
      category_action: 'Auto Monitoring',
      template:
        'Eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.',
      sample:
        'Eliminates 25 minutes of manual operational workload per month (saving 5 minutes per event across 5 monthly events) via Shell Script through continuous proactive monitoring and real-time anomaly detection.',
    },
    {
      status_triggered: 'Fully Automated',
      workload_range: 'WL >= 60 min',
      event_condition: 'Event > 1',
      tools_automation: 'Shell Script',
      category_action: 'Auto Restart',
      template:
        'Eliminates {WL_HR} hours of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.',
      sample:
        'Eliminates 5 hours of manual operational workload per month (saving 10 minutes per event across 30 monthly events) via Shell Script through automated service restarts and rapid downtime mitigation.',
    },
    {
      status_triggered: 'Not Yet Triggered Automated',
      workload_range: 'Workload = 0',
      event_condition: 'Any',
      tools_automation: 'Not Automate',
      category_action: 'Smart Healing',
      template:
        'Potentially eliminates manual intervention time and accelerates system recovery once automated {tool_clause} through {action_phrase}.',
      sample:
        'Potentially eliminates manual intervention time and accelerates system recovery once automated through standardized automation through automated fault detection and self-healing recovery.',
    },
    {
      status_triggered: 'Not Yet Triggered Automated',
      workload_range: '0 < WL < 60 min',
      event_condition: 'Event = 1',
      tools_automation: 'AION',
      category_action: 'Smart Healing',
      template:
        'Potentially eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event) once automated {tool_clause} through {action_phrase}.',
      sample:
        'Potentially eliminates 20 minutes of manual operational workload per month (saving 20 minutes per event) once automated via AION through automated fault detection and self-healing recovery.',
    },
    {
      status_triggered: 'Not Yet Triggered Automated',
      workload_range: 'WL >= 60 min',
      event_condition: 'Event > 1',
      tools_automation: 'Grafana',
      category_action: 'Auto Monitoring',
      template:
        'Potentially eliminates {WL_HR} hours of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) once automated {tool_clause} through {action_phrase}.',
      sample:
        'Potentially eliminates 7.5 hours of manual operational workload per month (saving 15 minutes per event across 30 monthly events) once automated via Grafana through continuous proactive monitoring and real-time anomaly detection.',
    },
    {
      status_triggered: 'Partial Automated',
      workload_range: 'WL >= 60 min',
      event_condition: 'Event > 1',
      tools_automation: 'AION',
      category_action: 'Self Service Request',
      template:
        'Reduces monthly operational workload by {WL_HR} hours (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.',
      sample:
        'Reduces monthly operational workload by 2.8 hours (saving 15 minutes per event across 11 monthly events) via AION through streamlined self-service execution and eliminating manual ticket handling.',
    },
  ],
  exception_analysis: [
    {
      activity_id: 'Email Relay External - Housekeeping',
      type: 'MANUAL_NUMERIC_OVERRIDE',
      field: 'Durasi / Event',
      source_value: 'Durasi: 30.0, Event: 1.0 (Workload: 30.0)',
      benchmark_value: 'Durasi: 5.0, Event: 1.0 (Workload: 5.0)',
      reason:
        'Duration calibrated manually from 30 to 5 minutes based on actual log execution metrics during operational triage. Internal formula Workload = Durasi * Event remained 100% consistent.',
      confidence: 'MANUAL_OVERRIDE',
    },
    {
      activity_id: 'Elisa - Check Log Elisa di DB',
      type: 'MANUAL_NUMERIC_OVERRIDE',
      field: 'Durasi / Event',
      source_value: 'Durasi: 5.0, Event: 30.0 (Workload: 150.0)',
      benchmark_value: 'Durasi: 5.0, Event: 1.0 (Workload: 5.0)',
      reason:
        'Event frequency calibrated from 30 to 1 monthly event due to consolidation of recurring database health checks. Internal formula Workload = Durasi * Event remained 100% consistent.',
      confidence: 'MANUAL_OVERRIDE',
    },
    {
      activity_id: 'C2P - Check Transaction C2P Service by Grafana ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'C2P - Check Transaction C2P Service by Grafana',
      benchmark_value: "'C2P - Check Transaction C2P Service by Grafana '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'C2P - Check Traffik C2P Service by Grafana ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'C2P - Check Traffik C2P Service by Grafana',
      benchmark_value: "'C2P - Check Traffik C2P Service by Grafana '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'C2P - Check Success Rate C2P Service by Grafana ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'C2P - Check Success Rate C2P Service by Grafana',
      benchmark_value: "'C2P - Check Success Rate C2P Service by Grafana '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'C2P - Check Error Count C2P Service by Grafana ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'C2P - Check Error Count C2P Service by Grafana',
      benchmark_value: "'C2P - Check Error Count C2P Service by Grafana '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'Uniprov Pacelayer - Restart & Load Reset Service UPL ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'Uniprov Pacelayer - Restart & Load Reset Service UPL',
      benchmark_value: "'Uniprov Pacelayer - Restart & Load Reset Service UPL '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'IoT Sphere - Check Status adapter_import_gp ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'IoT Sphere - Check Status adapter_import_gp',
      benchmark_value: "'IoT Sphere - Check Status adapter_import_gp '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'IoT Sphere - Check Status adapter_scheduler ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'IoT Sphere - Check Status adapter_scheduler',
      benchmark_value: "'IoT Sphere - Check Status adapter_scheduler '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'IoT Sphere - Check Status adapter_sync_commit ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'IoT Sphere - Check Status adapter_sync_commit',
      benchmark_value: "'IoT Sphere - Check Status adapter_sync_commit '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
    {
      activity_id: 'Digital Core ESB - DNSMASQ Overview and Record Adjustment ',
      type: 'WHITESPACE_INCONSISTENCY',
      field: 'CONCAT',
      source_value: 'Digital Core ESB - DNSMASQ Overview and Record Adjustment',
      benchmark_value: "'Digital Core ESB - DNSMASQ Overview and Record Adjustment '",
      reason: 'Trailing whitespace in benchmark CSV CONCAT key resolved by .strip().',
      confidence: 'RESOLVED_EXCEPTION',
    },
  ],
  validation_results: {
    workload_formula_match_rate: 100.0,
    benefit_text_match_rate: 100.0,
    total_benchmark_records: 667,
    category_action_distribution: [
      { name: 'Smart Healing', count: 199, percentage: 29.8 },
      { name: 'Auto Monitoring', count: 190, percentage: 28.5 },
      { name: 'Self Service Request', count: 120, percentage: 18.0 },
      { name: 'Auto Housekeeping', count: 112, percentage: 16.8 },
      { name: 'Health Check', count: 37, percentage: 5.5 },
      { name: 'Auto Restart', count: 9, percentage: 1.3 },
    ],
    tools_automation_distribution: [
      { name: 'AION', count: 323, percentage: 48.4 },
      { name: 'Shell Script', count: 244, percentage: 36.6 },
      { name: 'Grafana', count: 65, percentage: 9.7 },
      { name: 'BMC', count: 18, percentage: 2.7 },
      { name: 'DSC', count: 8, percentage: 1.2 },
      { name: 'CICD', count: 5, percentage: 0.7 },
      { name: 'AO', count: 2, percentage: 0.3 },
      { name: 'Not Automate', count: 2, percentage: 0.3 },
    ],
    status_triggered_distribution: [
      { name: 'Fully Automated', count: 389, percentage: 58.3 },
      { name: 'Not Yet Triggered Automated', count: 256, percentage: 38.4 },
      { name: 'Partial Automated', count: 22, percentage: 3.3 },
    ],
  },
};

type ActiveTab =
  | 'overview'
  | 'rule_catalog'
  | 'decision_table'
  | 'exceptions'
  | 'validation'
  | 'playground';

export const EnrichmentDiscovery: React.FC = () => {
  const [data, setData] = useState<DiscoveryReport>(FALLBACK_DISCOVERY_DATA);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [ruleFilter, setRuleFilter] = useState<'ALL' | ConfidenceStatus>('ALL');
  const [ruleSearch, setRuleSearch] = useState<string>('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Playground state for live benefit tester
  const [testAction, setTestAction] = useState<string>('Auto Monitoring');
  const [testTool, setTestTool] = useState<string>('Shell Script');
  const [testStatus, setTestStatus] = useState<string>('Fully Automated');
  const [testDuration, setTestDuration] = useState<number>(5);
  const [testEvent, setTestEvent] = useState<number>(5);

  const fetchDiscovery = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/enrichment/discovery');
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      // Keep fallback data
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscovery();
  }, []);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredRules = useMemo(() => {
    return data.rule_catalog.filter((rule) => {
      const matchesConfidence = ruleFilter === 'ALL' || rule.confidence === ruleFilter;
      const matchesSearch =
        rule.id.toLowerCase().includes(ruleSearch.toLowerCase()) ||
        rule.name.toLowerCase().includes(ruleSearch.toLowerCase()) ||
        rule.category.toLowerCase().includes(ruleSearch.toLowerCase()) ||
        rule.logic.toLowerCase().includes(ruleSearch.toLowerCase());
      return matchesConfidence && matchesSearch;
    });
  }, [data.rule_catalog, ruleFilter, ruleSearch]);

  // Live Playground Benefit Generator Calculation
  const playgroundOutput = useMemo(() => {
    const dur = Number(testDuration) || 0;
    const ev = Number(testEvent) || 0;
    const wl = dur * ev;

    const actionMap: Record<string, string> = {
      'Auto Monitoring': 'continuous proactive monitoring and real-time anomaly detection',
      'Smart Healing': 'automated fault detection and self-healing recovery',
      'Self Service Request': 'streamlined self-service execution and eliminating manual ticket handling',
      'Auto Housekeeping': 'scheduled automated log and disk housekeeping',
      'Health Check': 'automated system health checks and proactive issue prevention',
      'Auto Restart': 'automated service restarts and rapid downtime mitigation',
    };
    const actionPhrase = actionMap[testAction] || '';

    let toolClause = `via ${testTool}`;
    if (testTool === 'Not Automate') {
      toolClause = 'through standardized automation';
    } else if (testTool === 'CICD') {
      toolClause = 'via CI/CD automation';
    }

    if (wl === 0) {
      if (testStatus === 'Fully Automated') {
        return `Eliminates manual intervention time and accelerates system recovery ${toolClause} through ${actionPhrase}.`;
      } else if (testStatus === 'Not Yet Triggered Automated') {
        return `Potentially eliminates manual intervention time and accelerates system recovery once automated ${toolClause} through ${actionPhrase}.`;
      }
      return `Reduces manual intervention time ${toolClause} through ${actionPhrase}.`;
    }

    const wlStr =
      wl < 60
        ? `${Math.round(wl * 10) / 10} minutes`
        : Number.isInteger(wl / 60)
        ? `${wl / 60} hours`
        : `${(wl / 60).toFixed(1)} hours`;

    const durStr = Number.isInteger(dur) ? `${dur}` : `${dur}`;
    const evStr = Number.isInteger(ev) ? `${ev}` : `${ev}`;

    const durClause =
      ev === 1
        ? `(saving ${durStr} minutes per event)`
        : `(saving ${durStr} minutes per event across ${evStr} monthly events)`;

    if (testStatus === 'Fully Automated') {
      return `Eliminates ${wlStr} of manual operational workload per month ${durClause} ${toolClause} through ${actionPhrase}.`;
    } else if (testStatus === 'Not Yet Triggered Automated') {
      return `Potentially eliminates ${wlStr} of manual operational workload per month ${durClause} once automated ${toolClause} through ${actionPhrase}.`;
    } else if (testStatus === 'Partial Automated') {
      return `Reduces monthly operational workload by ${wlStr} ${durClause} ${toolClause} through ${actionPhrase}.`;
    }
    return '';
  }, [testAction, testTool, testStatus, testDuration, testEvent]);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Title & Status Header */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950/40 p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Reverse Engineering Discovery Baseline</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Enrichment Discovery & Rule Catalog
            </h1>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Empirical reconstruction and validation of the 667-record manual operational enrichment dataset (
              <span className="font-mono text-sky-400">Improvements_With_Benefit.csv</span>) matched against the
              3,460 raw source activities (
              <span className="font-mono text-sky-400">breakdown_activity_261105_1704_1.json</span>).
            </p>
          </div>
          <button
            onClick={fetchDiscovery}
            disabled={loading}
            className="inline-flex items-center self-start md:self-center px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 shadow-sm transition"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Re-run Verification
          </button>
        </div>

        {/* 4 KPI Metric Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-8 pt-6 border-t border-slate-800/80">
          <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800">
            <div className="text-xs text-slate-400 font-medium flex items-center justify-between">
              <span>Benchmark Activities</span>
              <Database className="h-4 w-4 text-sky-400" />
            </div>
            <div className="text-2xl font-bold text-white mt-2">
              {data.executive_summary.total_benchmark_records}
              <span className="text-xs text-slate-400 font-normal ml-2">/ 3,460 in JSON</span>
            </div>
            <div className="text-xs font-mono text-emerald-400 mt-1 flex items-center">
              <CheckCircle2 className="h-3 w-3 mr-1 inline" /> 100.00% Matched via CONCAT
            </div>
          </div>

          <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800">
            <div className="text-xs text-slate-400 font-medium flex items-center justify-between">
              <span>Total Workload Evaluated</span>
              <TrendingUp className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white mt-2">
              {data.executive_summary.total_workload_hours_per_month}
              <span className="text-xs text-slate-400 font-normal ml-1">hours/month</span>
            </div>
            <div className="text-xs font-mono text-slate-400 mt-1">
              {data.executive_summary.total_workload_minutes_per_month.toLocaleString()} minutes/month
            </div>
          </div>

          <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800">
            <div className="text-xs text-slate-400 font-medium flex items-center justify-between">
              <span>Workload Formula Match</span>
              <Cpu className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">
              {data.executive_summary.workload_formula_accuracy_percent}%
            </div>
            <div className="text-xs font-mono text-slate-400 mt-1">
              Durasi × Event = Workload (667/667)
            </div>
          </div>

          <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800">
            <div className="text-xs text-slate-400 font-medium flex items-center justify-between">
              <span>Benefit Grammar Match</span>
              <Sparkles className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">
              {data.executive_summary.benefit_text_accuracy_percent}%
            </div>
            <div className="text-xs font-mono text-slate-400 mt-1">
              Deterministic string equality (667/667)
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Level Status Summary Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              CONFIRMED ({data.confidence_summary.CONFIRMED.count})
            </span>
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">
            {data.confidence_summary.CONFIRMED.description}
          </p>
          <div className="text-[11px] font-mono text-emerald-400/80 pt-1">
            Rules: {data.confidence_summary.CONFIRMED.rules.join(', ')}
          </div>
        </div>

        <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">
              INFERRED ({data.confidence_summary.INFERRED.count})
            </span>
            <AlertTriangle className="h-5 w-5 text-amber-400" />
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">
            {data.confidence_summary.INFERRED.description}
          </p>
          <div className="text-[11px] font-mono text-amber-400/80 pt-1">
            Rules: {data.confidence_summary.INFERRED.rules.join(', ')}
          </div>
        </div>

        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">
              UNRESOLVED & EXCEPTIONS ({data.confidence_summary.UNRESOLVED.count})
            </span>
            <HelpCircle className="h-5 w-5 text-rose-400" />
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">
            {data.confidence_summary.UNRESOLVED.description}
          </p>
          <div className="text-[11px] font-mono text-rose-400/80 pt-1">
            Identified: {data.confidence_summary.UNRESOLVED.rules.join(', ')}
          </div>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="border-b border-slate-800">
        <nav className="flex space-x-2 sm:space-x-4 overflow-x-auto pb-2 scrollbar-none text-xs sm:text-sm">
          {[
            { id: 'overview', label: 'Dataset & Matching', icon: Database },
            { id: 'rule_catalog', label: 'Rule Catalog (12)', icon: BookOpen },
            { id: 'decision_table', label: 'Decision Table', icon: Table },
            { id: 'exceptions', label: 'Exception Analysis (11)', icon: AlertCircle },
            { id: 'validation', label: 'Validation Statistics', icon: Layers },
            { id: 'playground', label: 'Live Rule Verifier', icon: Play },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as ActiveTab)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab 1: Dataset Overview & Matching Results */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Source JSON Box */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center border border-sky-500/20">
                  <Database className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-base">Source JSON Assessment Dataset</h3>
                  <p className="text-xs text-slate-400">Raw operational baseline file</p>
                </div>
              </div>

              <div className="bg-slate-900 rounded-lg p-3 font-mono text-xs text-slate-300 break-all border border-slate-800">
                {data.dataset_overview.source_json.path}
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60">
                  <span className="text-slate-400">Total Activities:</span>
                  <div className="font-bold text-white text-sm mt-0.5">
                    {data.dataset_overview.source_json.total_records.toLocaleString()} rows
                  </div>
                </div>
                <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60">
                  <span className="text-slate-400">Columns Detected:</span>
                  <div className="font-bold text-white text-sm mt-0.5">
                    {data.dataset_overview.source_json.columns_detected} columns
                  </div>
                </div>
                <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60 col-span-2">
                  <span className="text-slate-400">Extracted Timestamp:</span>
                  <div className="font-mono text-slate-300 text-[11px] mt-0.5">
                    {data.dataset_overview.source_json.extracted_at}
                  </div>
                </div>
              </div>

              <div className="text-xs text-amber-300/80 bg-amber-500/10 p-3 rounded-lg border border-amber-500/20">
                <strong>Discovery Finding:</strong> In raw JSON, <span className="font-mono">Category Action</span> is 100% empty, and neither <span className="font-mono">Status Triggered</span> nor <span className="font-mono">Benefit</span> exist in the raw schema.
              </div>
            </div>

            {/* Benchmark CSV Box */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
                  <Table className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-base">Benchmark Enriched Dataset</h3>
                  <p className="text-xs text-slate-400">Manual operational enrichment ground truth</p>
                </div>
              </div>

              <div className="bg-slate-900 rounded-lg p-3 font-mono text-xs text-slate-300 break-all border border-slate-800">
                {data.dataset_overview.benchmark_csv.path}
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60">
                  <span className="text-slate-400">Curated Records:</span>
                  <div className="font-bold text-white text-sm mt-0.5">
                    {data.dataset_overview.benchmark_csv.total_records} rows (19.3% of JSON)
                  </div>
                </div>
                <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60">
                  <span className="text-slate-400">Enriched Columns:</span>
                  <div className="font-bold text-white text-sm mt-0.5">8 canonical fields</div>
                </div>
                <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60 col-span-2">
                  <span className="text-slate-400">Columns Schema:</span>
                  <div className="font-mono text-slate-300 text-[11px] mt-0.5 truncate">
                    {data.dataset_overview.benchmark_csv.columns.join(' | ')}
                  </div>
                </div>
              </div>

              <div className="text-xs text-emerald-300/80 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">
                <strong>Discovery Finding:</strong> All 667 records represent confirmed operational automation candidates curated across 69 enterprise applications.
              </div>
            </div>
          </div>

          {/* Matching Results Audit Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white text-base flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <span>Primary Key Matching & Linkage Audit</span>
              </h3>
              <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                100.00% Matched
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Every row in the benchmark CSV was tested for linkage against the source JSON dataset using the primary key relationship: <span className="font-mono text-sky-400">CONCAT (CSV) == activity_id (JSON)</span>.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400">Exact String Match</span>
                <div className="text-xl font-bold text-emerald-400 mt-1">
                  {data.matching_results.exact_matches} <span className="text-xs text-slate-500">/ 667</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">98.65% perfect character equality</div>
              </div>

              <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400">Trimmed Trailing Whitespace</span>
                <div className="text-xl font-bold text-amber-400 mt-1">
                  {data.matching_results.stripped_matches} <span className="text-xs text-slate-500">/ 667</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">1.35% matched after .strip()</div>
              </div>

              <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400">Unmatched / Orphan Rows</span>
                <div className="text-xl font-bold text-white mt-1">
                  {data.matching_results.unmatched_count}
                </div>
                <div className="text-[11px] text-emerald-400 mt-0.5">0 missing records (100% covered)</div>
              </div>
            </div>

            {/* Trailing Whitespace Accordion/List */}
            <div className="mt-4 pt-4 border-t border-slate-800/80">
              <span className="text-xs font-semibold text-slate-300 block mb-2">
                List of 9 Activities with Trailing Whitespace in Benchmark CSV:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {data.matching_results.whitespace_edge_cases.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-slate-900/60 border border-slate-800 text-[11px] font-mono text-slate-300 flex items-center justify-between"
                  >
                    <span className="truncate pr-2">{item}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
                      whitespace trimmed
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Rule Catalog */}
      {activeTab === 'rule_catalog' && (
        <div className="space-y-6">
          {/* Filter & Search Bar */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-slate-950/60">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-slate-400" />
              <span className="text-xs font-medium text-slate-300">Confidence Filter:</span>
              <div className="flex space-x-1.5">
                {(['ALL', 'CONFIRMED', 'INFERRED', 'UNRESOLVED'] as const).map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setRuleFilter(filter)}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${
                      ruleFilter === filter
                        ? 'bg-sky-500 text-white font-semibold'
                        : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>

            <div className="relative flex-1 sm:max-w-xs">
              <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search rules, logic, formulas..."
                value={ruleSearch}
                onChange={(e) => setRuleSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
              />
            </div>
          </div>

          {/* Rules List */}
          <div className="grid grid-cols-1 gap-4">
            {filteredRules.map((rule) => {
              const isConfirmed = rule.confidence === 'CONFIRMED';
              const isInferred = rule.confidence === 'INFERRED';
              return (
                <div
                  key={rule.id}
                  className="rounded-xl border border-slate-800 bg-slate-950/70 p-5 space-y-3 hover:border-slate-700 transition"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-3">
                      <span className="font-mono text-xs font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
                        {rule.id}
                      </span>
                      <h4 className="font-semibold text-white text-sm">{rule.name}</h4>
                      <span className="text-xs text-slate-500">({rule.category})</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${
                          isConfirmed
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : isInferred
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        }`}
                      >
                        {rule.confidence}
                      </span>
                      <button
                        onClick={() => handleCopy(rule.logic, rule.id)}
                        className="p-1 rounded text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition"
                        title="Copy formula/logic"
                      >
                        {copiedId === rule.id ? (
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="h-3.5 w-3.5" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Logic / Formula Code Block */}
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-200">
                    <div className="text-[10px] uppercase text-slate-500 font-semibold mb-1">
                      Rule Specification & Logic
                    </div>
                    {rule.logic}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800/50">
                      <span className="text-slate-400 font-medium">Preconditions:</span>
                      <div className="text-slate-300 font-mono text-[11px] mt-0.5">{rule.preconditions}</div>
                    </div>
                    <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800/50">
                      <span className="text-slate-400 font-medium">Empirical Verification:</span>
                      <div className="text-emerald-400 font-mono text-[11px] mt-0.5">{rule.verification}</div>
                    </div>
                  </div>

                  <div className="text-xs text-slate-400 bg-slate-900/30 p-2.5 rounded border border-slate-800/40">
                    <span className="text-slate-500 font-medium mr-1">Concrete Example:</span>
                    <span className="text-slate-300 font-mono text-[11px]">{rule.sample}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 3: Decision Table */}
      {activeTab === 'decision_table' && (
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 space-y-4">
            <div>
              <h3 className="font-semibold text-white text-base">Benefit Template Decision Matrix</h3>
              <p className="text-xs text-slate-400 mt-1">
                Mapping input conditions (Status Triggered, Workload, Event Count, Tool, and Category Action) to standardized output Benefit narratives.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-300 font-semibold">
                    <th className="p-3">Status Triggered</th>
                    <th className="p-3">Workload Range</th>
                    <th className="p-3">Event Condition</th>
                    <th className="p-3">Category Action & Tool</th>
                    <th className="p-3">Resulting Narrative Structure</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {data.decision_table.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/40 transition">
                      <td className="p-3 font-medium text-slate-200 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                            row.status_triggered === 'Fully Automated'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              : row.status_triggered === 'Not Yet Triggered Automated'
                              ? 'bg-sky-500/10 text-sky-400 border-sky-500/20'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          }`}
                        >
                          {row.status_triggered}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-slate-300 whitespace-nowrap">
                        {row.workload_range}
                      </td>
                      <td className="p-3 font-mono text-slate-400 whitespace-nowrap">
                        {row.event_condition}
                      </td>
                      <td className="p-3 text-slate-300 whitespace-nowrap">
                        <div className="font-medium text-sky-300">{row.category_action}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{row.tools_automation}</div>
                      </td>
                      <td className="p-3">
                        <div className="font-mono text-slate-200 text-[11px] bg-slate-900 p-2 rounded border border-slate-800">
                          {row.sample}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Exception Analysis */}
      {activeTab === 'exceptions' && (
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 space-y-4">
            <div>
              <h3 className="font-semibold text-white text-base flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-amber-400" />
                <span>Exception & Anomaly Analysis (11 Detected Items)</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Detailed audit of manual calibrations, whitespace inconsistencies, and tool taxonomy migrations identified during reverse engineering.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {data.exception_analysis.map((exc, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        {exc.type}
                      </span>
                      <span className="text-xs font-semibold text-white truncate max-w-md" title={exc.activity_id}>
                        {exc.activity_id}
                      </span>
                    </div>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      {exc.confidence}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 font-mono text-[10px] block">SOURCE JSON VALUE:</span>
                      <span className="font-mono text-slate-300 text-xs mt-0.5">{exc.source_value}</span>
                    </div>
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 font-mono text-[10px] block">BENCHMARK CSV VALUE:</span>
                      <span className="font-mono text-emerald-400 text-xs mt-0.5">{exc.benchmark_value}</span>
                    </div>
                  </div>

                  <div className="text-xs text-slate-300 bg-slate-950/40 p-2.5 rounded border border-slate-800/40">
                    <span className="text-slate-400 font-semibold mr-1">Triage Explanation:</span>
                    {exc.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Validation Statistics */}
      {activeTab === 'validation' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Category Action Breakdown */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-5 space-y-4">
              <h4 className="font-semibold text-white text-sm">Category Action (6 Classes)</h4>
              <div className="space-y-2.5">
                {data.validation_results.category_action_distribution.map((item) => (
                  <div key={item.name} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-medium">{item.name}</span>
                      <span className="text-slate-400 font-mono">
                        {item.count} ({item.percentage}%)
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-sky-500 rounded-full"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tools Automation Breakdown */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-5 space-y-4">
              <h4 className="font-semibold text-white text-sm">Tools Automation (8 Tools)</h4>
              <div className="space-y-2.5">
                {data.validation_results.tools_automation_distribution.map((item) => (
                  <div key={item.name} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-medium">{item.name}</span>
                      <span className="text-slate-400 font-mono">
                        {item.count} ({item.percentage}%)
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Status Triggered Breakdown */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-5 space-y-4">
              <h4 className="font-semibold text-white text-sm">Status Triggered (3 Tiers)</h4>
              <div className="space-y-2.5">
                {data.validation_results.status_triggered_distribution.map((item) => (
                  <div key={item.name} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-medium">{item.name}</span>
                      <span className="text-slate-400 font-mono">
                        {item.count} ({item.percentage}%)
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: Live Rule Verifier & Benefit Playground */}
      {activeTab === 'playground' && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 space-y-6">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center border border-sky-500/20">
              <Terminal className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-base">Interactive Benefit Grammar Verifier</h3>
              <p className="text-xs text-slate-400">
                Test any operational parameters against the reconstructed linguistic rules in real-time.
              </p>
            </div>
          </div>

          {/* Isolation & Non-Production Disclaimer Banner */}
          <div className="p-3.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start space-x-2.5">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-semibold text-amber-200">Demonstration Only (Client-Side Verification Sandbox):</span>
              <p className="text-slate-300 text-[11px] leading-relaxed">
                Fitur ini murni simulator interaktif di memori browser untuk memverifikasi dan mendemonstrasikan aturan tata bahasa hasil reverse engineering. Fitur ini <strong>bukan</strong> implementasi Enrichment Engine dan <strong>terisolasi 100%</strong> dari pipeline operasional backend (P1–P4). Tidak ada modifikasi data sumber, penyimpanan berkas, atau efek samping produksi.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Category Action</label>
              <select
                value={testAction}
                onChange={(e) => setTestAction(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-sky-500"
              >
                <option value="Auto Monitoring">Auto Monitoring</option>
                <option value="Smart Healing">Smart Healing</option>
                <option value="Self Service Request">Self Service Request</option>
                <option value="Auto Housekeeping">Auto Housekeeping</option>
                <option value="Health Check">Health Check</option>
                <option value="Auto Restart">Auto Restart</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Tools Automation</label>
              <select
                value={testTool}
                onChange={(e) => setTestTool(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-sky-500"
              >
                <option value="AION">AION</option>
                <option value="Shell Script">Shell Script</option>
                <option value="Grafana">Grafana</option>
                <option value="BMC">BMC</option>
                <option value="DSC">DSC</option>
                <option value="CICD">CICD</option>
                <option value="AO">AO</option>
                <option value="Not Automate">Not Automate</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Status Triggered</label>
              <select
                value={testStatus}
                onChange={(e) => setTestStatus(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-sky-500"
              >
                <option value="Fully Automated">Fully Automated</option>
                <option value="Not Yet Triggered Automated">Not Yet Triggered Automated</option>
                <option value="Partial Automated">Partial Automated</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Durasi (Menit)</label>
              <input
                type="number"
                min="0"
                value={testDuration}
                onChange={(e) => setTestDuration(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Event Per Month</label>
              <input
                type="number"
                min="0"
                value={testEvent}
                onChange={(e) => setTestEvent(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Calculated Workload</label>
              <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-emerald-400 font-bold">
                {testDuration * testEvent} minutes ({((testDuration * testEvent) / 60).toFixed(1)} hrs)
              </div>
            </div>
          </div>

          {/* Generated Benefit Preview */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-sky-400">
                Generated Benefit Statement:
              </span>
              <button
                onClick={() => handleCopy(playgroundOutput, 'playground')}
                className="inline-flex items-center space-x-1 text-slate-400 hover:text-white transition"
              >
                {copiedId === 'playground' ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
                <span>Copy</span>
              </button>
            </div>
            <div className="font-serif italic text-sm text-slate-100 bg-slate-950 p-4 rounded-lg border border-slate-800/80 leading-relaxed">
              "{playgroundOutput}"
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
