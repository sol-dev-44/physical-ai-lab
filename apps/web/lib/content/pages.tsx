/**
 * Shared builders for collection routes so every collection gets the same
 * index page, detail page, static params and metadata.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { type ReactNode, Suspense } from "react";
import { EntryList } from "@/components/entry-list";
import { PageHeader } from "@/components/page-header";
import type { CollectionName } from "./collections";
import { type Entry, getCollection, getEntry } from "./loader";
import { Mdx } from "./render";

const EMPTY_SLUG = "_empty";

export function collectionIndex(collection: CollectionName, title: string, intro: string, empty: string) {
  return async function Index() {
    const entries = await getCollection(collection);
    return (
      <>
        <PageHeader title={title} intro={intro} />
        <EntryList entries={entries} empty={empty} />
      </>
    );
  };
}

export function collectionDetail<C extends CollectionName>(
  collection: C,
  aside?: (entry: Entry<C>) => ReactNode,
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
      <Suspense fallback={<p className="text-sm text-muted">Loading…</p>}>
        <Article params={params} />
      </Suspense>
    );
  }

  async function Article({ params }: { params: Promise<{ slug: string }> }) {
    const entry = await getEntry(collection, (await params).slug);
    if (!entry) notFound();
    const fm = entry.frontmatter;
    return (
      <article>
        <header className="mb-8">
          <h1 className="text-2xl font-semibold">{fm.title}</h1>
          <p className="mt-1 text-sm text-muted">
            <time dateTime={fm.date}>{fm.date}</time>
            {fm.draft ? " · draft" : null}
          </p>
          <p className="mt-3">{fm.summary}</p>
        </header>
        {aside?.(entry)}
        <Mdx source={entry.body} />
      </article>
    );
  }

  return { generateStaticParams, generateMetadata, Detail };
}
