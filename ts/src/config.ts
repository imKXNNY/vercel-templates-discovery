import { join } from "node:path";
import { homedir } from "node:os";

export const BASE_URL = "https://vercel.com";

export const DEFAULT_CATEGORIES = [
  "next.js",
  "react",
  "vue",
  "svelte",
  "nuxt",
  "angular",
  "solid",
  "gatsby",
  "hugo",
  "jekyll",
  "eleventy",
  "astro",
  "remix",
  "tanstack-start",
  "docusaurus",
  "blog",
  "commerce",
  "dashboard",
  "ai",
  "portfolio",
  "documentation",
  "starter",
  "boilerplate",
];

export const FRAMEWORK_CATEGORIES = new Set([
  "next.js",
  "react",
  "vue",
  "svelte",
  "nuxt",
  "angular",
  "solid",
  "gatsby",
  "astro",
  "remix",
  "tanstack-start",
  "docusaurus",
]);

export function userAgent(): string {
  return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36";
}

export function cacheDbPath(): string {
  return join(homedir(), ".cache", "vercel-templates-discovery", "templates.db");
}
