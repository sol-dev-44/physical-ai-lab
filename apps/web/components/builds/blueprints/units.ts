/**
 * Shared constants for the blueprints. Kept out of the "use client" modules on purpose: a server
 * component that imports a plain function or constant from a client module gets a client
 * reference, not the value, and calling it throws.
 */
import { duration } from "@/lib/design/motion";

export type ViewBox = readonly [x: number, y: number, width: number, height: number];

/**
 * The width, in CSS pixels, each drawing is laid out for: a 375 px phone less the page gutters
 * and the card padding. Labels are placed so they fit at this width; wider screens only add air.
 */
export const DESIGN_PX = 300;

/** On-screen size of drawing text, in CSS pixels. */
export const TEXT_PX = 11;

/** Drawing units per design pixel: multiply a pixel size by this to place things in a view. */
export const unitsPerPx = (viewBox: ViewBox) => viewBox[2] / DESIGN_PX;

/** Id of a view's section-hatch pattern, for `fill={hatchUrl(id)}`. */
export const hatchId = (id: string) => `${id}-hatch`;
export const hatchUrl = (id: string) => `url(#${hatchId(id)})`;

/** How long an outline takes to draw, and when the labels start to fade in. */
export const DRAW_S = duration.slow * 1.6;
export const LABELS_AT_S = DRAW_S * 0.7;

/** The TPU tire's solid fill: dark ink on paper, a softer grey in dark mode so it doesn't glare. */
export const TIRE_FILL = "fill-fg/70 dark:fill-fg/40";
