import { getCollection, getEntry } from "@/lib/content/loader";
import { ogSize, renderCard } from "@/lib/og";
import { site } from "@/lib/site";

export const alt = `A write-up from ${site.name}`;
export const size = ogSize;
export const contentType = "image/png";

// Prerender one image per write-up at build time, like the pages themselves. Unknown slugs get the generic card.
export async function generateStaticParams() {
  return (await getCollection("experiments")).map((e) => ({ slug: e.slug }));
}

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const entry = await getEntry("experiments", (await params).slug);
  if (!entry) return renderCard({ title: site.tagline });
  return renderCard({
    eyebrow: `Experiment · ${entry.frontmatter.id}`,
    title: entry.frontmatter.title,
    footer: <div style={{ display: "flex" }}>{site.tagline}</div>,
  });
}
