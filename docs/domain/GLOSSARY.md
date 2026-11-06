# SOP L1 AGIT Workload Assessment & Automation

Domain vocabulary and authoritative definitions for assessing SOP activities, measuring workload reduction, and identifying automation opportunities across L1 operational workflows.

## Language

### Operational Entities & Scope

**Breakdown Activity**:
The primary assessment unit where exactly one row in the operational sheet represents exactly one discrete activity.
_Avoid_: Task breakdown, sub-activity, log line

**Activity ID**:
The immutable primary identifier assigned upstream to uniquely identify an operational activity across runs.
_Avoid_: Task key, composite ID, row number

**Activity Type**:
The operational classification of a breakdown activity indicating its routine function (such as Backup, Health Check, or Housekeeping).
_Avoid_: Category, job type

### Assessment & Improvement

**Improvement Category**:
The directional improvement decision established by L1 for an activity, taking values `Automation`, `As Is`, or `Dismantled`.
_Avoid_: Action category, future state

**Category Notes**:
The state descriptor detailing the operational stage of an activity under its designated Improvement Category.
_Avoid_: Remark, comment, detail status

**Target Mapping**:
The canonical business rule pairing an Improvement Category to its expected Category Notes: `Automation` maps to `Already Automation`, `As Is` maps to `To Be Automated`, and `Dismantled` maps to `Dismantled`.
_Avoid_: Workflow transition, auto-mapping

**Already Automation**:
The condition where an automation tool, script, or bot has already been developed and exists for the activity, regardless of whether it has been triggered or whether it encountered execution errors.
_Avoid_: Active bot, executed automation

**To Be Automated**:
The planned target state where an automation solution is slated for future construction, even if development has not yet begun.
_Avoid_: Automation backlog, pending tool

**Dismantled**:
The operational decision to eliminate an unnecessary manual activity from the standard operating procedure.
_Avoid_: Deleted task, obsolete activity, retired step

**Not Yet Solution**:
A transient assessment condition for a `To Be Automated` activity where an automation tool has not yet been identified, confirmed, or verified for feasibility.
_Avoid_: Impossible automation, blocked task

**New Improvement Category Fixed**:
The formal human correction made exclusively by L1 to resolve an inconsistency or finalize an assessment decision.
_Avoid_: AI auto-fix, system override

### Tools & Automation Scope

**Tools**:
The software applications, utilities, or consoles actually used during current manual execution of an activity.
_Avoid_: Current stack, software list

**Tools Automation**:
The automation technologies, scripts, APIs, or bots designated for existing or future automated execution of an activity.
_Avoid_: Bot name, target script

**Automation Opportunity**:
A viable candidate activity that can be automated through Automation Orchestration (AO) or non-AO solutions (such as shell scripts, APIs, or RPA).
_Avoid_: Bot lead, RPA candidate

### Roles & Follow-up

**Action By**:
The organizational tier accountable for executing the next follow-up action on an activity assessment.
_Avoid_: Assignee, ticket owner

**L0**:
Operational level responsible for routine execution and live monitoring of stabilized tasks.
_Avoid_: Operator, helpdesk

**L1**:
Primary operational owners who execute SOP activities, conduct workload assessments, and lead improvement initiatives.
_Avoid_: Frontline, agent

**L2**:
Technical engineering and escalation support responsible for tool construction, script development, and feasibility consulting.
_Avoid_: Developer, admin, tier 2

**Management**:
Executive stakeholders who review aggregated efficiency summaries and drill down into activity details with read-only access.
_Avoid_: Admin, approver

### Workload Metrics

**Workload**:
The initial monthly effort required for an activity, defined as baseline duration in minutes multiplied by monthly event frequency.
_Avoid_: Time spent, effort score

**Workload After**:
The estimated monthly effort remaining after improvement, currently modeled under a uniform static assumption of ten percent of baseline workload.
_Avoid_: Target duration, post-workload

**Workload Saved**:
The calculated monthly operational time eliminated by an improvement, expressed in minutes per month.
_Avoid_: Time saved, efficiency gain

**Annualized Workload Saved**:
The projected yearly operational time eliminated by an improvement, calculated as twelve times the monthly workload saved.
_Avoid_: Yearly saving, annual efficiency

### Operational Workspace & MVP Modules

**Assessment Workspace**:
The primary operational space for Tim L1 to inspect row-level assessment metrics and make human editing decisions.
_Avoid_: Edit form, spreadsheet editor

**Monitoring Dashboard**:
The executive reporting view presenting aggregated workload metrics, progress distributions, and activity drill-down capabilities.
_Avoid_: Admin console, BI dashboard

**Quality Review**:
The dedicated resolution panel isolating semantic data anomalies, Q14 target mapping deviations, and unresolved activity identities.
_Avoid_: Error log, bug tracker

**Follow-up Management**:
The operational tracking panel organizing next-step actions by accountable operational tier (`L0`, `L1`, `L2`).
_Avoid_: Jira board, task manager

### Operational Architecture & SharePoint Integration

**Operational Source of Truth**:
The authoritative master workbook hosted on SharePoint (`SOP L1 AGIT.xlsx`, sheet `Breakdown Activity`) from which operational data is extracted and to which authorized assessment decisions are synchronized.
_Avoid_: Central database, master CSV

**SharePoint Sync Payload**:
The structured delta JSON artifact exported from the Assessment Workspace containing only L1-authorized column mutations keyed by `activity_id`, formatted for consumption by Power Automate.
_Avoid_: Bulk update CSV, patch file

**Formula Immutability**:
The architectural invariant guaranteeing that no operational process or automation flow writes to or overwrites Excel formula cells (such as `Workload`, `DIV`, or `CONCAT`).
_Avoid_: Sheet lock, cell freezing

**Trigger Loop Prevention**:
The control mechanism combining service-account trigger exclusion, cell-level idempotency checking, and unique batch fingerprinting to prevent Power Automate flows from re-triggering themselves upon writing back updates.
_Avoid_: Recursive prevention, cycle breaker

**Idempotency Key**:
A deterministic SHA-256 fingerprint generated from the run identifier and sorted mutation items to guarantee that duplicate update payloads are recognized and processed at most once.
_Avoid_: Nonce, random token



