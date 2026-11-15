/**
 * Shared builders for collection routes so every collection gets the same
 * index page, detail page, static params and metadata.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { type ReactNode, Suspense } from "react";
import Link from "next/link";
import { EntryList } from "@/components/entry-list";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/format";
import type { CollectionName } from "./collections";
import { type Entry, getCollection, getEntry } from "./loader";
import { extractHeadings } from "./headings";
import { Mdx } from "./render";

const EMPTY_SLUG = "_empty";
const eyebrows: Record<CollectionName, string> = {
  experiments: "Experiments",
  log: "Lab log",
  builds: "Builds",
  research: "Research",
};
const indexRoutes: Record<CollectionName, string> = {
  experiments: "/experiments",
  log: "/log",
  builds: "/builds",
  research: "/research",
};

export function collectionIndex(collection: CollectionName, title: string, intro: string, empty: string) {
  return async function Index() {
    const entries = await getCollection(collection);
    return (
      <>
        <PageHeader eyebrow={eyebrows[collection]} title={title} intro={intro} />
        <EntryList entries={entries} empty={empty} />
      </>
    );
  };
}

export function collectionDetail<C extends CollectionName>(
  collection: C,
  aside?: (entry: Entry<C>) => ReactNode,
  footer?: (entry: Entry<C>) => ReactNode,
) {
  async function generateStaticParams() {
    const entries = await getCollection(collection);
    // Cache Components requires at least one param set. An empty collection
    // prerenders a single placeholder slug that resolves to notFound().
    return entries.length ? entries.map((e) => ({ slug: e.slug })) : [{ slug: EMPTY_SLUG }];
  }

  async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
    const entry = await getEntry(collection, (await params).slug);
    return entry ? { title: entry.frontmatter.title, description: entry.frontmatter.summary } : {};
  }

  // The page is a synchronous shell; reading params suspends inside the boundary
  // so client navigations stay instant.
  function Detail({ params }: { params: Promise<{ slug: string }> }) {
    return (
      <Suspense fallback={<p className="mx-auto max-w-prose text-sm text-muted">Loading…</p>}>
        <Article params={params} />
      </Suspense>
    );
  }

  async function Article({ params }: { params: Promise<{ slug: string }> }) {
    const entry = await getEntry(collection, (await params).slug);
    if (!entry) notFound();
    const fm = entry.frontmatter;
    return (
      <article className="mx-auto max-w-prose">
        <header className="mb-10">
          <Link
            href={indexRoutes[collection]}
            className="inline-flex min-h-11 items-center font-mono text-xs tracking-[0.14em] text-accent uppercase hover:underline"
          >
            ← {eyebrows[collection]}
          </Link>
          <h1 className="mt-2 text-title font-semibold">{fm.title}</h1>
          <p className="mt-3 flex flex-wrap items-center gap-2 text-sm text-subtle">
            <time dateTime={fm.date} className="font-mono">
              {formatDate(fm.date)}
            </time>
            {fm.draft ? <Badge tone="warn">Draft</Badge> : null}
          </p>
          <p className="mt-6 text-lg text-muted">{fm.summary}</p>
        </header>
        {aside?.(entry)}
        <Contents body={entry.body} />
        <Mdx source={entry.body} />
        {footer?.(entry)}
      </article>
    );
  }

  return { generateStaticParams, generateMetadata, Detail };
}

/** "Contents" list for long write-ups (four or more sections). */
function Contents({ body }: { body: string }) {
  const headings = extractHeadings(body);
  if (headings.length < 4) return null;
  return (
    <nav aria-label="Contents" className="mb-12 rounded-card border border-line bg-surface p-5">
      <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">Contents</p>
      <ol className="mt-3 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
        {headings.map((h) => (
          <li key={h.id}>
            <a href={`#${h.id}`} className="inline-flex min-h-9 items-center text-muted hover:text-accent">
              {h.text}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
