import { expect, it } from "vitest";
import { escapeXml, renderFeed, rfc822 } from "../lib/feed";

it("escapes XML special characters", () => {
  expect(escapeXml(`a & b < c > "d" 'e'`)).toBe("a &amp; b &lt; c &gt; &quot;d&quot; &apos;e&apos;");
});

it("formats RSS dates in UTC", () => {
  expect(rfc822("2026-11-15")).toBe("Sun, 15 Nov 2026 00:00:00 GMT");
});

it("renders a channel with escaped items", () => {
  const xml = renderFeed({ title: "Lab", url: "https://x.test", description: "d" }, [
    { title: "A & B", url: "https://x.test/a", date: "2026-11-15", summary: "<s>", category: "Lab log" },
  ]);
  expect(xml).toContain("<title>A &amp; B</title>");
  expect(xml).toContain("<description>&lt;s&gt;</description>");
  expect(xml.startsWith('<?xml version="1.0"')).toBe(true);
});
