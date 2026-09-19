# ADOS Workflow-Pack Proposal

**Related issue:** #21  
**Goal:** Define a small, reusable set of agentic workflows that use `vercel-templates-discovery` to help agents and developers pick the right Vercel Template.

## What an ADOS workflow-pack is

An ADOS workflow-pack is a collection of named, documented playbooks that an agent can run against a project. Each workflow states:

- **Trigger** — when to run it
- **Inputs** — what the agent needs (a PRD, a codebase path, a stack list, etc.)
- **Steps** — how to use `vercel-templates` to get an answer
- **Outputs** — what the agent returns to the user
- **Quality gate** — how to know the workflow succeeded

## Proposed workflows

### 1. `find-template-foundation`

**Trigger:** Kicking off a new project from a description, PRD, or idea.  
**Inputs:**

- Free-text project description
- Desired stack / framework constraints (optional)
- Must-have features (optional)

**Steps:**

1. Parse the description for framework, feature, and use-case keywords.
2. Run `vercel-templates search` for the top keywords.
3. If Ollama is available, run `vercel-templates search --semantic` on the full description for intent-based matches.
4. Rank candidates by: framework match, feature overlap, GitHub stars (via metadata), and README richness.
5. Pick the top 1–3 templates.
6. For each, extract `install_command`, `github_url`, and a one-paragraph rationale.

**Outputs:**

- Recommended starter template(s) with install commands
- A short "why this fits" note per candidate
- Suggested next step: clone / install / adapt

**Quality gate:** At least one candidate has a non-empty README and a working install command.

### 2. `find-reference-material`

**Trigger:** Improving an existing codebase that lacks a modern UI/UX pattern.  
**Inputs:**

- Path to the local codebase
- The feature or feeling the user wants to add (e.g., "AI chat UI", "dashboard layout", "auth flow")

**Steps:**

1. Scan the codebase for current frameworks and key libraries.
2. Map the target feeling to Vercel Template categories and keywords.
3. Run `vercel-templates recommend` with the inferred stack.
4. Return 2–5 templates that demonstrate the desired pattern.

**Outputs:**

- List of reference templates with links and descriptions
- Key files/components in each template that are worth studying

**Quality gate:** Every reference template uses a framework or stack the target codebase can realistically adopt.

## Suggested repo layout

```text
.ados/workflows/
├── find-template-foundation/
│   ├── README.md      # this playbook
│   └── workflow.py    # optional automation wrapper
└── find-reference-material/
    ├── README.md
    └── workflow.py
```

## First milestone

Implement `find-template-foundation` end-to-end:

- [ ] Add the playbook under `.ados/workflows/find-template-foundation/README.md`
- [ ] Add a CLI helper or Python script that takes a description and returns ranked candidates
- [ ] Add a pytest smoke test with a mocked catalog
- [ ] Wire it into the Hermes skill as a new usage example

## Open questions

- Should the workflow-pack live in this repo or in the separate `webton-ados` repository?
- Should workflows be pure documentation, or should they ship as runnable code?
- Do we want to integrate with the MCP server so any agent can call the workflows as tools?
