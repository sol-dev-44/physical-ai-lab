"use client";

import { m, useReducedMotion, type Variants } from "motion/react";
import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";
import { duration, easeOutQuint } from "@/lib/design/motion";
import { DRAW_S, LABELS_AT_S } from "./units";

/**
 * Animated pieces of a blueprint. A BlueprintView switches its children from "hidden" to "show"
 * once it scrolls into view: outlines draw on, fills fade in under them, then labels fade in.
 * The drawing components themselves stay server components and only use these leaves.
 */

const draw: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  show: (delay: number = 0) => ({
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: { duration: DRAW_S, ease: easeOutQuint, delay },
      opacity: { duration: duration.fast, delay },
    },
  }),
};

const appear: Variants = {
  hidden: { opacity: 0 },
  show: (delay: number = 0) => ({
    opacity: 1,
    transition: { duration: duration.slow, ease: easeOutQuint, delay },
  }),
};

/**
 * Stroke widths for outlines are in screen pixels through `--upx` (drawing units per CSS pixel,
 * set by BlueprintView), not `vector-effect: non-scaling-stroke`: Chrome measures `pathLength`
 * dashes in user units but draws non-scaling dashes in screen pixels, so the draw-on animation
 * comes out chopped into dashes on a non-scaling path.
 */
const OUTLINE_WIDTH = {
  part: "[stroke-width:calc(var(--upx)*1.5px)]",
  context: "[stroke-width:calc(var(--upx)*1px)]",
} as const;

/** Print and no-JavaScript must show the finished drawing (see BlueprintFrame's noscript rule). */
const settled = "print:[stroke-dasharray:none]! print:opacity-100!";

/** An outline that draws itself on. `tone` picks the stroke weight; colour comes from className. */
export function Outline({
  d,
  className,
  delay = 0,
  tone = "part",
}: {
  d: string;
  className?: string;
  delay?: number;
  tone?: keyof typeof OUTLINE_WIDTH;
}) {
  const reduce = useReducedMotion();
  return (
    <m.path
      data-draw
      d={d}
      fill="none"
      stroke="currentColor"
      strokeLinejoin="round"
      strokeLinecap="round"
      className={cn(OUTLINE_WIDTH[tone], settled, className)}
      variants={reduce ? appear : draw}
      custom={delay}
    />
  );
}

/** A filled region (section hatch, solid) that fades in under its outline. */
export function Fill({
  d,
  className,
  fill,
  delay = DRAW_S * 0.35,
  fillRule,
}: {
  d: string;
  className?: string;
  /** An explicit fill such as a pattern url; otherwise style the fill with a class. */
  fill?: string;
  delay?: number;
  fillRule?: "evenodd" | "nonzero";
}) {
  return (
    <m.path
      data-reveal
      d={d}
      fill={fill}
      fillRule={fillRule}
      stroke="none"
      className={cn(settled, className)}
      variants={appear}
      custom={delay}
    />
  );
}

/** A group that fades in after the outlines: dimensions, labels, leaders. */
export function Fade({
  children,
  delay = 0,
  className,
}: {
  children: ReactNode;
  /** Extra delay after the labels' start. */
  delay?: number;
  className?: string;
}) {
  return (
    <m.g data-reveal className={cn(settled, className)} variants={appear} custom={LABELS_AT_S + delay}>
      {children}
    </m.g>
  );
}
