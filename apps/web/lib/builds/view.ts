/**
 * Pure view helpers for a build's page: every number the page shows is computed here from the
 * exported BuildData, never typed into a component. No server-only imports, so tests can load it.
 */
import type { BuildData } from "./data";

const formatters = new Map<number, Intl.NumberFormat>();

/** A number with at most `digits` decimals, grouped ("1,000"). Fixed locale so server and client agree. */
export function num(value: number, digits = 2): string {
  let f = formatters.get(digits);
  if (!f) {
    f = new Intl.NumberFormat("en-GB", { maximumFractionDigits: digits });
    formatters.set(digits, f);
  }
  return f.format(value);
}

/** Millimetres, with a no-break space before the unit. */
export function mm(value: number, digits = 0): string {
  return `${num(value, digits)} mm`;
}

export function grams(value: number, digits = 1): string {
  return `${num(value, digits)} g`;
}

/** Capitalise the first letter: the exported log lines start mid-sentence ("design chosen ..."). */
export function sentence(text: string): string {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : text;
}

/** The first "<number> g" in a free-text cell ("about 846 g", "1000 g"), or null. */
export function parseGrams(text: string): number | null {
  const m = /(\d[\d,]*(?:\.\d+)?)\s*g\b/.exec(text);
  return m?.[1] ? Number(m[1].replace(/,/g, "")) : null;
}

/** Grams of one material in a usage cell ("PETG 10.0 g; 4 x M2 x 6 ..."), or null. */
export function materialGrams(text: string, material: string): number | null {
  const m = new RegExp(`${material}\\s+(\\d+(?:\\.\\d+)?)\\s*g\\b`, "i").exec(text);
  return m?.[1] ? Number(m[1]) : null;
}

/** An ASIN cell can hold several ("B07426WCLM, B0DNCJRX18"). */
export function asins(cell: string): string[] {
  return cell
    .split(/[,\s]+/)
    .map((a) => a.trim())
    .filter((a) => /^[A-Z0-9]{10}$/.test(a));
}

/** Total parts printed (sum of the quantity column). */
export function printedCount(d: BuildData): number {
  return d.printed.reduce((n, p) => n + (Number.parseInt(p.qty, 10) || 0), 0);
}

export type Spools = {
  /** Spool 1: capacity and what the usage log adds up to. */
  capacity: number;
  used: number;
  left: number;
  /** The sealed second spool, when the stock table has one. */
  sealed: number | null;
  /** Grams the next parts are estimated to take, when the stock table says. */
  planned: number | null;
  plannedText: string;
};

/** PETG stock from the consumables table plus petg_used_g; null if the table has no PETG spool 1. */
export function petgSpools(d: BuildData): Spools | null {
  const stock = d.consumables.stock;
  const first = stock.find((s) => /petg/i.test(s.item) && /spool 1/i.test(s.item));
  const capacity = first ? parseGrams(first.start) : null;
  if (!first || capacity === null) return null;
  const second = stock.find((s) => /petg/i.test(s.item) && (/spool 2/i.test(s.item) || /sealed/i.test(s.item)));
  const sealed = second ? parseGrams(second.left) ?? parseGrams(second.start) : null;
  return {
    capacity,
    used: d.petg_used_g,
    left: Math.max(capacity - d.petg_used_g, 0),
    sealed,
    planned: parseGrams(first.planned),
    plannedText: first.planned,
  };
}

export type HeroStat = { value: string; label: string; note?: string };

/** The headline numbers for the hero and the index card. */
export function heroStats(d: BuildData): HeroStat[] {
  const { base, wheel } = d;
  const behind = (x: number) => (x <= 0 ? "behind" : "ahead of");
  const spools = petgSpools(d);
  return [
    { value: mm(base.width_over_tires_mm), label: "Width over the tires", note: `track ${mm(base.track_mm)}` },
    { value: mm(wheel.od_mm), label: "Wheel diameter", note: `${mm(wheel.width_mm)} wide` },
    {
      value: mm(Math.abs(base.com_x_mm)),
      label: `Centre of mass ${behind(base.com_x_mm)} the axle`,
      note: `${mm(Math.abs(base.com_x_with_arm_mm))} ${behind(base.com_x_with_arm_mm)} with the v2 arm reaching forward`,
    },
    { value: num(printedCount(d), 0), label: "Parts printed", note: `${d.printed.length} designs` },
    {
      value: grams(d.petg_used_g, 0),
      label: "PETG used",
      note: spools ? `of a ${grams(spools.capacity, 0)} spool` : undefined,
    },
  ];
}

export type PrintedCard = {
  title: string;
  material: string | null;
  qty: string;
  status: string;
  notes: string;
  dates: string[];
  grams: number | null;
  /** Fasteners from the usage log ("4 x M2 x 6 self-tapping (servo bag)"). */
  fixings: string[];
  retired: boolean;
  /** Position of its first line in the usage log, which is in the order things happened. */
  order: number;
};

/**
 * One card per printed part, joined to the usage log by name: "exp003 wheel hub, PETG" matches
 * "Two wheel hubs". The printed table has no dates or grams of its own (see the report on the
 * data contract), so a part the log does not name shows without them.
 */
export function printedCards(d: BuildData): PrintedCard[] {
  const cards = d.printed.map((p) => {
    const materialMatch = /,\s*([A-Za-z]+[\w ]*)$/.exec(p.item);
    const material = materialMatch?.[1]?.trim() ?? null;
    const name = p.item
      .replace(/^exp\d+\s+/i, "")
      .replace(/,\s*[^,]+$/, "")
      .trim();
    const key = name.toLowerCase();
    const usage = d.consumables.usage;
    const uses = usage.filter((u) => u.what.toLowerCase().includes(key));
    const g = material ? uses.map((u) => materialGrams(u.used, material)) : [];
    const known = g.filter((x): x is number => x !== null);
    const fixings = uses.flatMap((u) =>
      u.used
        .split(";")
        .map((s) => s.trim())
        .filter((s) => s && (!material || !new RegExp(`^${material}\\b`, "i").test(s))),
    );
    return {
      title: sentence(name),
      material,
      qty: p.qty,
      status: p.status,
      notes: p.notes,
      dates: [...new Set(uses.map((u) => u.date))].sort(),
      grams: known.length ? Math.round(known.reduce((a, b) => a + b, 0) * 10) / 10 : null,
      fixings: [...new Set(fixings)],
      retired: /retired/i.test(p.notes) || /retired/i.test(p.status),
      order: uses[0] ? usage.indexOf(uses[0]) : usage.length,
    };
  });
  // Build order: first printed first; parts the log does not name last.
  return cards.sort((a, b) => a.order - b.order);
}

export type DayGroup<T> = { date: string; day: number; items: T[] };

/** Group dated rows by day, keeping their order, with a day count from the first date. */
export function groupByDate<T extends { date: string }>(rows: T[]): DayGroup<T>[] {
  const groups: DayGroup<T>[] = [];
  const first = rows[0]?.date;
  for (const row of rows) {
    const last = groups.at(-1);
    if (last && last.date === row.date) last.items.push(row);
    else groups.push({ date: row.date, day: first ? daysBetween(first, row.date) + 1 : 1, items: [row] });
  }
  return groups;
}

function daysBetween(a: string, b: string): number {
  return Math.round((Date.parse(`${b}T00:00:00Z`) - Date.parse(`${a}T00:00:00Z`)) / 86_400_000);
}

/** BOM groups in first-appearance order, with counts. */
export function bomGroups(bom: BuildData["bom"]): { group: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const row of bom) counts.set(row.group, (counts.get(row.group) ?? 0) + 1);
  return [...counts].map(([group, count]) => ({ group, count }));
}

/** "0,1" or "0 1" to [0, 1]: MDX blocks JS expressions, so list props arrive as strings. */
export function parseNumberList(text: string | undefined): number[] {
  return (text ?? "")
    .split(/[\s,]+/)
    .filter(Boolean)
    .map(Number)
    .filter(Number.isFinite);
}

/** A value from the build data by dotted path ("tire.bore_mm", "cradle.window.0"). Throws when missing. */
export function lookup(d: BuildData, path: string): number | string {
  let cur: unknown = d;
  for (const key of path.split(".")) {
    if (cur === null || typeof cur !== "object" || !(key in cur)) {
      throw new Error(`<Val k="${path}">: "${key}" is not in the build data for ${d.slug}`);
    }
    cur = (cur as Record<string, unknown>)[key];
  }
  if (typeof cur !== "number" && typeof cur !== "string") {
    throw new Error(`<Val k="${path}">: not a number or text in the build data for ${d.slug}`);
  }
  return cur;
}

/** Unit implied by a field name's suffix. */
export function unitFor(path: string): string {
  if (path.endsWith("_mm")) return "mm";
  if (path.endsWith("_kg")) return "kg";
  if (path.endsWith("_g")) return "g";
  return "";
}
