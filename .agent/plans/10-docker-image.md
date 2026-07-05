# Plan: Issue #10 — Add Docker image

## Goal
Provide an official container image so agents and CI can run the catalog discovery CLI without installing Python/Node locally.

## Approach
- Add a `Dockerfile` at the repo root.
- Use a Python 3.12 base image.
- Install the local package in editable or production mode (`pip install .` or `pip install -e .[server]`).
- Also include the TypeScript implementation pre-built in `/app/ts`.
- Provide both `vercel-templates` and `vercel-templates-mcp` entry points.
- Add a `.dockerignore` to keep the image small.
- Add `.github/workflows/publish-docker.yml` to build and push to GitHub Container Registry (`ghcr.io`) on tag pushes.
- Test locally: `docker build`, `docker run vercel-templates --help`, `docker run vercel-templates stats`.

## Acceptance criteria
- [ ] `Dockerfile` exists and builds successfully.
- [ ] `.dockerignore` excludes unnecessary files.
- [ ] Image contains both Python and TypeScript CLI implementations.
- [ ] `docker run --rm <image> vercel-templates --help` works.
- [ ] GitHub Actions workflow publishes to `ghcr.io` on tag push.
- [ ] README and CHANGELOG updated.
- [ ] ADOS review gate passes.

## Files to modify
- `Dockerfile` (new)
- `.dockerignore` (new)
- `.github/workflows/publish-docker.yml` (new)
- `README.md` (update)
- `CHANGELOG.md` (update)
- `docs/PROJECT_STATUS.md` (update)
- `.agent/plans/10-docker-image.md` (new)

## Dependencies
- M4 PyPI/npm publish complete (Issue #8, #9)
- Working Python package install
- Working TypeScript build
