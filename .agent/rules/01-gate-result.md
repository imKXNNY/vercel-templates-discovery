# .agent/rules/01-gate-result.md — Gate Result Template (Source of Truth)

> Companion to `00-core.md`. All workflows that cross a phase boundary MUST emit a conforming `## Gate Result` block.

## Purpose

Make ADOS gates visible as structured, parseable output. Every phase boundary in the Core Delivery Harness produces a Gate Result that answers: **Did this gate pass? What is the evidence? What happens next?**

## When to emit

| Workflow | Gate | Emit after |
|---|---|---|
| `plan-feature.md` | Plan Gate | Validation Contract is written |
| `validate.md`, `validate-simple.md`, `validate-adversarial.md` | Verify Gate | Validation commands finish |
| `code-review.md` | Review Gate | Review verdict is reached |
| `close.md` (WS3) | Close Gate | Final evidence package assembled |

## Template (copy verbatim)

```markdown
## Gate Result

**Gate:** Plan | Verify | Review | Close
**Status:** PASS | FAIL | BLOCKED
**Evidence:** <command, result, artifact path>
**Failure reason:** <if FAIL or BLOCKED>
**Next:** proceed | revise | re-plan | escalate
```

### Field rules

- **Gate** — One of the four canonical gate names. Use the closest match if a workflow spans multiple gates (emit one per gate crossed).
- **Status**
  - `PASS` — all assertions satisfied, evidence recorded.
  - `FAIL` — at least one assertion failed; revision loop required.
  - `BLOCKED` — cannot proceed due to external dependency, missing input, or human approval needed.
- **Evidence** — Concrete, falsifiable proof. Prefer: command + exit code + artifact path. Example: `npm run build` exited 0; artifact `.agent/reports/validation/TEC-123.md`.
- **Failure reason** — Required when Status is FAIL or BLOCKED. One sentence root cause. Links to failure fingerprint or review report when available.
- **Next** — Recommended action:
  - `proceed` — gate passed, continue to next phase.
  - `revise` — gate failed, enter revision loop (max 2 cycles per `revise.md`).
  - `re-plan` — gate failed and revision budget exhausted; return to `plan-feature` or `rca`.
  - `escalate` — blocked or catastrophic failure; human handoff required.

## Integration with other rules

- **Hybrid-Light spec gate (#176)** — Plan Gate references the spec gate but does NOT replace it. The spec gate lives in `plan-feature.md`; the Gate Result makes its outcome visible.
- **Validation Contract** — Verify Gate references Validation Contract assertions but does NOT replace them. The contract lives in the plan document; the Gate Result records the verdict.
- **Revision Budget** — When Status=FAIL and Next=revise, the revision loop is governed by `revise.md` (max 2 cycles, failure fingerprinting, early abort to `rca`).

## Example

```markdown
## Gate Result

**Gate:** Verify
**Status:** PASS
**Evidence:**
- `npm run build` → exit 0
- `npm test` → 42 passed, 0 failed
- Type-check: `tsc --noEmit` → 0 errors
**Failure reason:** n/a
**Next:** proceed
```

## Parsing contract

Orchestrators and recovery runs may parse Gate Result blocks. Rules for machine readability:

1. The `## Gate Result` heading must appear exactly once per gate crossing.
2. The five bold fields (`**Gate:**`, `**Status:**`, `**Evidence:**`, `**Failure reason:**`, `**Next:**`) must all be present, in any order under the heading.
3. Use `n/a` or `none` for empty fields rather than omitting them.
4. Keep Evidence to ≤5 bullet lines when possible; link to full artifacts for detail.

## References

- `00-core.md` — Definition of Done, Hybrid-Light defaults
- `plan-feature.md` — Validation Contract format
- `revise.md` — Revision budget policy (2-cycle cap, failure fingerprinting)
- `validate-adversarial.md` — Adversarial validation proof document format
