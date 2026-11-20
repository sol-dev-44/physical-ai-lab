"use client";

import { AnimatePresence, m } from "motion/react";
import { useDeferredValue, useId, useMemo, useState } from "react";
import type { BuildData } from "@/lib/builds/data";
import { asins, bomGroups } from "@/lib/builds/view";
import { cn } from "@/lib/design/cn";
import { control } from "@/lib/design/controls";
import { duration, easeOutQuint } from "@/lib/design/motion";

type Row = BuildData["bom"][number];

const ALL = "All";

/** The bill of materials with group chips and a text search. Rows stack on phones. */
export function PartsList({ bom }: { bom: Row[] }) {
  const groups = useMemo(() => bomGroups(bom), [bom]);
  const [group, setGroup] = useState(ALL);
  const [query, setQuery] = useState("");
  const q = useDeferredValue(query.trim().toLowerCase());
  const searchId = useId();
  const statusId = useId();

  const rows = useMemo(
    () =>
      bom.filter(
        (r) =>
          (group === ALL || r.group === group) &&
          (!q || [r.item, r.asin, r.check, r.group, String(r.n)].some((f) => f.toLowerCase().includes(q))),
      ),
    [bom, group, q],
  );

  return (
    <div className="rounded-card border border-line bg-surface shadow-card">
      <div className="flex flex-col gap-3 border-b border-line p-4 sm:p-5">
        <div role="group" aria-label="Filter by group" className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1 [scrollbar-width:thin] sm:flex-wrap sm:overflow-visible sm:pb-0">
          {[{ group: ALL, count: bom.length }, ...groups].map((g) => {
            const on = g.group === group;
            return (
              <button
                key={g.group}
                type="button"
                aria-pressed={on}
                onClick={() => setGroup(g.group)}
                className={cn(
                  "inline-flex min-h-11 shrink-0 items-center gap-2 rounded-full border px-4 text-sm whitespace-nowrap transition-colors duration-base ease-out-quint",
                  on
                    ? "border-accent bg-accent-soft font-medium text-accent"
                    : "border-line text-muted hover:border-line-strong hover:text-fg",
                )}
              >
                {g.group}
                <span className={cn("font-mono text-xs tabular-nums", on ? "text-accent" : "text-subtle")}>{g.count}</span>
              </button>
            );
          })}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <label htmlFor={searchId} className="sr-only">
            Search parts
          </label>
          <input
            id={searchId}
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search parts, ASINs, checks…"
            aria-describedby={statusId}
            autoComplete="off"
            className={cn(control.input, "w-full sm:max-w-xs")}
          />
          <p id={statusId} aria-live="polite" className="font-mono text-xs text-subtle tabular-nums">
            {rows.length === bom.length ? `${bom.length} items` : `${rows.length} of ${bom.length} items`}
          </p>
        </div>
      </div>

      <div
        aria-hidden
        className="hidden grid-cols-[2.5rem_minmax(0,1fr)_9rem_8rem] gap-4 border-b border-line px-5 py-2.5 font-mono text-[0.6875rem] tracking-wider text-subtle uppercase md:grid"
      >
        <span>#</span>
        <span>Item · check on arrival</span>
        <span>Group</span>
        <span>ASIN</span>
      </div>

      <ul aria-label="Parts" className="divide-y divide-line">
        <AnimatePresence initial={false}>
          {rows.map((r) => (
            <m.li
              key={r.n}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, transition: { duration: duration.fast } }}
              transition={{ duration: duration.base, ease: easeOutQuint }}
              className="grid grid-cols-[2.5rem_minmax(0,1fr)] gap-x-4 gap-y-2 px-4 py-4 transition-colors duration-fast hover:bg-surface-2/60 sm:px-5 md:grid-cols-[2.5rem_minmax(0,1fr)_9rem_8rem] md:items-baseline"
            >
              <span className="font-mono text-sm text-subtle tabular-nums">{String(r.n).padStart(2, "0")}</span>
              <div className="min-w-0">
                <p className="font-medium text-fg">{r.item}</p>
                {r.check ? (
                  <p className="mt-1 text-sm text-muted">
                    <span className="font-mono text-[0.6875rem] tracking-wider text-warn uppercase">Check </span>
                    {r.check}
                  </p>
                ) : null}
              </div>
              <span className="col-start-2 text-sm text-muted md:col-start-auto">
                <span className="sr-only">Group: </span>
                {r.group}
              </span>
              <span className="col-start-2 flex flex-wrap gap-x-3 md:col-start-auto">
                {asins(r.asin).map((a) => (
                  <a
                    key={a}
                    href={`https://www.amazon.com/dp/${a}`}
                    className="inline-flex min-h-11 items-center font-mono text-sm text-accent underline-offset-2 hover:underline md:min-h-0"
                  >
                    <span className="sr-only">Amazon listing for item {r.n}, ASIN </span>
                    {a}
                  </a>
                ))}
              </span>
            </m.li>
          ))}
        </AnimatePresence>
      </ul>
      {rows.length === 0 ? (
        <div className="p-6 text-sm text-muted">
          Nothing matches “{query.trim()}”
          {group !== ALL ? ` in ${group}` : ""}.{" "}
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setGroup(ALL);
            }}
            className="inline-flex min-h-11 items-center font-medium text-accent underline underline-offset-2"
          >
            Clear filters
          </button>
        </div>
      ) : null}
    </div>
  );
}
