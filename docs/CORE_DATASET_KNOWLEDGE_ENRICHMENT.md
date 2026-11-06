# WORKLENS — Core Dataset Knowledge Enrichment

**Status:** Enrichment draft based on the supplied authoritative analysis and business Q&A  
**Purpose:** Connect empirical dataset findings to the user's business definitions and assessment workflow without changing source data, recomputing the original analysis, or inventing unresolved rules.

## 1. Source hierarchy and interpretation rules

This enrichment uses two primary references:

1. `CORE_DATASET_COMPREHENSIVE_ANALYSIS.md` — empirical baseline, schema, profiling, data-quality findings, formula checks, and statistical observations.
2. `Workload_Enrichment_Tanya_Jawab_Q1-Q51(2).md` — recorded business answers Q1–Q51. It is a record of user decisions, not a final technical specification for every detail.

Apply these labels throughout:
- **Dataset fact:** explicitly reported by the comprehensive analysis.
- **Business decision:** explicitly answered in Q1–Q51.
- **Interpretation:** a reasoned connection between a fact and a business decision.
- **Open question / validation required:** not decided or not proven by the supplied sources.

The business Q&A defines the intended meaning and ownership of assessment. The dataset analysis describes what the current source contains. Neither should silently overwrite the other.

## 2. Critical source reconciliation issue

The two source materials describe different dataset snapshots:

| Attribute | Comprehensive Analysis baseline | Separately uploaded raw JSON |
|---|---:|---:|
| Record count | 3,460 | 3,456 |
| Detected source columns | 36 | 36 |
| Attributes including `activity_id` | 37 | 37 |
| Extraction timestamp | 2026-11-05T10:04:16.062Z | 2026-11-03T16:46:57.068Z |
| SHA-256 | `2ee85f439665495b49a2ff8913f1cf7ce91d700a114a2d19ac33dbb006ef4e90` | `bd51be956dfb598fd4f5832592970556a5fa7e3f871deaba56640b43f415b869` |

The uploaded JSON has 3,456 records, 37 keys per record, and 3,456 distinct non-empty `activity_id` values. It is not byte-identical to the 3,460-record snapshot described by the analysis document.

**Handling decision for this enrichment:** preserve the comprehensive analysis as the declared baseline reference (3,460) and record the raw JSON mismatch as unresolved. Do not combine counts, infer which four rows are missing, or claim that the analysis statistics have been revalidated against the uploaded JSON. A canonical source snapshot must be selected before implementation or refreshed profiling.

## 3. Business purpose and assessment model

### 3.1 Purpose

**Business decisions (Q1–Q6):**
- Assess all activities in `Breakdown Activity`, one row representing one activity.
- Identify automation opportunities, validate existing automation, identify manual activities, identify activities that may be dismantled, and assess potential workload reduction.
- L1 AGIT owns and performs the assessment.
- L2 provides technical knowledge or confirmation when L1 determines it is needed; L2 feedback is not mandatory for every activity.
- Assessment evidence may include activity description, SOP/documentation, L2 explanation, As-Is observation, current tools/application, automation information, process constraints, improvement target, PIC/stakeholder, duration, and frequency. Not every evidence type is mandatory for every row.
- If information is incomplete, L1 may defer assessment or make a provisional assessment while explicitly recording the information gap.

**Enrichment interpretation:** the system is an L1 assessment workspace and decision-support process, not an automatic classifier that replaces L1 judgment. Missing context should be visible as a limitation or review need, not silently filled by AI.

### 3.2 Meaning of assessment completion

**Business decisions (Q7–Q10):**
- `Assessment Status` is intended to reflect assessment progress, information completeness, and L2 validation where applicable.
- Current `Done` values do not automatically prove that all dimensions are complete.
- `Done` means L1 has completed its assessment, considers the information sufficient, and has a category decision. L2 confirmation is required only when the case needs it.
- L1 decides when L2 input is necessary, for example when the process description or SOP is unclear, an automation/dismantle opportunity needs technical assessment, or confirmation is needed.

**Dataset fact:** the baseline analysis reports 706 blank `Assessment Status` values (20.40%) and one populated value (`Done`). It also reports 3,460 rows in its baseline.

**Interpretation:** the current status field is a limited signal. It cannot, by itself, prove that evidence is complete, that L2 has validated a case, or that the decision is correct. A future quality/review capability should distinguish an observed status value from the richer business meaning of completion. The exact status lifecycle and validation rules remain intentionally undecided.

## 4. Business semantics of assessment fields

| Field | Meaning from Q&A | How to interpret current data | Guardrail |
|---|---|---|---|
| `Improvement Category` | L1's improvement direction: `Automation`, `As Is`, or `Dismantled` (Q12) | Decision category, not a statement of current execution method | Do not infer it solely from `Automation/Manual` |
| `Category Notes` | Further condition/status of the improvement direction (Q13) | Adds the status/next state | Do not treat it as a synonym for `Improvement Category` |
| Target mapping | `Automation` → `Already Automation`; `As Is` → `To Be Automated`; `Dismantled` → `Dismantled` (Q14) | Intended mapping; current values may be inconsistent | Flag inconsistencies for L1; do not auto-correct source (Q17–Q18) |
| `New Improvement Category Fixed` | Correction result of the earlier `Improvement Category` (Q19) | Corrected assessment outcome | It is not an initial recommendation generated by the system |
| `Automation/Manual` | Actual execution condition at assessment time (Q21–Q24) | Whether the activity is manual or automated now | Partial automation still counts as `Automation`; not an improvement decision |
| `Tools` | Tools actually used now (Q25) | Current environment/tool evidence | Do not populate from planned tools |
| `Tools Automation` | Existing and/or planned automation tools in one field (Q26–Q28) | Can describe current or future solution | Interpret alongside category, notes, and actual execution state |
| `Action by` | Party responsible for follow-up (Q42–Q44) | Follow-up ownership | Do not assume L2 owns the activity; L1 owns assessment |
| `Assessment Status` | Assessment progress/completeness and applicable L2 validation (Q8–Q9) | Current data has limited values | `Done` is not an automatic completeness certificate |

### 4.1 Category and solution-state distinctions

The Q&A makes the following distinctions:

- `Already Automation` means a tool/script/AO has been created or is available. It does not need to have run before, been triggered by an event, or succeeded operationally (Q16, Q33–Q35).
- `To Be Automated` means automation is planned; implementation need not have started (Q16).
- `Not Yet Solution` means a solution has not yet been found, search has not succeeded, L2 support/coordination may be needed, or feasibility is not confirmed. It does **not** mean automation is impossible (Q29–Q31).
- A case may be `To Be Automated` while also having `Not Yet Solution`; the exact representation of both in the same `Category Notes` cell is not decided (Q31).
- Once a solution is found, the note remains `To Be Automated` until the automation is actually created (Q32).
- If an existing automation has failed, it remains `Already Automation` because the tool has been created; operational repair is a separate concern (Q35).
- Monitoring is an operational process after assessment, not part of assessment status (Q36).

**Interpretation:** the assessment data models at least three separate concepts: improvement direction, solution maturity/availability, and current execution condition. They should not be collapsed into one status.

## 5. Workload: metric meaning and limitations

### 5.1 Business definition

**Business decisions (Q37–Q40):**
- `Workload` is the total monthly workload for one activity.
- Formula: `Durasi (Menit) × Event Per Month`.
- Unit: minutes per month.
- `Durasi after` and `Workload after` are estimates for discussion and can currently be ignored.
- The current `Workload after` assumption is static at 10% of `Workload` before, intended to apply to all activities; it is not an actual post-improvement measurement.

**Dataset facts from the baseline analysis:**
- Formula reconciliation is reported as exact for 3,080 complete rows for both `Workload` and `Workload after`.
- 3,028 rows follow the 10% duration-after ratio; 33 rows are reduced to zero and 19 rows have custom ratios.
- 380 rows have blank `Workload`.
- Among the 380 blank-workload rows, the analysis describes 215 with duration/event/workload all blank, 162 with operands present but text pollution affecting calculation, and 3 with duration present but event blank.
- 80 duration values contain text and 75 event-frequency values contain text.
- Decimal fractions use comma notation, such as `0,333333333` and `1,5`.

**Important distinction:** the Q&A states the intended business assumption (10% after) for all activities. The empirical baseline reports that the current populated data does not follow that pattern uniformly. This is a difference between a business rule/assumption and observed source values, not permission to rewrite the source or force all records to 10%.

### 5.2 Workload-saving caution

Q41 explicitly says the workload-saving formula already exists in a project artifact and should be referenced rather than reconstructed. The comprehensive analysis reports `Workload Saved = Workload - Workload after` in its methodology, but the Q&A instructs the next work to consult the existing artifact. Therefore, this enrichment does not redefine or implement the formula.

The current `Workload after` is an assumption, not measured realized savings. Any dashboard/report must label it as estimated/assumed and must not present it as actual realized time saved unless a separate measurement source is provided.

### 5.3 Data quality impact

The baseline analysis reports:
- 380 blank workload values (10.98% of 3,460).
- Numeric pollution in `Durasi (Menit)` and `Event Per Month`.
- Indonesian decimal-comma formatting.
- A zero-heavy distribution: 1,605 of 3,080 valid workload records have workload 0.

**Interpretation:** zero workload, missing workload, and unparseable workload are three different states. A zero may reflect zero event frequency or zero duration; blank may mean not estimated or not calculable; text pollution is a data-quality issue. They must not be merged into one generic “no workload” bucket.

The baseline analysis also reports a highly skewed distribution and a very large OneDrive backup outlier. Aggregate workload and rankings should therefore be accompanied by distributions and drill-down context; a single mean or total can be dominated by outliers.

## 6. What the current dataset says about readiness

This section connects source findings to business use without creating new validation rules.

| Dataset finding in baseline analysis | Business relevance | Safe interpretation |
|---|---|---|
| `activity_id` is reported unique and equivalent to `APPS + " - " + ACTIVITY NAME` for all 3,460 baseline rows | Stable row-level assessment identity | Suitable as the baseline's reported identity key; revalidate against the canonical snapshot before implementation |
| 380 blank workload values | Potential benefit cannot be quantified for those rows from current workload fields | Keep as unknown/unavailable; do not assume zero |
| 80 duration and 75 event text-polluted values | Workload calculation reliability | Mark as data-quality exceptions; do not silently coerce uncertain values |
| Five fields reported 100% empty: `Link Wiki`, `Category Action`, `Confirmation Tower/L2`, `Support Needed`, `Module AO` | Some follow-up/context fields are not populated in the baseline source | Empty source columns are not evidence that the business concept is unnecessary |
| `Tools` has 99 variants and 60.90% missing | Technical context for solution feasibility is incomplete/fragmented | Current tool coverage is insufficient to infer tool feasibility for every row |
| `Action by` is 79.13% missing | Follow-up accountability is not comprehensively represented | Do not assume an owner where the field is empty |
| `Assessment Status` is 20.40% missing and populated as `Done` | Progress tracking is incomplete and semantically limited | Do not treat current status as full evidence of assessment quality |
| Lookup fields contain `#N/A` values | Organizational/application metadata may be incomplete | Preserve and flag lookup failures; do not invent department/division values |
| `Link Confluence` includes missing values and 7 non-URL notes | SOP evidence may not be directly accessible | A link field can contain a note; validate URL-ness before treating it as documentation |
| `Category Action` is empty in source but appears in a separate 667-row benchmark CSV (per analysis) | The benchmark contains later/manual enrichment | Do not attribute benchmark labels to the original source without provenance |

## 7. Implications for the six MVP modules

Q50 explicitly identifies six modules. The following maps only supported business needs and source evidence; detailed UI layout, validation rules, and workflows remain open.

### 7.1 Assessment Workspace (L1)
- Primary working area for L1 to view, review, and manage each activity.
- Supports per-activity assessment decisions and relevant evidence.
- Must preserve the distinction between actual execution (`Automation/Manual`), improvement direction (`Improvement Category`), and solution state (`Category Notes`).
- L1 is the owner and editor.

### 7.2 Monitoring Dashboard (Management)
- Summary of activity totals, assessment status, progress, and results.
- Management access is read-only, with summary and drill-down to activity detail.
- Do not infer Management edit rights or comment/feedback rights; those are not established.

### 7.3 Download Enriched CSV
- Provides reusable enriched assessment data.
- Source CSV/workbook remains immutable (Q&A closing notes).
- Enrichment output must remain distinguishable from original source fields and values.

### 7.4 Generate Assessment Report
- Summarizes assessment results, findings, and recommendations.
- Any workload-after or savings values based on the 10% assumption must be labelled as estimates, not actual measured outcomes.
- Do not invent recommendations where evidence is insufficient.

### 7.5 Quality Review
- Makes inconsistencies and records requiring review visible.
- Q&A directs inconsistent category mappings to L1 review; do not auto-correct source.
- Quality findings should distinguish missing data, invalid/polluted values, lookup failures, and business ambiguity.

### 7.6 Follow-up Management
- Tracks follow-up, coordination, and `Action by`.
- L1 owns assessment; L2 supports when required.
- Detailed relationships between tools and follow-up were explicitly deferred.

## 8. Roles and access model

| Role | Supported responsibility/access |
|---|---|
| L1 | Assessment owner; performs assessment; decides when L2 input is needed; can edit assessment, `Improvement Category`, `Category Notes`, Quality Review, and Follow-up |
| L2 | Technical support/knowledge/confirmation when requested by L1; not the activity owner |
| Management | Read-only; can view summary and drill down to activity details |
| L0 | Operational responsibility is mentioned in the Q&A, but detailed workflow is intentionally not elaborated because the project focuses on L1 |

Management comment/feedback permission is undecided. Do not add it to the access model without a new decision.

## 9. Explicitly unresolved items — do not assume

The Q&A explicitly defers:
1. Detailed lifecycle from initial status through `Done`.
2. Detailed data validation rules.
3. Detailed relationship between tools and follow-up.
4. How to represent `To Be Automated` together with `Not Yet Solution` in one `Category Notes` cell.
5. Detailed dashboard pages, components, filters, and visualizations.
6. Management edit/comment/feedback permissions.
7. Reconstructing the workload-saving formula without consulting the existing project artifact.

Additional evidence/reconciliation items from the supplied sources:
8. Which dataset snapshot is canonical: the 3,460-row analysis baseline or the separately uploaded 3,456-row JSON.
9. Whether the 380 baseline rows without workload should be estimated by L1/Tower or excluded from benefit aggregation.
10. Why `Tools` is missing for 2,107 baseline records.
11. Whether duration strings such as `30 menit` may be officially normalized automatically.
12. How to resolve lookup `#N/A` values, including ERICA and HSS.
13. Whether the five entirely empty columns should remain in the source schema or be deprecated.

These are not decisions made by this enrichment.

## 10. Recommended knowledge and implementation guardrails

These are direct consequences of the supplied decisions and facts, not new business policy:

1. **Immutable source:** never overwrite the original workbook/CSV/JSON. Store enrichment and corrections separately.
2. **Traceability:** every enriched conclusion should be traceable to source fields, an explicit Q&A decision, or a clearly labelled inference.
3. **Human ownership:** L1 remains the decision-maker. AI can surface evidence, inconsistency, and candidate reasoning; it should not silently finalize or auto-correct business decisions.
4. **Separate concepts:** keep current execution, improvement direction, solution maturity, assessment progress, and operational monitoring distinct.
5. **No false precision:** missing/unparseable workload is not zero; assumed workload reduction is not measured realized savings.
6. **Conditional L2 involvement:** do not require L2 approval for every row.
7. **Role-based access:** L1 edit; Management read-only; do not infer additional permissions.
8. **Snapshot integrity:** record file identity, extraction timestamp, record count, and checksum for each dataset run. Do not compare metrics across snapshots without reconciliation.
9. **No invented rules:** preserve unresolved items as unresolved until the user decides them.

## 11. Overall synthesis

WORKLENS is intended to support L1 AGIT in assessing every activity, deciding whether it should remain As Is, be automated, or be dismantled, documenting solution maturity and follow-up, and exposing assessment progress and quality to Management.

The empirical baseline is useful for understanding the current dataset's structure, workload distribution, and quality limitations. It does not prove that every activity has sufficient evidence for a decision. In particular, missing workload, incomplete tool information, lookup failures, blank follow-up fields, and limited assessment-status semantics constrain what can safely be concluded.

The key product principle is therefore: **use the dataset as evidence, use Q1–Q51 as the recorded business meaning, and keep L1 accountable for decisions.** The system should make gaps and inconsistencies visible rather than hiding them through automatic correction or unsupported inference.

---
*Prepared from the two supplied knowledge documents and a direct metadata check of the separately uploaded JSON. No source dataset or original analysis output was modified.*
