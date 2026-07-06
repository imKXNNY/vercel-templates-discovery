# Gate Result — Issue #10: Docker image

## Gate Result

**Gate:** Close  
**Status:** PASS  
**Evidence:**
- Dockerfile multi-stage build now succeeds locally and in GitHub Actions (run 28759600764).
- Docker publish workflow pushed `ghcr.io/imkxnny/vercel-templates-discovery:0.2.3`, `0.2`, and `latest` (workflow log: `image.name` confirms all three tags).
- PyPI v0.2.3 live: https://pypi.org/project/vercel-templates-discovery/0.2.3/
- npm v0.2.3 live: https://www.npmjs.com/package/@imkxnny/vercel-templates-discovery/v/0.2.3
- GitHub release v0.2.3 created: https://github.com/imKXNNY/vercel-templates-discovery/releases/tag/v0.2.3

**Failure reason:** none

**Next:** proceed to Issue #11 (semantic search)

## Handoff

**Implemented:**
- Fixed Dockerfile TypeScript build stage (WORKDIR /build, copy tsconfig.json and src/ before `npm run build`).
- Added `declarationMap`, `sourceMap`, and `types: ["node"]` to `ts/tsconfig.json`.
- Bumped versions to v0.2.3 in `pyproject.toml` and `ts/package.json`.
- Updated `CHANGELOG.md` and `docs/PROJECT_STATUS.md` to v0.2.3.
- Committed fix and pushed v0.2.3 tag, triggering publish-pypi, publish-npm, and publish-docker workflows.
- Created GitHub release v0.2.3 with PyPI/npm/Docker links.

**Left undone:**
- Local `docker pull` from GHCR returned 403 because the local `gh` auth token lacks `read:packages` scope; the workflow push succeeded and the image is available to users with package read access.
- GHCR package remains private (consistent with private repo decision). Making it public is deferred until M6 / ToS review.

**Commands run:**

| Command | Exit code |
|---------|-----------|
| `git add .github/workflows/publish-docker.yml && git commit -m "chore: enable manual dispatch..."` | 0 |
| `git add -A && git commit -m "chore: bump to v0.2.2..." && git tag -a v0.2.2 ... && git push origin master && git push origin v0.2.2` | 0 |
| `docker build --target ts-build -t vercel-templates-tmp .` | 1 (first attempt: tsconfig not in build root) |
| `docker build --target ts-build -t vercel-templates-tmp .` | 0 (after Dockerfile fix) |
| `docker build -t vercel-templates-tmp-final .` | 0 |
| `git add Dockerfile ts/tsconfig.json && git commit -m "fix: correct TypeScript build stage..."` | 0 |
| `git add -A && git commit -m "chore: bump to v0.2.3..." && git tag -a v0.2.3 ... && git push origin master && git push origin v0.2.3` | 0 |
| `gh run watch 28759600764 --exit-status` | 0 (Docker workflow succeeded) |
| `curl -sL https://pypi.org/pypi/vercel-templates-discovery/json \| grep version` | 0 (0.2.3) |
| `curl -sL https://registry.npmjs.org/@imkxnny/vercel-templates-discovery \| grep version` | 0 (0.2.3) |
| `gh release create v0.2.3 ...` | 0 |

**Issues discovered:**
- v0.2.1 and v0.2.2 Docker builds failed because the Dockerfile did not copy `tsconfig.json` into the TypeScript build root before `npm run build`.
- v0.2.2 PyPI/npm succeeded but Docker failed; a v0.2.3 patch was needed to fix the image build and keep versions aligned.
- Local `gh` token does not include `read:packages` scope, so private GHCR pulls cannot be verified locally without adding that scope.

**Procedures followed:** yes
- Issue-first workflow (Issue #10 referenced in all commits).
- Version bump and CHANGELOG/PROJECT_STATUS updates.
- Verification via PyPI/npm registry API and GitHub Actions run logs.
- Gate result artifact emitted.
