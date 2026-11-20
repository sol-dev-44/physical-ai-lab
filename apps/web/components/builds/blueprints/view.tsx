"use client";

import { m } from "motion/react";
import { useEffect, useRef, type CSSProperties, type ReactNode } from "react";
import { cn } from "@/lib/design/cn";
import { hatchId, TEXT_PX, unitsPerPx, type ViewBox } from "./units";

/**
 * One drawing: a responsive SVG whose viewBox is in millimetres. It measures its width and sets
 * `--upx` (drawing units per CSS pixel) so text stays 11 px and outlines stay hairlines at any
 * width; text is capped at its design-width size so labels never outgrow their layout.
 * It also starts the draw-on animation the first time it scrolls into view.
 */
export function BlueprintView({
  id,
  viewBox,
  title,
  desc,
  caption,
  hatch,
  className,
  children,
}: {
  /** Prefix for ids inside the SVG (patterns, masks); unique on the page. */
  id: string;
  viewBox: ViewBox;
  /** Accessible name. */
  title: string;
  /** Accessible description with the key numbers. */
  desc: string;
  /** Short view label under the drawing, such as "Detail A · 3 : 1". */
  caption?: string;
  /** Spacing of the section hatch in drawing units; omit when the view has no section. */
  hatch?: number;
  className?: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLElement>(null);
  const [vx, vy, vw, vh] = viewBox;
  const design = unitsPerPx(viewBox);

  // Written straight to the element rather than through state: the figure is a plain element
  // React leaves alone between renders (its style prop never changes), and nothing re-renders
  // on resize. The SVG reads the variable for its text size and outline widths.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const set = (w: number) => {
      if (w > 0) el.style.setProperty("--upx", String(vw / w));
    };
    set(el.getBoundingClientRect().width);
    const ro = new ResizeObserver((entries) => set(entries[0]?.contentRect.width ?? 0));
    ro.observe(el);
    return () => ro.disconnect();
  }, [vw]);

  const figureStyle = { "--upx": String(design) } as CSSProperties;
  const svgStyle: CSSProperties = { fontSize: `calc(min(var(--upx), ${design}) * ${TEXT_PX}px)` };

  return (
    <figure ref={ref} className={cn("min-w-0", className)} style={figureStyle}>
      <m.svg
        viewBox={`${vx} ${vy} ${vw} ${vh}`}
        role="img"
        aria-labelledby={`${id}-title`}
        aria-describedby={`${id}-desc`}
        className="block h-auto w-full overflow-visible font-mono tabular-nums select-none"
        style={svgStyle}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, amount: 0.35 }}
      >
        <title id={`${id}-title`}>{title}</title>
        <desc id={`${id}-desc`}>{desc}</desc>
        {hatch ? (
          <defs>
            {/* Pattern content inherits from the pattern's ancestors, not from the shape that
                uses it, so the colour is set here. */}
            <pattern
              id={hatchId(id)}
              patternUnits="userSpaceOnUse"
              width={hatch}
              height={hatch}
              patternTransform="rotate(45)"
              className="text-accent"
            >
              <line
                x1={0}
                y1={0}
                x2={0}
                y2={hatch}
                stroke="currentColor"
                className="[stroke-width:calc(var(--upx)*1px)]"
                strokeOpacity={0.75}
              />
            </pattern>
          </defs>
        ) : null}
        {children}
      </m.svg>
      {caption ? (
        <figcaption className="mt-2 text-center font-mono text-[0.6875rem] tracking-[0.12em] text-subtle uppercase">
          {caption}
        </figcaption>
      ) : null}
    </figure>
  );
}
