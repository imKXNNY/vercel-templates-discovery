# Vercel ToS / Compliance Review

**Scope:** Whether the `vercel-templates-discovery` project can publicly index and redistribute metadata from `https://vercel.com/templates`.

**Review date:** 2026-07-07
**Documents reviewed:**
- Vercel Terms of Service (saved locally as `Terms of Service.html`, source `https://vercel.com/legal/terms`)
- Vercel robots.txt (`https://vercel.com/robots.txt`)

## robots.txt

```text
User-Agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=no

Allow: /api/og/*
Allow: /api/docs-og*
Allow: /api/product-og*
Allow: /api/dynamic-og*
Allow: /api/model-og*
Allow: /api/www/avatar/*

Disallow:
Disallow: /api/
Disallow: /oauth
Disallow: /confirm
Disallow: /notifications
Disallow: /old-browser.html
Disallow: /preauthorize
Disallow: /signup?*
Disallow: /invites/

Sitemap: https://vercel.com/sitemap.xml
```

`/templates` is **not** listed in `Disallow`. The empty `Disallow:` directive (without a path) does not block anything; the explicit disallowed paths do not include the templates gallery.

## Relevant Terms of Service clauses

### Section 2 — Temporary Use License
Grants a personal, non-exclusive, non-transferable, limited license to use the Services for internal business or personal purposes. This is primarily about account holders using Vercel's platform, not about browsing public marketing pages.

### Section 3 — Your Content
Covers content users upload/post to Vercel. Does not apply to publicly visible template listings we read without an account.

### Section 7 — Acceptable Use
Requires compliance with the [Acceptable Use Policy](https://vercel.com/legal/acceptable-use-policy). Notably, it does not prohibit automated access to public pages per se.

### Section 8 — Etiquette
Vercel may monitor use and prohibit activity it believes violates terms. This gives Vercel broad discretion but does not create an explicit scraping ban.

### Section 11 — Usage Restrictions
The most relevant section. Prohibits:
- (iii) unauthorized access to Services or related systems/networks
- (vi) violation of applicable laws or infringement of third-party rights

Key question: Is automated, public, read-only access to the marketing/templates gallery "unauthorized access"? The terms do not explicitly define it, and the pages are published without authentication. robots.txt does not block it. This is a **gray area** rather than a clear violation.

### Section 14 — Representations
Users must not infringe third-party IP, privacy, or publicity rights. Template metadata (title, description, GitHub URL, install command) is generally factual and publicly displayed, but the README text and page copy may contain copyrightable content.

### Section 15 — Indemnification
Users indemnify Vercel for breaches, infringement claims, or misuse of Services.

## Risk assessment

| Risk | Level | Notes |
|------|-------|-------|
| Breach of ToS for scraping public pages | **Low to medium** | No explicit ban; robots.txt allows; pages are public and unauthenticated. |
| Copyright in template descriptions/READMEs | **Medium** | Vercel or template authors may own copyright in descriptions and README text. We should not publish full READMEs verbatim. |
| Trademark use of "Vercel" / template names | **Low** | Nominative use to identify the service is generally acceptable; avoid implying official affiliation. |
| Rate-limiting / abuse | **Low** | Current implementation uses delays, concurrency limits, and a realistic User-Agent. |
| Vercel changing terms or robots.txt | **Medium** | Any future change could require re-evaluation. |

## Mitigations already in place

- Public pages only; no login or API credentials used.
- `robots.txt` is respected (`/templates` is allowed).
- Rate limiting: delays between category requests, limited concurrency.
- Realistic browser User-Agent.
- No mutation of Vercel systems; read-only indexing.
- Metadata is stored locally; the published `catalog.json` is a user-generated export.

## Recommended mitigations before v1.0.0

1. **Disclaim official affiliation.** README and documentation should state clearly: "This is an unofficial community tool and is not affiliated with or endorsed by Vercel."
2. **Limit redistribution of verbatim content.** Do not publish full READMEs or long excerpts from Vercel template detail pages in `catalog.json` or releases. Keep published data to metadata only (title, slug, framework, GitHub URL, install command, short description).
3. **Respect future robots.txt changes.** Add a nightly check that aborts indexing if `/templates` becomes disallowed.
4. **Document fair-use intent.** Explain that the tool helps users discover Vercel templates and always links back to the original Vercel pages and GitHub repositories.
5. **Consider contacting Vercel.** For a definitive green light, ask Vercel via their support or open-source team whether a read-only community index of the templates gallery is acceptable. This is the only way to eliminate legal uncertainty completely.

## Conclusion

A public v1.0.0 release appears **defensible** under current Vercel terms and robots.txt, provided the project remains read-only, respects rate limits, does not claim affiliation with Vercel, and avoids publishing substantial verbatim copyrighted content. The remaining legal risk is moderate and can be further reduced by adding the recommended mitigations and, ideally, obtaining explicit permission from Vercel.

**Decision:** Proceed to v1.0.0 after implementing the mitigations above, with a note that this is an ongoing legal risk to monitor.
