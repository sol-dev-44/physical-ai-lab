"use client";

import { useActionState } from "react";
import type { ToolRow } from "@/lib/data/commands";
import { requestCommand } from "./actions";

export function CommandForm({ tools }: { tools: ToolRow[] }) {
  const [state, action, pending] = useActionState(requestCommand, null);
  if (tools.length === 0) {
    return <p className="text-sm text-muted">No tools registered. Start the lab-agent to register its tools.</p>;
  }
  return (
    <form action={action} className="space-y-3 text-sm">
      <div className="flex flex-wrap gap-2">
        <select name="tool" className="rounded border border-line bg-transparent px-2 py-2">
          {tools.map((t) => (
            <option key={t.name} value={t.name}>
              {t.name}
              {t.requires_confirmation ? " (confirm)" : ""}
            </option>
          ))}
        </select>
        <input
          name="args"
          defaultValue="{}"
          className="flex-1 rounded border border-line bg-transparent px-3 py-2 font-mono"
          aria-label="args as JSON"
        />
      </div>
      <label className="flex items-center gap-2">
        <input type="checkbox" name="confirmed" /> I confirm (required for tools marked confirm)
      </label>
      <button type="submit" disabled={pending} className="rounded border border-line px-3 py-2">
        {pending ? "Queuing…" : "Queue command"}
      </button>
      {state ? <p className={state.ok ? "" : "text-red-600"}>{state.message}</p> : null}
    </form>
  );
}
