import Link from "next/link";
import { site } from "@/lib/site";
import { SiteNav } from "./site-nav";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-bg/85 backdrop-blur-md supports-[backdrop-filter]:bg-bg/70">
      <nav aria-label="Main" className="relative mx-auto flex h-16 w-full max-w-page items-center justify-between px-5 sm:px-8">
        <Link href="/" className="group flex min-h-11 items-center gap-2.5 font-semibold tracking-tight">
          <span aria-hidden className="grid size-6 place-items-center rounded-md bg-accent-solid text-accent-contrast">
            <span className="size-2 rounded-full bg-current transition-transform duration-base ease-out-quint group-hover:scale-125" />
          </span>
          {site.name}
        </Link>
        <SiteNav items={site.nav} />
      </nav>
    </header>
  );
}
