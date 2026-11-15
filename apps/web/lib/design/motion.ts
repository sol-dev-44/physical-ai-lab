/**
 * Motion tokens for JS animations (motion/react). They mirror the CSS tokens in
 * app/globals.css (--ease-out-quint, --duration-*), so CSS transitions and JS
 * animations feel like one system. Use CSS for hover and focus states; use these
 * for enter, reveal and layout animations.
 */
import type { Transition, Variants } from "motion/react";

export const easeOutQuint = [0.22, 1, 0.36, 1] as const;

export const duration = { fast: 0.15, base: 0.25, slow: 0.5 } as const;

export const spring: Transition = { type: "spring", stiffness: 420, damping: 36, mass: 0.8 };

/** Fade and rise a few pixels. Reduced motion (MotionConfig "user") keeps the fade only. */
export const rise: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: duration.slow, ease: easeOutQuint } },
};

export const stagger = (step = 0.06): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: step } },
});
