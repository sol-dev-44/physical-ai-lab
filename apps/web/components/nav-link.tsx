"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/** Header link that marks the section the reader is in (for sight and for screen readers). */
export function NavLink({ href, label }: { href: string; label: string }) {
  const pathname = usePathname();
  const current = pathname === href || pathname.startsWith(`${href}/`);
  return (
    <Link
      href={href}
      aria-current={current ? "page" : undefined}
      className={`text-sm hover:text-fg ${current ? "text-fg" : "text-muted"}`}
    >
      {label}
    </Link>
  );
}
