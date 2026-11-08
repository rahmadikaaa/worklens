# WORKLENS V1 — Design Specification

**Product:** WORKLENS  
**Full Name:** Workload & Automation Intelligence  
**Target Organization:** L1 AGIT  
**Version:** 1.0  
**Design Status:** Direction Locked — Specification Draft  
**Primary User:** L1 Operations  
**Navigation:** Topbar  
**Visual Direction:** Executive Dashboard  
**Activity Detail:** Side Drawer  

---

## 1. Product Vision

WORKLENS is an operational intelligence dashboard designed to help L1 AGIT understand, monitor, and analyze workload distribution, automation progress, activity status, and data quality.

The application provides a unified interface to explore operational activities and identify opportunities, gaps, and inconsistencies in automation data.

### Primary Objectives

1. Provide visibility into operational workload.
2. Monitor automation status and progress.
3. Identify workload distribution across criticality and organizational units.
4. Explore individual activities and their supporting information.
5. Detect data quality issues and inconsistencies across source datasets.
6. Provide traceable metric definitions and business rules.

### Product Principle

WORKLENS must distinguish between:
- Operational facts.
- Automation implementation status.
- Automation execution status.
- Assessment progress.
- Workload estimates and calculated benefits.
- Data quality findings.

These dimensions must never be combined into one ambiguous completion metric.

---

## 2. Target User

### Primary User: L1 Operations

L1 users need to:
- Understand the overall operational situation.
- Identify activities requiring attention.
- Investigate individual activity records.
- Review automation progress.
- Validate workload information.
- Identify inconsistencies between datasets.

### Secondary Audience

Management may use the dashboard for read-only operational visibility.

V1 prioritizes L1 workflows. Management-specific reporting and access controls can be expanded in subsequent versions.

---

## 3. Information Architecture

The application uses a horizontal top navigation.

### Main Navigation

1. Overview
2. Workload
3. Automation
4. Activities
5. Data Quality
6. Definitions

### Global Application Header

Components:
- WORKLENS logo and product name.
- Main navigation.
- Current dataset / baseline indicator.
- Data freshness indicator.
- User or workspace context.

The header should remain consistent across all main pages.

---

## 4. Page Specifications

### 4.1 Overview

Purpose: Provide an executive-style summary of operational conditions.

Components:

**A. KPI Summary**
- Total Activities
- Total Workload Before
- Total Workload After
- Assessment Done
- Data Quality Issues

**B. Workload Overview**
- Positive workload records.
- Zero workload records.
- Invalid or missing workload records.

**C. Criticality Distribution**
- Mission Critical.
- Business Critical.
- Business Important.
- Business Support.
- Unclassified.

**D. Operational Insights**
- Activities requiring review.
- Workload anomalies.
- Automation status observations.
- Unmatched or conflicting records.

**E. Recent Data Information**
- Dataset name.
- Snapshot date.
- Record count.
- Last processing timestamp.

Overview should prioritize key information rather than displaying every available chart.

### 4.2 Workload Analytics

Purpose: Analyze operational workload distribution and potential workload reduction.

Components:
- Workload Before vs Workload After.
- Workload distribution by criticality.
- Workload distribution by department.
- Workload distribution by application.
- Workload distribution by activity type.
- Workload records requiring validation.

All workload values must clearly identify their units and time basis.

Potential workload reduction and observed workload reduction must be displayed separately.

### 4.3 Automation Progress

Purpose: Monitor automation implementation and execution status.

Components:

**A. Automation Status**
- Already Automation.
- To Be Automated.
- Not Yet Solution.
- Other source-defined categories.

**B. Triggered Status**
- Fully Automated.
- Partial Automated.
- Not Yet Triggered Automated.

**C. Criticality Breakdown**
- MC.
- BC.
- BI.
- BS.
- Unclassified.

**D. Operational Category**
- Alert & Incident.
- Change.
- Service Request & Complaint Handling.
- Other source-defined categories.

**E. Activity Monitoring**
- Automated activities.
- Partially automated activities.
- Activities awaiting triggering.
- Activities requiring validation.

Important: Automation implementation does not automatically mean the automation has been triggered or successfully executed.

### 4.4 Activity Explorer

Purpose: Provide searchable access to operational activity records.

Components:
- Search by activity name.
- Filter by application.
- Filter by department.
- Filter by criticality.
- Filter by assessment status.
- Filter by automation category.
- Filter by automation tool.
- Filter by workload condition.
- Sort and paginate records.

The table should prioritize:
- Activity Name.
- Application.
- Department.
- Criticality.
- Workload.
- Automation Status.
- Assessment Status.

Clicking a record opens a side drawer without navigating away from the activity list.

### 4.5 Activity Detail Drawer

Purpose: Display the complete context of an individual activity.

Drawer sections:

**A. Identity**
- Activity ID.
- Application.
- Activity Name.
- CONCAT.

**B. Organization**
- Division.
- Department.
- Criticality.

**C. Workload**
- Workload Before.
- Workload After.
- Duration.
- Duration After.
- Events per Month.

**D. Improvement**
- Improvement Category.
- Category Notes.
- Additional Notes.
- New Improvement Category Fixed.

**E. Automation**
- Automation / Manual.
- Tools.
- Tools Automation.
- FMC / Mobile.
- Ops Activity.

**F. Assessment & Execution**
- Assessment Status.
- Status.
- Phase.
- Team QC.
- SOP Name.
- Action By.

**G. Documentation**
- Link Confluence.
- Link Wiki.
- Other available supporting references.

**H. Data Quality**
- Validation findings.
- Missing fields.
- Conflicting source values.
- Reconciliation status.

The drawer must preserve original source values and clearly distinguish derived values from source fields.

### 4.6 Data Quality & Reconciliation

Purpose: Make data inconsistencies visible and traceable.

Components:
- Missing value summary.
- Invalid workload summary.
- Duplicate activity ID.
- Duplicate CONCAT.
- Source-only records.
- Matched records.
- Conflicting values.
- Manual overrides.
- Validation status.

Each finding should provide:
- Record identity.
- Source dataset.
- Original source value.
- Comparison value, if available.
- Issue category.
- Review status.

No automatic source correction is allowed.

### 4.7 Definitions

Purpose: Provide a single reference for metric definitions and business rules.

Components:
- Metric Dictionary.
- Formula.
- Unit.
- Source dataset.
- Calculation method.
- Business interpretation.
- Known limitations.
- Decision reference.
- Definition status.

Definitions should be classified as:
- Confirmed.
- Provisional.
- Pending SME Confirmation.
- Deprecated.

---

## 5. Visual Design System

### Design Direction

Executive dashboard with operational clarity.

Characteristics:
- Clean enterprise interface.
- Neutral background.
- Strong typography hierarchy.
- Large KPI values.
- Restrained use of colors.
- Compact but readable data tables.
- Consistent spacing.
- Minimal decorative elements.

### Color Semantics

- Neutral: General information.
- Green: Healthy / validated.
- Amber: Warning / requires review.
- Red: Critical / invalid.
- Blue: Informational / in progress.

Color must not be the only indicator of status. Include text labels.

### Layout

- Topbar navigation.
- Main content centered within a consistent maximum width.
- KPI cards at the top of relevant pages.
- Charts and insights below KPI sections.
- Tables near the bottom.
- Side drawer for activity details.

### Responsive Behavior

Desktop is the primary target.

Tablet and mobile should retain:
- Navigation accessibility.
- KPI readability.
- Filter usability.
- Drawer access.

Large data tables may use horizontal scrolling on smaller screens.

---

## 6. Global Interaction Rules

1. Global filters must behave consistently across relevant pages.
2. Opening an activity drawer must preserve current search and filter state.
3. Closing the drawer returns the user to the same table position.
4. Every chart must have a clear title, unit, and data source context.
5. Clicking a chart segment should enable relevant drill-down where supported.
6. Empty states must explain why no data is available.
7. Loading and error states must be explicit.
8. Export functionality must identify the dataset and applied filters.
9. Source data must remain immutable.
10. Derived metrics must be distinguishable from source values.

---

## 7. Data Source Architecture

WORKLENS V1 must preserve the separation between datasets.

### A. Operational Dataset
Official baseline: `breakdown_activity_261106_1112.json`

- 3,460 records.
- Operational activity information.
- Workload information.
- Criticality.
- Assessment status.
- Automation classification.

### B. Benefit Dataset
Source: `Improvements_With_Benefit.csv`

- 667 records.
- Benefit and automation-related information.
- Triggered status.
- Operational category.
- Workload benchmark.

### C. Universe / Progress Tracker
Reference population: 884 activities.

- Universe target.
- Completed progress.
- Remaining progress.
- Criticality-based tracking.

These datasets must not be merged into a single population without an approved mapping and reconciliation rule.

---

## 8. Data Governance

### Immutable Source Principle

- Raw datasets are read-only.
- No automatic correction.
- No silent normalization.
- All transformations must be traceable.
- Derived fields must retain calculation lineage.

### Reconciliation Principle

Matching records must use the approved identity strategy.

CONCAT normalization may be used for comparison, but original source values must remain unchanged.

Fuzzy matching must not silently establish record identity.

### Metric Separation

The following concepts must remain distinct:

- Assessment Completion.
- Automation Implementation.
- Automation Triggering.
- Universe Completion.
- Workload Before.
- Workload After.
- Workload Saved.
- EOD Workload Reduction.

No metric should be presented as interchangeable with another.

---

## 9. Access & Roles

### L1
- View operational dashboard.
- Explore activity records.
- Review data quality findings.
- Inspect source discrepancies.
- Export permitted datasets.

### Management
- Read-only dashboard access.
- View aggregate metrics and operational insights.

Detailed permission enforcement and authentication are implementation concerns to be finalized before production release.

---

## 10. V1 Scope

### Included
- Executive Overview.
- Workload Analytics.
- Automation Progress.
- Activity Explorer.
- Activity Detail Drawer.
- Data Quality & Reconciliation.
- Metric & Business Definitions.
- Dataset identification and lineage.

### Excluded from Initial V1
- Automatic source correction.
- Real-time automation telemetry.
- Automatic approval of business decisions.
- Predictive workload forecasting.
- Financial monetization of workload savings.
- Unverified Universe Tracker mapping.
- Automated synchronization with external systems.

---

## 11. Acceptance Criteria

V1 design is accepted when:

1. All six main navigation sections are defined.
2. Overview provides an executive summary.
3. Activity Explorer supports search and filtering.
4. Activity Detail Drawer displays complete record context.
5. Data Quality provides traceable findings.
6. Workload and automation metrics are clearly separated.
7. Each displayed metric has a defined source and unit.
8. Unverified metrics are explicitly marked.
9. Raw source data remains immutable.
10. The design supports desktop-first operational use.

---

## 12. Design Decisions Locked

| Decision | V1 |
|---|---|
| Primary User | L1 Operations |
| Navigation | Topbar |
| Visual Direction | Executive |
| Activity Detail | Side Drawer |
| Primary Platform | Desktop Web |
| Data Principle | Immutable Source |
| Metric Principle | Explicit Definitions |
| Reconciliation | Traceable, No Silent Correction |

