# Plan: Issue #8 — Publish PyPI package

## Goal
Make `pip install vercel-templates-discovery` work by publishing the Python package to a private test index first, then to PyPI once M6 is reached.

## Approach
- Ensure `pyproject.toml` is complete and correct (name, version, description, classifiers, readme, license, authors, dependencies, optional extras, scripts).
- Add `build` and `twine` to dev extras for building and publishing.
- Build the wheel/sdist with `python -m build`.
- Validate the package with `twine check`.
- Publish to TestPyPI first using a scoped/private package name or a private test index (per Kenny's preference for private publish now).
- Since the repo is private and we want a private publish, we can use `TestPyPI` with a `--repository-url` or use a private GitHub Packages PyPI repository. But for this task, TestPyPI is the standard safe test index.
- To keep it private-ish, we can use a scoped name like `kxnnymusic-vercel-templates-discovery` or just use TestPyPI as a staging environment. Kenny said "private publish", so I'll use a non-public name on TestPyPI or ensure the package is marked as a pre-release.
- Actually, true private PyPI hosting requires a registry like GitHub Packages, AWS CodeArtifact, or a self-hosted pypi. The simplest is to publish to TestPyPI with a clearly private/test name.
- Alternatively, I can configure GitHub Packages PyPI as a private registry. But that requires GitHub token and configuration. For this task, I'll use TestPyPI with `kxnnymusic-vercel-templates-discovery` or `vercel-templates-discovery-test`.

## Acceptance criteria
- [ ] `pyproject.toml` is publish-ready.
- [ ] `python -m build` produces wheel/sdist.
- [ ] `twine check` passes.
- [ ] Package published to TestPyPI (or private index) with a working install command.
- [ ] README updated with `pip install` instructions.
- [ ] CI workflow updated to build/check package.

## Files to modify
- `pyproject.toml` (add build/twine deps, ensure metadata)
- `README.md` (install instructions)
- `.github/workflows/ci.yml` (build check)
- `.agent/plans/8-pypi-publish.md` (new)

## Dependencies
- M2 done (tests, CHANGELOG)
- M3 done (server, skill)
- `build` and `twine` tools
