---
name: vercel-templates
description: Search and discover Vercel Templates from Hermes agents.
category: productivity
tags: [vercel, templates, discovery, agentic]
---

# vercel-templates skill

Search the indexed Vercel Templates catalog by keyword, get full details for a single template, or list available frameworks and use cases.

## Requirements

- `vercel-templates-discovery` Python package installed and the catalog indexed (`vercel-templates index`).
- Or the `ts/` Node.js implementation built and indexed.

## Tools

### search_templates

Search the catalog by keyword.

```json
{
  "query": "AI chatbot",
  "limit": 5
}
```

### get_template

Get full details for a template by slug.

```json
{
  "slug": "/templates/next.js/chatbot"
}
```

### list_categories

List available frameworks and use cases.

```json
{}
```

## Usage from Hermes

If this skill is loaded, you can ask:

- "Find me a Next.js ecommerce template."
- "Show details for the Vercel AI chatbot template."
- "What template categories do we have?"

The skill will call the catalog and return structured results.
