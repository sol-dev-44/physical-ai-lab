import Link from "next/link";
import { site } from "@/lib/site";
import { NavLink } from "./nav-link";

export function SiteHeader() {
  return (
    <header className="border-b border-line">
      <nav aria-label="Main" className="mx-auto flex max-w-4xl flex-wrap items-baseline gap-x-5 gap-y-2 px-4 py-4">
        <Link href="/" className="mr-auto font-semibold">
          {site.name}
        </Link>
        {site.nav.map((item) => (
          <NavLink key={item.href} href={item.href} label={item.label} />
        ))}
      </nav>
    </header>
  );
}
