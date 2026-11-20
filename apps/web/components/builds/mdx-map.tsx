import type { ReactNode } from "react";
import { BasePlan, CradleViews, WheelSection } from "@/components/builds/blueprints";
import { H2 } from "@/components/mdx";
import type { BuildData } from "@/lib/builds/data";
import { lookup, num, parseNumberList, unitFor } from "@/lib/builds/view";
import type { MdxComponents } from "@/lib/content/render";
import { BuildLog } from "./build-log";
import { Materials } from "./materials";
import { PartsList } from "./parts-list";
import { PrintedParts } from "./printed-parts";
import { Roadmap } from "./roadmap";
import { ServoSheet } from "./servo-sheet";

/**
 * A block that runs the full width of the body column. Everything else in a build write-up is
 * held to reading width by the wrapper's `[&>*:not([data-wide])]:max-w-prose`.
 */
function Wide({ children }: { children: ReactNode }) {
  return (
    <div data-wide className="not-prose my-10 sm:my-12">
      {children}
    </div>
  );
}

/** Build pages have a sticky chip bar under the site header on phones, so headings stop lower. */
function BuildH2({ children }: { children?: ReactNode }) {
  return <H2 className="scroll-mt-36 lg:scroll-mt-24">{children}</H2>;
}

type ValProps = { k: string; digits?: string; abs?: boolean; pct?: boolean; unit?: string };

/**
 * MDX components for one build, closed over its data, so a write-up places a panel with
 * `<PartsList />` and a number with `<Val k="tire.bore_mm" />` and never types either in.
 * MDX blocks JS expressions, so props arrive as strings (`digits="0"`) or bare flags (`abs`).
 *
 * Without data (a plain write-up) the data components render nothing, so the page still builds.
 */
export function buildComponents(data: BuildData | null): MdxComponents {
  const none = () => null;
  if (!data) {
    return {
      h2: BuildH2,
      Val: none,
      WheelSection: none,
      CradleViews: none,
      BasePlan: none,
      ServoSheet: none,
      PrintedParts: none,
      PartsList: none,
      Materials: none,
      BuildLog: none,
      Roadmap: none,
    };
  }

  const build: BuildData = data;
  function Val({ k, digits, abs, pct, unit }: ValProps) {
    const v = lookup(build, k);
    if (typeof v === "string") return <>{v}</>;
    const d = digits === undefined ? (pct ? 1 : 2) : Number(digits);
    const n = abs ? Math.abs(v) : v;
    const u = pct ? "%" : unit === "none" ? "" : (unit ?? unitFor(k));
    return (
      <span className="whitespace-nowrap tabular-nums">
        {num(pct ? n * 100 : n, d)}
        {u ? (u === "%" ? u : ` ${u}`) : null}
      </span>
    );
  }

  return {
    h2: BuildH2,
    Val,
    WheelSection: () => (
      <Wide>
        <WheelSection data={data} />
      </Wide>
    ),
    CradleViews: () => (
      <Wide>
        <CradleViews data={data} />
      </Wide>
    ),
    BasePlan: () => (
      <Wide>
        <BasePlan data={data} />
      </Wide>
    ),
    ServoSheet: () => (
      <Wide>
        <ServoSheet servo={data.servo} />
      </Wide>
    ),
    PrintedParts: () => (
      <Wide>
        <PrintedParts data={data} />
      </Wide>
    ),
    PartsList: () => (
      <Wide>
        <PartsList bom={data.bom} />
      </Wide>
    ),
    Materials: () => (
      <Wide>
        <Materials data={data} />
      </Wide>
    ),
    BuildLog: () => (
      <Wide>
        <BuildLog timeline={data.timeline} />
      </Wide>
    ),
    Roadmap: ({ current }: { current?: string }) => (
      <Wide>
        <Roadmap phases={data.phases} current={parseNumberList(current)} />
      </Wide>
    ),
  };
}
