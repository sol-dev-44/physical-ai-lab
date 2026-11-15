"use client";

import { m } from "motion/react";
import type { ReactNode } from "react";
import { rise, stagger } from "@/lib/design/motion";

const viewport = { once: true, margin: "0px 0px -10% 0px" } as const;

/**
 * Fades content in as it scrolls into view. For below-the-fold content only: the hero
 * and anything that is the page's main content render without it, so they paint at once.
 */
export function Reveal({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <m.div
      data-reveal
      className={className}
      variants={rise}
      initial="hidden"
      whileInView="show"
      viewport={viewport}
    >
      {children}
    </m.div>
  );
}

/** A list whose items (RevealItem) appear one after another. */
export function RevealList({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <m.ul data-reveal className={className} variants={stagger()} initial="hidden" whileInView="show" viewport={viewport}>
      {children}
    </m.ul>
  );
}

export function RevealItem({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <m.li data-reveal className={className} variants={rise}>
      {children}
    </m.li>
  );
}
