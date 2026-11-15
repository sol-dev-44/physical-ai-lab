"use client";

import { AnimatePresence, m } from "motion/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useId, useState } from "react";
import { cn } from "@/lib/design/cn";
import { duration, easeOutQuint } from "@/lib/design/motion";
import type { NavItem } from "@/lib/site";
import { NavLink, isCurrent } from "./nav-link";

/** Inline links from `sm` up; a disclosure menu on phones. */
export function SiteNav({ items }: { items: readonly NavItem[] }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const menuId = useId();

  return (
    <div onKeyDown={(e) => e.key === "Escape" && setOpen(false)}>
      <ul className="hidden items-center sm:flex">
        {items.map((item) => (
          <li key={item.href}>
            <NavLink href={item.href} label={item.label} />
          </li>
        ))}
      </ul>

      <button
        type="button"
        className="-mr-2 inline-flex size-11 items-center justify-center rounded-control text-fg sm:hidden"
        aria-expanded={open}
        aria-controls={menuId}
        onClick={() => setOpen((o) => !o)}
      >
        <span className="sr-only">{open ? "Close menu" : "Open menu"}</span>
        <span aria-hidden className="relative block h-3 w-5">
          <span
            className={cn(
              "absolute inset-x-0 top-0 h-0.5 rounded-full bg-current transition-transform duration-base ease-out-quint",
              open && "translate-y-[5px] rotate-45",
            )}
          />
          <span
            className={cn(
              "absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-current transition-transform duration-base ease-out-quint",
              open && "-translate-y-[5px] -rotate-45",
            )}
          />
        </span>
      </button>

      <AnimatePresence>
        {open ? (
          <m.div
            id={menuId}
            key="menu"
            className="absolute inset-x-0 top-full border-b border-line bg-bg sm:hidden"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: duration.base, ease: easeOutQuint }}
          >
            <ul className="px-5 py-2">
              {items.map((item) => {
                const current = isCurrent(pathname, item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={current ? "page" : undefined}
                      onClick={() => setOpen(false)}
                      className={cn(
                        "flex min-h-12 items-center justify-between border-b border-line text-base last:border-0",
                        current ? "font-medium text-fg" : "text-muted",
                      )}
                    >
                      {item.label}
                      {current ? <span aria-hidden className="size-1.5 rounded-full bg-accent" /> : null}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </m.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
