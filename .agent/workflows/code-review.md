---
description: "Technical code review for quality, correctness, and maintainability"
id: "ados-code-review"
name: Code Review
version: 1.0.0
category: development
author: ADOS Team
status: active
license: MIT
---

# Code Review

## Goal
Review recent changes for correctness, clarity, and alignment with repo conventions.

## Read first
- `.agent/rules/00-core.md`
- Any repo lint/style/testing conventions (README, docs)

## Gather diffs (propose commands)
- `git status`
- `git diff HEAD`
- `git diff --stat`

## Review checklist

### Hybrid-Light Review Gate (#176)
- Spec before coding: issue/spec/AC are explicit enough to verify done vs not done.
- AC/DoD traceability: every material change maps to stated acceptance criteria or a documented plan task.
- TDD on risky logic: risky behavior changes include RED-GREEN evidence, or a documented reason TDD does not apply.
- Review before done: verdict is recorded before marking work done/merge-ready.

### Correctness & Safety
- Edge cases handled, inputs validated
- Error handling around IO/network/db
- No secrets logged or committed

### Architecture & Maintainability
- Follows existing patterns and folder conventions
- Small cohesive functions/modules
- Avoids unnecessary abstraction

### Performance
- Avoids obvious N+1 / expensive loops / repeated API calls
- Reasonable caching/batching when relevant

### UX / API contracts
- No breaking changes without migration path
- Clear user-facing behavior

### Tests
- Behavior changes covered by appropriate tests
- Bugfixes have regression tests when feasible

### Deep-review extension (Track C / #51)
For high-impact PRs, add these checks:
- AC/DoD traceability (issue -> changes -> validation evidence)
- Hybrid-Light evidence (spec gate satisfied, risk/TDD classification, review gate verdict)
- Rollback readiness for operational/infrastructure changes
- Cross-file contract consistency (no contradictory rules/docs)
- Failure taxonomy coverage (if runbook/ops changes involved)

## Output
Provide:
1) Summary
2) Findings grouped by severity:
   - Blocker
   - High
   - Medium
   - Low / nit
3) Suggested fixes (specific)
4) **Review Gate Result** — per `.agent/rules/01-gate-result.md` (see below)

## Review Gate Result

After the review verdict is reached, emit a `## Gate Result` block per `.agent/rules/01-gate-result.md`:

```markdown
## Gate Result

**Gate:** Review
**Status:** PASS | FAIL | BLOCKED
**Evidence:**
- Verdict: APPROVE | REQUEST_CHANGES | COMMENT
- Findings: N Blocker / M High / O Medium / P Low
- Report path: `.agent/reports/code-reviews/...`
**Failure reason:** <if FAIL or BLOCKED>
**Next:** proceed | revise | re-plan | escalate
```

- **PASS** — verdict is APPROVE or only Low/Nit findings remain.
- **FAIL** — verdict is REQUEST_CHANGES with Blocker/High/Medium findings.
- **BLOCKED** — cannot complete review (missing diff, missing context, tool failure).
- **Next=proceed** — gate passed, work is merge-ready (pending human approval if required).
- **Next=revise** — invoke `.agent/workflows/revise.md` with the review report; max 2 cycles.
- **Next=re-plan** — revision budget exhausted or repeated identical failure fingerprint; route to `rca` or `plan-feature` update.

Optionally save a report to:
- `.agent/reports/code-reviews/<date>-<topic>.md`

## Review Agent Mode (Subagent-based)

Use when line-level review quality is required without CodeRabbit.

### Decision Matrix
| Scenario | Approach |
|---|---|
| Complex feature PR (>200 lines changed) | Review Agent (spawn subagent) |
| Simple fix / docs / chore (<50 lines) | Self-review (checklist above) |
| Hotfix under time pressure | Skip → document risk in PR body |
| Already reviewed by another human | Self-review to confirm |

### How to spawn the Review Agent

Spawn a Codex-based subagent with the following inputs and prompt.

**Inputs to provide:**
1. Full PR diff (`gh pr diff <number>`)
2. Repo rules (`.agent/rules/00-core.md`)
3. Relevant source files touched by the PR (from `gh pr diff --stat`)
4. Optional: previous review findings (for re-review passes)

**Review Agent prompt template:**
~~~
You are a senior software engineer performing a thorough code review.

## Context
- Repo rules: [contents of .agent/rules/00-core.md]
- PR diff: [full diff output]
- Changed files context: [relevant source file excerpts]

## Task
Review the diff for:
1. Correctness & Safety (edge cases, error handling, no secrets committed)
2. Architecture & Maintainability (patterns, cohesion, unnecessary abstractions)
3. Performance (N+1 queries, expensive loops, missing batching)
4. API/UX contracts (breaking changes, behavior clarity)
5. Tests (behavior changes covered, regression tests for bugfixes)

## Output format (strict — do not deviate)

### Summary
<2-3 sentence overall assessment>

### Findings

#### 🔴 Blocker
- [file:line] Description — Suggested fix

#### 🟠 High
- [file:line] Description — Suggested fix

#### 🟡 Medium
- [file:line] Description — Suggested fix

#### 🟢 Low / Nit
- [file:line] Description — Suggested fix

### Verdict
APPROVE | REQUEST_CHANGES | COMMENT
~~~

### Output
- Save findings to `.agent/reports/code-reviews/<YYYY-MM-DD>-<topic>.md`
- Pass report path to `code-review-fix.md` for remediation of non-low findings
