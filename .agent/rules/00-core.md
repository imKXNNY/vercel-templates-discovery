# .agent/rules/00-core.md — Repo Core Rules (Source of Truth)

## 0) Source of Truth & Paths
- Rules: .agent/rules/*
- Workflows/Commands: .agent/workflows/*
- Plans: .agent/plans/
- Reports: .agent/reports/
- Specs: specs/
- HTML Templates: .agent/templates/html/
- HTML Artifact Rules: .agent/rules/09-html-artifacts.md
If CLAUDE.md or GEMINI.md exist, they must point here (this file stays canonical).

## 1) Issue-First Process
- Each change must reference an Issue ID (e.g. #123).
- If the task exists only in chat: create an Issue Draft first (Title, Body, AC, Labels).
- "Discovered during work" items become NEW issues (or comment suggestions), not local log dumps.
- Legacy TASK.md / TODO.md:
  - Do not append.
  - If you need info from them: summarize into Issues and stop using them as a live tracker.

## 2) Definition of Done (DoD)
A task is "done" when:
- Acceptance Criteria of the Issue are met.
- Relevant tests exist/updated (unit/integration/E2E depending on change).
- Verification steps are provided (commands + expected outcome).
- Review gate completed before done/merge-ready status (self-review for small changes; fresh review agent/subagent for risky or larger changes).
- README/docs updated if behavior/setup changed.
- No secrets added; configs follow repo conventions.

## 2a) Track B Hybrid-Light Defaults (#176)
ADOS adopts Hybrid-Light as the default delivery posture. See `docs/ops/TRACK_B_HYBRID_SOP.md`.
- **Spec before coding:** no non-trivial implementation starts until the issue/spec/AC are understood and mapped to a plan or issue draft.
- **TDD on risky logic:** business rules, permissions, parsers/validators, workflow dispatch, migrations, and bug fixes need RED-GREEN-REFACTOR or a documented test-first equivalent. Docs-only/prompt-only changes may use rendering/diff smoke proof instead.
- **Review gate before done:** work is not done until the diff is reviewed against AC, validation evidence, and repo conventions.

## 3) Branch / Commit / PR Conventions
- Branch naming:
  - feature/<issue>-short-slug
  - fix/<issue>-short-slug
  - chore/<issue>-short-slug (if applicable)
- Commit messages:
  - Prefer: "<type>: <summary> (#<issue>)"
  - For bugfixes that should auto-close on merge: ensure PR body contains "Fixes #<issue>".
- PR requirements:
  - PR title references Issue: "[#123] Short summary"
  - PR body includes:
    - What/Why
    - How tested
    - "Fixes #123" (when closing)

## 4) Testing Policy (Repo-aware)
- Prefer the repo's existing test stack (do not invent libraries).
- UI/end-to-end flows: Playwright if already present.
- Pure logic: unit tests are acceptable and often faster.
- Bugfixes: add a regression test when feasible.
- Store screenshots/artifacts under .agent/reports/ or the repo's established test artifact path.

## 5) Style & Tooling
- Follow the repo's formatters/linters (ESLint/Prettier, Black/Ruff, etc.).
- Confirm file paths/modules exist before referencing them.
- Do not delete/overwrite code unless:
  - explicitly requested, OR
  - required by the Issue, OR
  - part of a minimal refactor necessary to implement the change safely.

## 6) Execution Rules (Terminal)
- Never run commands without explicit approval.
- When proposing commands, include:
  - the exact command
  - why it's needed
  - what success looks like

## 7) BUILDING Loop Rule
After each BUILDING loop iteration, update AGENTS.md if operational learnings emerged (new constraints, patterns, gotchas discovered during implementation).

## 8) Durable Abstraction & Workflow Design
- Operate at the highest durable abstraction layer that still preserves control and observability.
- Keep execution grounded in file-tree/task-graph artifacts (instructions, tools, data attached to concrete task folders/files).
- Avoid adding new orchestration layers unless they create measurable, repeatable benefit.
- Treat new model/platform capabilities as pluggable tools or subtasks; do not reset architecture by default on every upstream change.
- Prefer reusable composition patterns over bespoke framework complexity.

## 9) Gate Result (Required for phase-boundary workflows)

Every workflow that crosses a phase boundary in the Core Delivery Harness MUST emit a conforming `## Gate Result` block. See `.agent/rules/01-gate-result.md` for the canonical template, field rules, and parsing contract.

Quick reference:
```markdown
## Gate Result
**Gate:** Plan | Verify | Review | Close
**Status:** PASS | FAIL | BLOCKED
**Evidence:** <command, result, artifact path>
**Failure reason:** <if FAIL or BLOCKED>
**Next:** proceed | revise | re-plan | escalate
```

Affected workflows: `plan-feature`, `validate` (all variants), `code-review`, `close`.

## 10) Structured Handoff Schema (Required for `handoff` doc-key)

Every agent run that produces a `handoff` doc-key (Paperclip issue document or session artifact) MUST use this schema. Free-form markdown is not accepted — orchestrators and recovery runs parse these fields.

```markdown
## Handoff

**Implemented:**
- <bullet per completed item>

**Left undone:**
- <bullet per incomplete item, with why>

**Commands run:**
| Command | Exit code |
|---------|-----------|
| npm run build | 0 |
| npm test | 0 |

**Issues discovered:**
- <any surprises, hidden deps, tech debt>

**Procedures followed:** yes / partial / no
<explain if partial or no>
```

Rules:
- All five sections are required; use "none" or "n/a" for empty sections rather than omitting them.
- "Implemented" and "Left undone" must be evidence-backed bullets, not summaries.
- "Commands run" must list every significant command executed (build, test, lint, deploy). Use exit code 0 for success, non-zero for failure.
- "Issues discovered" captures surprises that are NOT already tracked in a separate issue; create issues for anything actionable.
- "Procedures followed" evaluates adherence to this file's Definition of Done (§2) and any workflow-specific SOP.

## 10) Research-Wave Soft Guidance (Issues #163 #164 #165)
- Tool discovery at scale: prefer progressive capability disclosure over eager full tool loading.
- Tool selection should be explainable in artifacts when non-obvious (why this tool, why now).
- Long-running workflows should emit checkpoint/evidence artifacts so interrupted work can resume safely.
- Multi-agent handoffs should define explicit scope and pass only minimal required context.
- Keep advanced routing heuristics, orchestrator-state formalization, and full handoff-envelope schemas provisional until additional pilot/incident evidence is captured.
