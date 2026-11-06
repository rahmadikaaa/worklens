---
name: grill-with-docs
description: Orchestrate systematic discovery, relentless grilling, and persistent technical documentation (ADRs, Glossaries, Specifications, and PRDs) as decisions crystallize.
---

# Grill with Docs

Orchestrate the complete lifecycle from ambiguous requirements to production-grade technical documentation. This skill combines active requirements discovery and relentless grilling with continuous documentation so that no decision is lost in conversation history.

## The 4-Phase Discovery & Documentation Workflow

```text
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  1. DISCOVERY   │ ────> │   2. GRILLING   │ ────> │  3. DECISION    │ ────> │ 4. PERSISTENT   │
│ Fact Gathering  │       │  Design Tree    │       │ Consensus &     │       │ DOCUMENTATION   │
│ Context Mapping │       │  Frontier Q&A   │       │ Trade-offs      │       │ ADR/Spec/Glossary│
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

### Phase 1: Context Discovery (Facts Before Questions)
1. **Inspect Workspace Context:** Before asking any questions, read existing specifications, project briefs, schemas, configuration files, and code.
2. **Identify Existing Document Conventions:** Detect where project documentation lives:
   - Does a `docs/adr/` or `architecture/` directory exist?
   - Is there a `GLOSSARY.md` or domain dictionary?
   - Is there a central specification or PRD document?
   - If no documentation convention exists, default to clean project-level markdown files (`docs/adr/` for decisions, or a unified `SPECIFICATION.md` / `PRD.md`).
3. **Map the Unknowns:** Separate verified facts from assumptions, ambiguities, and unsettled decisions.

### Phase 2: Orchestrated Grilling
1. **Establish the Design Tree:** Structure open questions using the `grilling` methodology.
2. **Run Frontier Rounds:** Group questions into logical dependency rounds.
3. **Challenge Inconsistent Terminology:** Actively police domain language. If the user uses conflicting terms for the same concept (e.g., "User" vs. "Account", "Workload" vs. "Duration"), clarify and standardize immediately.
4. **Enforce Simplicity:** Pair each question with a recommended answer following the `ponytail` principle (smallest viable change, no premature complexity).

### Phase 3: Decision Capture & Consensus
1. As each round concludes, formalize accepted recommendations into explicit, immutable decisions.
2. Distinguish clearly between:
   - **Confirmed Decisions:** Explicitly approved by user.
   - **Proposals/Recommendations:** Recommended by agent, awaiting confirmation.
   - **Deferred Items:** Deliberately parked for future iterations.

### Phase 4: Progressive Documentation
Do not wait until the entire project is designed to begin writing documentation. Document lazily as decisions crystallize:

1. **Domain Glossary (`GLOSSARY.md`):** Record newly defined terms, acronyms, and invariants as soon as they are disambiguated.
2. **Architectural Decision Records (ADR):** For critical architectural forks (e.g., technology choice, state management, storage strategy, security boundaries), draft an ADR capturing:
   - **Context:** Problem statement and forces at play.
   - **Decision:** The chosen path.
   - **Consequences:** Positive gains, trade-offs, and what was intentionally skipped.
3. **Technical Specification / PRD:** Consolidate the entire design tree into an authoritative baseline document before writing any production implementation code.

## Guardrails
- **No Invisible State:** Every settled decision must be captured in persistent markdown, never left solely in ephemeral chat messages.
- **Maintain Document Integrity:** Never silently overwrite existing project conventions or unrelated sections of existing documentation.
- **Stay Agnostic:** Adapt to whatever documentation format the host project uses; never force a rigid folder layout if the project already has an established documentation pattern.
