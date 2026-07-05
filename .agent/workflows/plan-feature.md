---
description: Create a comprehensive implementation plan (no coding)
argument-hint:"issue-id or feature-description"
id: "ados-plan-feature"
name: Plan Feature
version: 1.0.0
category: development
author: ADOS Team
status: active
license: MIT
---

# Plan Feature: $ARGUMENTS

## Mission
Turn the request into a **context-rich, executable plan** that another agent can implement in one pass.

**Hard rule:** Do NOT write implementation code in this phase.

## Inputs
- Preferred: GitHub Issue ID (e.g. `123`)
- Fallback: Plain feature description

If an Issue ID is provided and GitHub CLI is available, propose:
- `gh issue view <id>`

## Planning steps

### 1) Understand the goal
- Restate the goal in 1–2 sentences.
- Extract Acceptance Criteria (AC). If missing, propose AC.
- **Hybrid-Light spec gate (#176):** do not proceed to implementation planning until the issue/spec/AC are explicit enough that another agent can verify done vs not done.

### 2) Inspect the repo for conventions
- Read `.agent/rules/00-core.md` (and any additional `.agent/rules/*`)
- Read relevant docs/configs for the area being changed.

### 3) Identify touch points
- List the files/modules likely to be modified
- List new files to be added (if any)
- Note existing patterns to follow (naming, folder structure, APIs)

### 4) Define the execution contract
Your plan MUST include:
- **Issue:** `#<id>` (or "Issue draft needed")
- **Branch:** `feature/<id>-<slug>` or `fix/<id>-<slug>` (choose appropriately)
- **Plan file path:** `.agent/plans/<id>-<slug>.md`
- **Risk/TDD classification:** mark whether the change touches risky logic and, if yes, name the RED/GREEN proof to add first.
- **Verification commands:** repo-appropriate (discover from package scripts / tooling)

### 5) Write the Validation Contract (REQUIRED — before implementation steps)

Every plan MUST include a `## Validation Contract` section written **before** the implementation steps. This is what validators receive; they do not receive implementation history.

```markdown
## Validation Contract
### Assertions (written before implementation)
- [ ] <behavior X is observable at endpoint Y>
- [ ] <edge case Z returns error code W>
- [ ] Type-check passes with zero errors
- [ ] Lint passes with zero warnings
### Performance bounds
- <e.g. p95 response < 200 ms under N concurrent users>
### Interface contracts
- <e.g. POST /api/foo accepts { bar: string } and returns { id: string }>
```

**DoD requirement:** A plan without a Validation Contract is incomplete and must not be handed to an executor.

### 6) Emit Plan Gate Result

After the Validation Contract is written and the plan is stable, emit a `## Gate Result` block per `.agent/rules/01-gate-result.md`:

```markdown
## Gate Result

**Gate:** Plan
**Status:** PASS | FAIL | BLOCKED
**Evidence:** Plan file path, AC present, Validation Contract present, risk/TDD classification recorded
**Failure reason:** <if FAIL or BLOCKED>
**Next:** proceed | revise | re-plan | escalate
```

- **PASS** — plan is complete with Validation Contract, branch name, AC, and risk classification.
- **FAIL** — plan is incomplete (missing AC, missing Validation Contract, ambiguous scope).
- **BLOCKED** — external dependency or human decision needed before planning can complete.
- **Next=revise** → return to step 3–5; do not hand to executor until PASS.

### 7) Produce an implementation plan
Write a plan that includes:
- Step-by-step tasks (small slices)
- Data model changes (if any)
- API changes (if any)
- UI changes (if any)
- Tests to add/update per slice
- Edge cases and failure handling
- Rollback considerations (if relevant)

## Output
1) Print:
   - Issue (or Issue Draft)
   - Branch name
   - Plan file path
2) Save the plan to: `.agent/plans/<id>-<slug>.md`

## PLANNING-Loop Mode (Ralph-style)

Use when specs exist under `specs/*.md` and a plan needs to be derived or refined iteratively.

### When to use
- Specs files exist (`specs/*.md`) but `IMPLEMENTATION_PLAN.md` is missing or stale
- Plan needs multiple passes to cover all spec gaps

### Loop lifecycle
1. **Read specs** — load all `specs/*.md` fresh (no prior context assumed)
2. **Read existing code** — scan relevant `/src` or repo files
3. **Gap analysis** — compare what specs require vs what code provides
4. **Update plan** — write/update `IMPLEMENTATION_PLAN.md` with prioritized task list
5. **No implementation** — this mode produces plans only
6. **Loop condition** — continue until plan covers all gaps; typically 1–2 iterations

### Output
- Stable `IMPLEMENTATION_PLAN.md` at repo root (or `.agent/plans/<id>-<slug>.md`)
- Each task entry includes: description, acceptance criteria, files to touch, verification command

### Transition
When plan is stable → switch to BUILDING-loop mode (`execute.md` or `ralph-loop.md`)
