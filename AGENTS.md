# AGENTS.md — Vercel Templates Discovery

This project follows ADOS (Agent Delivery OS) from `~/.openclaw/workspace/projects/webton/webton-ados`.

## Read first (canonical order)
1. `.agent/rules/00-core.md` — repo core rules and Definition of Done
2. `.agent/rules/01-gate-result.md` — gate result contract
3. `.agent/workflows/plan-feature.md` — how to plan before coding
4. `.agent/workflows/code-review.md` — review gate
5. `docs/PROJECT_PLAN.md` — project roadmap and milestones
6. `docs/PROJECT_STATUS.md` — current owner status and decisions

## Quick conventions
- Issue-first: every change references a GitHub issue
- Branch: `feature/<issue>-<slug>` / `fix/<issue>-<slug>` / `chore/<issue>-<slug>`
- Commit: `<type>: <summary> (#<issue>)`
- PR title: `[#<issue>] Short summary`
- Gate Result required after Plan, Review, Validate, Close
- Handoff schema required for session artifacts
