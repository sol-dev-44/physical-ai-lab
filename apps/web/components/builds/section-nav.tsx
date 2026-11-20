"use client";

import { useEffect, useRef, useState } from "react";
import type { Heading } from "@/lib/content/headings";
import { cn } from "@/lib/design/cn";

/**
 * "On this page" for a long build write-up: a sticky rail from `lg` up and a sticky, horizontally
 * scrolling chip bar below it. Both highlight the section being read.
 *
 * Renders two siblings (not one wrapper) so each can stick inside the tall parent: a sticky
 * element only sticks within its containing block. `endId` names an element after the last
 * section, so a short final section still lights up when the page bottoms out.
 */
export function SectionNav({ headings, endId }: { headings: Heading[]; endId?: string }) {
  const active = useScrollSpy(headings, endId);
  const bar = useRef<HTMLUListElement>(null);

  // Keep the current chip in view in the mobile bar, without moving the page.
  useEffect(() => {
    const list = bar.current;
    const chip = list?.querySelector<HTMLElement>(`[data-id="${active}"]`);
    if (!list || !chip || list.offsetParent === null) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    list.scrollTo({
      left: chip.offsetLeft - list.clientWidth / 2 + chip.clientWidth / 2,
      behavior: reduce ? "auto" : "smooth",
    });
  }, [active]);

  if (headings.length < 2) return null;

  return (
    <>
      <nav aria-label="On this page" className="hidden lg:block">
        <div className="sticky top-24 max-h-[calc(100vh-7rem)] overflow-y-auto pb-6">
          <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">On this page</p>
          <ol className="mt-4 border-l border-line">
            {headings.map((h) => {
              const current = h.id === active;
              return (
                <li key={h.id}>
                  <a
                    href={`#${h.id}`}
                    aria-current={current ? "location" : undefined}
                    className={cn(
                      "relative -ml-px flex min-h-9 items-center border-l-2 py-1 pl-4 text-sm transition-colors duration-fast",
                      current
                        ? "border-accent font-medium text-fg"
                        : "border-transparent text-muted hover:border-line-strong hover:text-fg",
                    )}
                  >
                    {h.text}
                  </a>
                </li>
              );
            })}
          </ol>
          <a
            href="#top"
            className="mt-6 inline-flex min-h-11 items-center gap-1 text-sm text-subtle transition-colors duration-fast hover:text-accent"
          >
            <span aria-hidden>↑</span> Back to top
          </a>
        </div>
      </nav>

      <nav
        aria-label="On this page"
        className="sticky top-16 z-10 -mx-5 mb-8 border-b border-line bg-bg/90 backdrop-blur-md supports-[backdrop-filter]:bg-bg/75 sm:-mx-8 lg:hidden print:hidden"
      >
        <ul
          ref={bar}
          className="flex snap-x gap-2 overflow-x-auto overscroll-x-contain px-5 py-2 [scrollbar-width:none] sm:px-8 [&::-webkit-scrollbar]:hidden"
        >
          {headings.map((h) => {
            const current = h.id === active;
            return (
              <li key={h.id} data-id={h.id} className="shrink-0 snap-start">
                <a
                  href={`#${h.id}`}
                  aria-current={current ? "location" : undefined}
                  className={cn(
                    "inline-flex min-h-11 items-center rounded-full border px-4 text-sm whitespace-nowrap transition-colors duration-base ease-out-quint",
                    current
                      ? "border-accent bg-accent-soft font-medium text-accent"
                      : "border-line bg-surface text-muted hover:border-line-strong hover:text-fg",
                  )}
                >
                  {h.text}
                </a>
              </li>
            );
          })}
        </ul>
      </nav>
    </>
  );
}

/**
 * The id of the section being read: the last heading above a line 30% down the viewport.
 * An IntersectionObserver whose root is shrunk to the top 30% fires whenever a heading crosses
 * that line, a second one watches the end marker for the page's bottom, and `scrollend` catches
 * jumps that skip over the line.
 */
function useScrollSpy(headings: Heading[], endId?: string): string | undefined {
  const [active, setActive] = useState(headings[0]?.id);
  const ids = headings.map((h) => h.id).join("|");

  useEffect(() => {
    const els = ids
      .split("|")
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null);
    if (!els.length) return;
    let atEnd = false;

    const pick = () => {
      if (atEnd) {
        setActive(els.at(-1)?.id);
        return;
      }
      const line = window.innerHeight * 0.3;
      let current = els[0]?.id;
      for (const el of els) if (el.getBoundingClientRect().top <= line) current = el.id;
      setActive(current);
    };

    const spy = new IntersectionObserver(pick, { rootMargin: "0px 0px -70% 0px", threshold: [0, 1] });
    for (const el of els) spy.observe(el);

    const end = endId ? document.getElementById(endId) : null;
    const bottom = new IntersectionObserver((entries) => {
      atEnd = entries.some((e) => e.isIntersecting);
      pick();
    });
    if (end) bottom.observe(end);

    // A jump (a link, find-in-page, a restored scroll position) can carry a heading across the
    // line between two frames, which the observer never reports. Settle up when scrolling stops.
    window.addEventListener("scrollend", pick, { passive: true });
    window.addEventListener("resize", pick, { passive: true });

    pick();
    return () => {
      spy.disconnect();
      bottom.disconnect();
      window.removeEventListener("scrollend", pick);
      window.removeEventListener("resize", pick);
    };
  }, [ids, endId]);

  return active;
}
