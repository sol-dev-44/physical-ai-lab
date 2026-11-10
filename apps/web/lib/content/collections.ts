/**
 * Content collections: the schema for each kind of write-up.
 *
 * Write-ups live as MDX in /content/<collection>/<slug>.mdx at the repo root.
 * Front matter is validated here, so a bad field fails the build instead of
 * rendering a broken page.
 *
 * Numbers (trials, success rate, null-test gap) are NOT typed into front matter.
 * An experiment lists the run_ids it publishes, and the page computes results
 * from those runs' events.
 */
import { ExperimentId, RunId } from "@lab/schema";
import { z } from "zod";

const isoDate = z.iso.date();

const base = {
  title: z.string().min(1),
  date: isoDate,
  summary: z.string().min(1),
  tags: z.array(z.string()).default([]),
  /** Drafts render in dev and are hidden in production builds. */
  draft: z.boolean().default(false),
};

export const collections = {
  experiments: z.strictObject({
    ...base,
    id: ExperimentId,
    status: z.enum(["planned", "running", "done", "abandoned"]),
    hypothesis: z.string().optional(),
    hardware: z.array(z.string()).default([]),
    /** Runs whose results this write-up publishes. Order = display order. */
    runs: z.array(RunId).default([]),
    /** Set when the experiment lives in a standalone app. */
    app_url: z.url().optional(),
  }),
  log: z.strictObject({
    ...base,
    experiment: ExperimentId.optional(),
  }),
  builds: z.strictObject({
    ...base,
    status: z.enum(["planned", "building", "working", "retired"]),
    parts: z.array(z.string()).default([]),
  }),
} as const;

export type CollectionName = keyof typeof collections;
export type Frontmatter<C extends CollectionName> = z.output<(typeof collections)[C]>;
