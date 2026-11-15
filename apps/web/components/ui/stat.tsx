/** One headline number with a label. Numbers come from the write-ups, never invented here. */
export function Stat({ value, label, note }: { value: string; label: string; note?: string }) {
  return (
    <div className="border-l border-line-strong pl-4">
      <p className="font-mono text-2xl font-semibold tracking-tight tabular-nums sm:text-3xl">{value}</p>
      <p className="mt-1 text-sm text-fg">{label}</p>
      {note ? <p className="mt-0.5 text-xs text-subtle">{note}</p> : null}
    </div>
  );
}
