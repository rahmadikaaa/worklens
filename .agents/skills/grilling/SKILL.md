---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

# Grilling

Interview the user relentlessly until you reach a shared, unambiguous understanding. Treat any engineering task—architecture, data pipelines, AI workflows, API design, or system refactoring—as a **design tree**: every foundational decision branches into subsequent decisions hanging off it.

## The Core Discipline

1. **Map the Design Tree:** Identify foundational decisions first (data contracts, architecture boundaries, security, scope) before detailing leaf nodes (syntax, helper utilities).
2. **Work in Rounds:** The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing answers to unasked questions.
3. **Ask the Whole Frontier:** Present all open questions belonging to the current frontier in one round. Number each question and provide your recommended answer.
4. **Never Ask for Facts You Can Discover:** Finding facts is your job, never the user's. Before formulating questions, inspect the workspace, analyze existing code, read configuration, or invoke research subagents if available. Only ask the user for *decisions*, *priorities*, and *domain intentions*.

## Probing Dimensions

When mapping the design tree of any engineering problem, systematically probe across these dimensions:

- **Scope & Boundaries:** What is explicitly in-scope vs. out-of-scope for this phase? What is YAGNI?
- **Data & Interfaces:** What are the input contracts, schemas, primary identifiers, and invariants? How are nulls, empty values, and invalid formats handled?
- **Behavior & Failure Modes:** How does the system behave when a step fails? Fail-fast vs. graceful degradation? Idempotency and retry semantics?
- **Operational & Non-Functional:** Privacy constraints, credential isolation, performance/throughput, cost/token efficiency, offline vs. online execution modes.
- **Change & Evolution:** How does the system handle schema changes, versioning, re-runs, and backwards compatibility?

## Format for Each Round

Format each round consistently:

```markdown
❓ **Q1** - **<Question Title>**: <Context explaining trade-offs, consequences, and choices.>

➡️ <Your recommended answer, explaining why it is the simplest or most robust option.>

---

❓ **Q2** - **<Question Title>**: <Context explaining trade-offs, consequences, and choices.>

➡️ <Your recommended answer, explaining why it is the simplest or most robust option.>
```

- **Binary Alignment:** Word each question and recommended answer so that a simple "yes" from the user confirms the recommended approach.
- **No Guessing Ahead:** If Question B depends on the choice made in Question A, hold Question B for the *next* round after Question A is settled.

## Session Lifecycle

1. **Active Interrogation:** Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock downstream questions.
2. **Record Settled Decisions:** State confirmed decisions clearly at the beginning of each round.
3. **Session Completion:** The session is complete when the frontier is empty: every essential branch has been explored, all edge cases addressed, and no critical assumptions left silent. Do not begin implementation until the user explicitly confirms the finalized baseline.
