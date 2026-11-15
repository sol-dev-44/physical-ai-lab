/** Heading ids and a contents list for MDX write-ups. Shared by the h2 component and the contents nav. */

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[`*_]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export type Heading = { id: string; text: string };

/** Level-2 headings (`## ...`) in document order, skipping fenced code blocks. */
export function extractHeadings(body: string): Heading[] {
  const out: Heading[] = [];
  let fenced = false;
  for (const line of body.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
    if (fenced) continue;
    const raw = /^##\s+(.+?)\s*#*\s*$/.exec(line)?.[1];
    if (raw) {
      const text = raw.replace(/[`*_]/g, "");
      out.push({ id: slugify(text), text });
    }
  }
  return out;
}
