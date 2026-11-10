import { getPublishedRun } from "@/lib/data/runs";

const pct = (n: number | null) => (n === null ? "n/a" : `${Math.round(n * 100)}%`);

/** Results for one published run, computed from its events. Render inside <Suspense>. */
export async function RunResults({ runId }: { runId: string }) {
  const run = await getPublishedRun(runId);
  if (!run) {
    return (
      <p className="text-sm text-muted">
        Run <code>{runId}</code> is not published yet.
      </p>
    );
  }
  const s = run.summary;
  const rows: [string, string | number][] = [
    ["Status", s.status + (s.null_test ? " (null test)" : "")],
    ["Commands requested", s.requested],
    ["Denied by safety gate", s.denied],
    ["Sent", s.sent],
    ["Failed", s.failed],
    ["Outcomes observed", s.observed],
    ["Success rate", pct(s.success_rate)],
  ];
  return (
    <section className="rounded border border-line p-4">
      <h3 className="mb-2 font-mono text-sm">{runId}</h3>
      <table className="w-full text-sm">
        <tbody>
          {rows.map(([k, v]) => (
            <tr key={k} className="border-t border-line first:border-0">
              <td className="py-1 text-muted">{k}</td>
              <td className="py-1 text-right font-mono">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
