import { Suspense } from "react";
import { requireAdmin } from "@/lib/auth";
import { listRecentCommands, listTools } from "@/lib/data/commands";
import { listRunsForAdmin } from "@/lib/data/runs";
import { setRunPublished } from "./actions";
import { CommandForm } from "./command-form";
import { RobotPanel } from "./robot-panel";
import { control } from "@/lib/design/controls";

// Every admin page: a static shell, with the session read inside a Suspense boundary.
export default function AdminHome() {
  return (
    <Suspense fallback={<p className="text-sm text-muted">Checking access…</p>}>
      <Console />
    </Suspense>
  );
}

async function Console() {
  const admin = await requireAdmin();
  const [runs, tools, commands] = await Promise.all([listRunsForAdmin(), listTools(), listRecentCommands()]);

  return (
    <div className="space-y-10">
      <p className="text-sm text-muted">Signed in as {admin.email}</p>

      <RobotPanel tools={tools} />

      <section>
        <h2 className="mb-3 text-lg font-semibold">Command console</h2>
        <CommandForm tools={tools} />
        {commands.length ? (
          // Scrolls inside its own box on a phone instead of widening the page.
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-muted">
                  <th className="py-1 pr-3 font-normal">Tool</th>
                  <th className="py-1 pr-3 font-normal">Args</th>
                  <th className="py-1 pr-3 font-normal">Status</th>
                  <th className="py-1 pr-3 font-normal">Result</th>
                  <th className="py-1 text-right font-normal">Queued</th>
                </tr>
              </thead>
              <tbody>
                {commands.map((c) => (
                  <tr key={c.id} className="border-t border-line">
                    <td className="py-1 pr-3 font-mono whitespace-nowrap">{c.tool}</td>
                    <td className="py-1 pr-3 font-mono text-muted">{JSON.stringify(c.args)}</td>
                    <td className="py-1 pr-3">{c.status}</td>
                    <td className="py-1 pr-3 text-muted">{c.result}</td>
                    <td className="py-1 text-right whitespace-nowrap text-muted">
                      <time dateTime={c.created_at}>{new Date(c.created_at).toLocaleString()}</time>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Runs</h2>
        {runs.length === 0 ? (
          <p className="text-sm text-muted">No runs synced yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-muted">
                  <th className="py-1 pr-3 font-normal">Run</th>
                  <th className="py-1 pr-3 font-normal">Experiment</th>
                  <th className="py-1 pr-3 font-normal">Status</th>
                  <th className="py-1 text-right font-normal">
                    <span className="sr-only">Publish</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.run_id} className="border-t border-line">
                    <td className="py-1 pr-3 font-mono whitespace-nowrap">{r.run_id}</td>
                    <td className="py-1 pr-3">{r.experiment_id}</td>
                    <td className="py-1 pr-3">{r.status}</td>
                    <td className="py-1 text-right">
                      <form action={setRunPublished}>
                        <input type="hidden" name="run_id" value={r.run_id} />
                        <input type="hidden" name="published" value={String(!r.published)} />
                        <button type="submit" className={control.textLink} aria-label={`${r.published ? "Unpublish" : "Publish"} ${r.run_id}`}>
                          {r.published ? "Unpublish" : "Publish"}
                        </button>
                      </form>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
