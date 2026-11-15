import Link from "next/link";
import { site } from "@/lib/site";

const more = [
  { href: `${site.repo}/blob/main/docs/architecture.md`, label: "Architecture" },
  { href: `${site.repo}/blob/main/docs/adr/README.md`, label: "Decision records" },
  { href: site.repo, label: "Code on GitHub" },
];

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-line">
      <div className="mx-auto grid w-full max-w-page gap-10 px-5 py-12 sm:grid-cols-[1.5fr_1fr_1fr] sm:px-8">
        <div className="max-w-sm">
          <p className="font-semibold tracking-tight">{site.name}</p>
          <p className="mt-2 text-sm text-muted">{site.tagline}</p>
          <p className="mt-4 text-xs text-subtle">
            Children never appear in published data, frames or write-ups (ADR 0007).
          </p>
        </div>
        <FooterList title="Lab" items={site.nav} />
        <FooterList title="Source" items={more} />
      </div>
    </footer>
  );
}

function FooterList({ title, items }: { title: string; items: readonly { href: string; label: string }[] }) {
  return (
    <div>
      <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">{title}</p>
      <ul className="mt-3 space-y-1">
        {items.map((i) => (
          <li key={i.href}>
            <Link href={i.href} className="inline-flex min-h-9 items-center text-sm text-muted hover:text-fg">
              {i.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
