"use client";

import { m } from "motion/react";
import { cn } from "@/lib/design/cn";
import { duration, easeOutQuint } from "@/lib/design/motion";

/**
 * One segment of a horizontal meter that grows from the left when it scrolls into view.
 * `data-reveal` lets the no-JavaScript and print styles show it at full size.
 */
export function MeterFill({ fraction, className, delay = 0 }: { fraction: number; className?: string; delay?: number }) {
  const pct = `${Math.min(Math.max(fraction, 0), 1) * 100}%`;
  return (
    <m.div
      data-reveal
      aria-hidden
      className={cn("h-full origin-left", className)}
      style={{ width: pct }}
      initial={{ scaleX: 0 }}
      whileInView={{ scaleX: 1 }}
      viewport={{ once: true, margin: "0px 0px -10% 0px" }}
      transition={{ duration: duration.slow * 1.6, ease: easeOutQuint, delay }}
    />
  );
}
