import { Suspense } from "react";
import { requireAdmin } from "@/lib/auth";
import { listRecentCommands, listTools } from "@/lib/data/commands";
import { listRunsForAdmin } from "@/lib/data/runs";
import { setRunPublished } from "./actions";
import { CommandForm } from "./command-form";

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

      <section>
        <h2 className="mb-3 text-lg font-semibold">Command console</h2>
        <CommandForm tools={tools} />
        {commands.length ? (
          <table className="mt-4 w-full text-sm">
            <tbody>
              {commands.map((c) => (
                <tr key={c.id} className="border-t border-line">
                  <td className="py-1 font-mono">{c.tool}</td>
                  <td className="py-1 font-mono text-muted">{JSON.stringify(c.args)}</td>
                  <td className="py-1">{c.status}</td>
                  <td className="py-1 text-muted">{c.result}</td>
                  <td className="py-1 text-right text-muted">{new Date(c.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Runs</h2>
        {runs.length === 0 ? (
          <p className="text-sm text-muted">No runs synced yet.</p>
        ) : (
          <table className="w-full text-sm">
            <tbody>
              {runs.map((r) => (
                <tr key={r.run_id} className="border-t border-line">
                  <td className="py-1 font-mono">{r.run_id}</td>
                  <td className="py-1">{r.experiment_id}</td>
                  <td className="py-1">{r.status}</td>
                  <td className="py-1 text-right">
                    <form action={setRunPublished}>
                      <input type="hidden" name="run_id" value={r.run_id} />
                      <input type="hidden" name="published" value={String(!r.published)} />
                      <button type="submit" className="underline">
                        {r.published ? "Unpublish" : "Publish"}
                      </button>
                    </form>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
