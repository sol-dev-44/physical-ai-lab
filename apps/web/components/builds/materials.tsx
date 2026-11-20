import { Reveal } from "@/components/motion/reveal";
import type { BuildData } from "@/lib/builds/data";
import { type Spools, grams, groupByDate, num, petgSpools } from "@/lib/builds/view";
import { formatDate } from "@/lib/format";
import { MeterFill } from "./meter-fill";

const dash = <span className="text-subtle">—</span>;

/** Consumables: the PETG meter, the stock table and the usage log. */
export function Materials({ data }: { data: BuildData }) {
  const { stock, usage } = data.consumables;
  const spools = petgSpools(data);
  return (
    <div className="space-y-8">
      {spools ? (
        <Reveal>
          <PetgMeter spools={spools} />
        </Reveal>
      ) : null}

      <Reveal>
        <div className="overflow-hidden rounded-card border border-line bg-surface shadow-card">
          <p className="border-b border-line px-5 py-3 font-mono text-xs tracking-[0.14em] text-subtle uppercase">Stock</p>
          {/* Phones: one card per item. */}
          <ul className="divide-y divide-line md:hidden">
            {stock.map((s) => (
              <li key={s.item} className="px-5 py-4">
                <p className="font-medium">{s.item}</p>
                <dl className="mt-3 grid grid-cols-3 gap-3 text-sm">
                  <Cell label="Start" value={s.start} />
                  <Cell label="Used" value={s.used} />
                  <Cell label="Left" value={s.left} />
                </dl>
                {s.planned || s.reorder || s.lead_time ? (
                  <dl className="mt-3 space-y-1.5 text-sm">
                    {s.planned ? <Line label="Planned" value={s.planned} /> : null}
                    {s.reorder ? <Line label="Reorder" value={s.reorder} /> : null}
                    {s.lead_time ? <Line label="Lead time" value={s.lead_time} /> : null}
                  </dl>
                ) : null}
              </li>
            ))}
          </ul>
          {/* From md up: a real table. */}
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full text-left text-sm">
              <thead className="font-mono text-[0.6875rem] tracking-wider text-subtle uppercase">
                <tr className="border-b border-line">
                  <th scope="col" className="px-5 py-2.5 font-medium">Item</th>
                  <th scope="col" className="px-3 py-2.5 font-medium">Start</th>
                  <th scope="col" className="px-3 py-2.5 font-medium">Used</th>
                  <th scope="col" className="px-3 py-2.5 font-medium">Left</th>
                  <th scope="col" className="px-3 py-2.5 font-medium">Planned</th>
                  <th scope="col" className="px-5 py-2.5 font-medium">Reorder</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line align-top">
                {stock.map((s) => (
                  <tr key={s.item} className="transition-colors duration-fast hover:bg-surface-2/60">
                    <th scope="row" className="w-[22%] px-5 py-3 font-medium text-fg">{s.item}</th>
                    <td className="px-3 py-3 text-muted">{s.start || dash}</td>
                    <td className="px-3 py-3 text-muted">{s.used || dash}</td>
                    <td className="px-3 py-3 text-fg">{s.left || dash}</td>
                    <td className="px-3 py-3 text-muted">{s.planned || dash}</td>
                    <td className="px-5 py-3 text-muted">
                      {s.reorder || dash}
                      {s.lead_time ? <span className="mt-1 block text-xs text-subtle">Lead time: {s.lead_time}</span> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Reveal>

      <Reveal>
        <div className="rounded-card border border-line bg-surface p-5 shadow-card">
          <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">Usage log</p>
          <ol className="mt-4 space-y-5">
            {groupByDate(usage).map((g) => (
              <li key={g.date} className="grid gap-2 sm:grid-cols-[7.5rem_1fr] sm:gap-6">
                <time dateTime={g.date} className="font-mono text-xs text-subtle sm:pt-0.5">
                  {formatDate(g.date)}
                </time>
                <ul className="divide-y divide-line border-y border-line">
                  {g.items.map((u, i) => (
                    <li key={`${u.what}-${i}`} className="flex flex-wrap justify-between gap-x-6 gap-y-0.5 py-2 text-sm">
                      <span className="text-fg">{u.what}</span>
                      <span className="font-mono text-xs text-muted sm:text-sm">{u.used}</span>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ol>
        </div>
      </Reveal>
    </div>
  );
}

function PetgMeter({ spools }: { spools: Spools }) {
  const { capacity, used, left, sealed, planned, plannedText } = spools;
  const plannedOnSpool = planned !== null ? Math.min(planned, left) : 0;
  const both = left + (sealed ?? 0);
  const afterPlan = planned !== null ? Math.round((both - planned) / 10) * 10 : null;
  return (
    <div className="rounded-card border border-line bg-surface p-5 shadow-card sm:p-6">
      <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-2">
        <div>
          <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">PETG on hand</p>
          <p className="mt-2 font-mono text-3xl font-semibold tracking-tight tabular-nums">
            {grams(both, 0)}
            <span className="ml-2 font-sans text-sm font-normal tracking-normal text-muted">left of {grams(capacity + (sealed ?? 0), 0)}</span>
          </p>
        </div>
        {afterPlan !== null ? (
          <p className="max-w-xs text-sm text-muted">
            About <span className="font-mono text-fg tabular-nums">{grams(afterPlan, 0)}</span> to spare once the
            planned parts are printed.
          </p>
        ) : null}
      </div>

      <div className="mt-6 space-y-5">
        <div>
          <div className="flex justify-between text-sm">
            <span className="font-medium">Spool 1</span>
            <span className="font-mono text-muted tabular-nums">
              {grams(used, 0)} used · {grams(left, 0)} left
            </span>
          </div>
          <div
            role="meter"
            aria-label="PETG spool 1 used"
            aria-valuemin={0}
            aria-valuemax={capacity}
            aria-valuenow={used}
            aria-valuetext={`${num(used, 0)} of ${num(capacity, 0)} grams used`}
            className="mt-2 flex h-4 overflow-hidden rounded-full bg-surface-2 ring-1 ring-line ring-inset"
          >
            <MeterFill fraction={used / capacity} className="bg-accent-solid" />
            {plannedOnSpool > 0 ? (
              <MeterFill
                fraction={plannedOnSpool / capacity}
                delay={0.35}
                className="bg-[repeating-linear-gradient(135deg,var(--accent-soft)_0_5px,transparent_5px_10px)] ring-1 ring-accent/30 ring-inset"
              />
            ) : null}
          </div>
        </div>

        {sealed !== null ? (
          <div>
            <div className="flex justify-between text-sm">
              <span className="font-medium">Spool 2</span>
              <span className="font-mono text-muted tabular-nums">sealed · {grams(sealed, 0)}</span>
            </div>
            <div
              role="meter"
              aria-label="PETG spool 2 used"
              aria-valuemin={0}
              aria-valuemax={sealed}
              aria-valuenow={0}
              aria-valuetext="Sealed, none used"
              className="mt-2 h-4 rounded-full bg-surface-2 ring-1 ring-line ring-inset"
            />
          </div>
        ) : null}
      </div>

      <ul className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted">
        <li className="flex items-center gap-2">
          <span aria-hidden className="size-3 rounded-sm bg-accent-solid" /> Used (usage log)
        </li>
        {plannedOnSpool > 0 ? (
          <li className="flex items-center gap-2">
            <span
              aria-hidden
              className="size-3 rounded-sm bg-[repeating-linear-gradient(135deg,var(--accent-soft)_0_3px,transparent_3px_6px)] ring-1 ring-accent/30 ring-inset"
            />
            Planned: {plannedText}
          </li>
        ) : null}
        <li className="flex items-center gap-2">
          <span aria-hidden className="size-3 rounded-sm bg-surface-2 ring-1 ring-line ring-inset" /> Free
        </li>
      </ul>
    </div>
  );
}

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-mono text-[0.6875rem] tracking-wider text-subtle uppercase">{label}</dt>
      <dd className="mt-0.5 text-fg">{value || dash}</dd>
    </div>
  );
}

function Line({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2">
      <dt className="w-20 shrink-0 text-subtle">{label}</dt>
      <dd className="text-muted">{value}</dd>
    </div>
  );
}
