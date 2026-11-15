"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/design/cn";

export function isCurrent(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Header link that marks the section the reader is in (for sight and for screen readers). */
export function NavLink({ href, label }: { href: string; label: string }) {
  const current = isCurrent(usePathname(), href);
  return (
    <Link
      href={href}
      aria-current={current ? "page" : undefined}
      className={cn(
        "relative inline-flex min-h-11 items-center px-3 text-sm transition-colors duration-fast",
        current ? "text-fg" : "text-muted hover:text-fg",
      )}
    >
      {label}
      {current ? (
        <span aria-hidden className="absolute inset-x-3 bottom-1.5 h-0.5 rounded-full bg-accent" />
      ) : null}
    </Link>
  );
}
