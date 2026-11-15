"use client";

import { LazyMotion, MotionConfig } from "motion/react";
import type { ReactNode } from "react";

const loadFeatures = () => import("./features").then((m) => m.default);

/**
 * Loads the small DOM animation feature set in its own chunk after the page is interactive
 * (use `m.*`, not `motion.*`, so the full bundle never ships) and respects the visitor's
 * reduced-motion setting. Layout animations (`layoutId`) need the larger set; don't use them.
 */
export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={loadFeatures} strict>
      <MotionConfig reducedMotion="user">{children}</MotionConfig>
    </LazyMotion>
  );
}
