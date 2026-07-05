# Plan: Issue #9 — Publish npm package

## Goal
Make `npm install -g @kxnnymusic/vercel-templates-discovery` work by publishing the TypeScript package as a scoped, restricted npm package.

## Approach
- The package is already scoped `@kxnnymusic/vercel-templates-discovery`.
- Ensure `package.json` has:
  - `files` whitelist so only `dist/` and essential files are published.
  - `publishConfig.access` set to `restricted` (private scoped package).
  - `types` field pointing to `dist/index.d.ts`.
  - A `prepublishOnly` script that runs `npm run build`.
- Add a `.npmignore` or rely on `files`.
- Run `npm run build` and `npm pack` to verify.
- Publish to npm with `npm publish --access restricted`.
- Since this is a private publish, use restricted access.

## Acceptance criteria
- [ ] `package.json` publish-ready with `files`, `publishConfig`, `types`.
- [ ] `npm run build` succeeds.
- [ ] `npm pack` produces a clean tarball.
- [ ] Package published to npm as `@kxnnymusic/vercel-templates-discovery` with restricted access.
- [ ] README updated with `npm install -g` instructions.
- [ ] CI workflow checks TypeScript build and pack.

## Files to modify
- `ts/package.json` (add files, publishConfig, types, prepublishOnly)
- `ts/.npmignore` (optional)
- `README.md` (npm install instructions)
- `.github/workflows/ci.yml` (npm pack check)
- `.agent/plans/9-npm-publish.md` (new)

## Dependencies
- M2 done (TypeScript port, tests)
- npm account and auth token (will use existing npm config if available, otherwise prompt)
