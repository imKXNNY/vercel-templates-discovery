import { describe, expect, it } from "vitest";
import {
  VercelTemplateScraper,
  extractFlightChunk,
  extractInstallCommand,
  extractJsonString,
  extractReadmeText,
  extractSidebarValues,
  unescapeHtml,
  unescapeJsonString,
} from "../src/scraper.js";
import { TemplateDatabase } from "../src/db.js";
import type { TemplateInput } from "../src/types.js";

const sampleFlightPayload =
  'self.__next_f.push([1,"S1:{\\"readmeText\\":\\"$REF123\\"}"])' +
  "REF123:\"\\n# Hello\\nThis is a test.\"\nself.__next_f.push([1,\"REF123:ignored\"])";

describe("scraper helpers", () => {
  it("unescapes HTML entities", () => {
    expect(unescapeHtml("A &amp; B")).toBe("A & B");
  });

  it("unescapes JSON strings", () => {
    expect(unescapeJsonString("hello\\nworld")).toBe("hello\nworld");
  });

  it("extracts githubUrl", () => {
    const text = '\\"githubUrl\\":\\"https://github.com/vercel/vercel/tree/main/examples/nextjs\\"';
    expect(extractJsonString(text, "githubUrl")).toBe(
      "https://github.com/vercel/vercel/tree/main/examples/nextjs",
    );
  });

  it("extracts sidebar values", () => {
    const text = '\\"children\\":\\"Framework\\"\\"children\\":\\"Next.js\\"';
    expect(extractSidebarValues(text, "Framework")).toEqual(["Next.js"]);
  });

  it("extracts flight chunk", () => {
    const scripts = `\\"readmeText\\":\\"$REF123\\" ... REF123:prefix self.__next_f.push([1,"\\n# Title\\nBody"])`;
    expect(extractFlightChunk(scripts, "REF123")).toBe("\\n# Title\\nBody");
  });

  it("extracts readme text", () => {
    const scripts = `\\"readmeText\\":\\"$REF123\\" some junk REF123:x self.__next_f.push([1,"\\n# Title\\nMore"])`;
    expect(extractReadmeText(scripts)).toBe("\n# Title\nMore");
  });

  it("extracts install command from README", () => {
    const readme = "```bash\nnpm install\nnpx create-next-app --example foo bar\n```";
    expect(extractInstallCommand(readme, "")).toBe(
      "npx create-next-app --example foo bar",
    );
  });
});

describe("TemplateDatabase", () => {
  it("saves and searches templates", () => {
    const db = new TemplateDatabase(":memory:");
    const template: TemplateInput = {
      slug: "/templates/next.js/chatbot",
      framework: "next.js",
      title: "Chatbot",
      description: "AI chatbot template",
      github_url: "https://github.com/vercel/ai-chatbot",
      owner: "vercel",
      repository: "ai-chatbot",
      use_cases: "AI",
      frameworks: "Next.js",
      css: "Tailwind",
      databases: "",
      authentication: "",
      cms: "",
      experimentation: "",
      readme_text: "# Chatbot\nA chatbot.",
      install_command: "npx create-next-app --example chatbot my-app",
      detail_url: "https://vercel.com/templates/next.js/chatbot",
      indexed_at: 123456,
    };
    db.saveTemplates([template]);
    const results = db.search("chatbot");
    expect(results.length).toBe(1);
    expect(results[0].title).toBe("Chatbot");
    db.close();
  });
});
