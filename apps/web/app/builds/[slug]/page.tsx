import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { BuildHero } from "@/components/builds/build-hero";
import { buildComponents } from "@/components/builds/mdx-map";
import { SectionNav } from "@/components/builds/section-nav";
import { getBuildData } from "@/lib/builds/data";
import { extractHeadings } from "@/lib/content/headings";
import { getCollection, getEntry } from "@/lib/content/loader";
import { Mdx } from "@/lib/content/render";
import { cn } from "@/lib/design/cn";
import { site } from "@/lib/site";

const EMPTY_SLUG = "_empty";
const END_ID = "build-end";

export async function generateStaticParams() {
  const builds = await getCollection("builds");
  // Cache Components needs at least one param set; an empty collection prerenders a placeholder
  // that resolves to notFound().
  return builds.length ? builds.map((b) => ({ slug: b.slug })) : [{ slug: EMPTY_SLUG }];
}

export async function generateMetadata({ params }: PageProps<"/builds/[slug]">): Promise<Metadata> {
  const entry = await getEntry("builds", (await params).slug);
  return entry ? { title: entry.frontmatter.title, description: entry.frontmatter.summary } : {};
}

// A synchronous shell: reading params suspends inside the boundary, so client navigations stay
// instant. Every known slug is prerendered, so the fallback only shows for unknown ones.
export default function Page({ params }: PageProps<"/builds/[slug]">) {
  return (
    <Suspense fallback={<p className="text-sm text-muted">Loading…</p>}>
      <Build params={params} />
    </Suspense>
  );
}

async function Build({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const entry = await getEntry("builds", slug);
  if (!entry) notFound();
  // Only after the slug is known to be a real build, so a crafted slug never reaches the file read.
  const data = await getBuildData(entry.slug);
  const headings = extractHeadings(entry.body);
  const withNav = headings.length >= 2;

  return (
    <article>
      <BuildHero fm={entry.frontmatter} data={data} />
      <div className={cn(withNav && "lg:grid lg:grid-cols-[11rem_minmax(0,1fr)] lg:gap-12 xl:gap-16")}>
        {withNav ? <SectionNav headings={headings} endId={END_ID} /> : null}
        <div className="min-w-0">
          {/* Prose holds to reading width; blocks marked data-wide (drawings, panels) use the full column. */}
          <Mdx source={entry.body} components={buildComponents(data)} className="[&>*:not([data-wide])]:max-w-prose" />
          <div id={END_ID} aria-hidden className="h-px" />
          <footer className="mt-16 flex max-w-prose flex-col gap-3 border-t border-line pt-6 text-sm text-muted sm:flex-row sm:items-center sm:justify-between">
            {data ? (
              <p>
                Numbers on this page come from{" "}
                <a href={`${site.repo}/blob/main/${data.source}`} className="font-mono text-xs text-accent hover:underline">
                  {data.source}
                </a>
                .
              </p>
            ) : (
              <span />
            )}
            <Link href="/builds" className="inline-flex min-h-11 items-center font-medium text-accent hover:underline">
              ← All builds
            </Link>
          </footer>
        </div>
      </div>
    </article>
  );
}
