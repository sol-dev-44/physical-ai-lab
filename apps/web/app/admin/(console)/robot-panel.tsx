"use client";

import { useActionState, useState } from "react";
import type { ToolRow } from "@/lib/data/commands";
import { requestCommand } from "./actions";

const MOVES = [
  { tool: "robot.forward", label: "Forward" },
  { tool: "robot.reverse", label: "Reverse", hint: "backs up and turns left" },
] as const;

// The agent's safety gate caps holds at 3 s (exp000 Hold model); this only shapes the slider.
const MAX_SECONDS = 3;

/**
 * One-tap controls for the exp000 toy robot. Same path as the command form: each tap
 * queues a row, the lab-agent at home claims it and runs the safety gate.
 */
export function RobotPanel({ tools }: { tools: ToolRow[] }) {
  const [state, action, pending] = useActionState(requestCommand, null);
  const [seconds, setSeconds] = useState(1);
  const available = MOVES.filter((m) => tools.some((t) => t.name === m.tool));
  if (available.length === 0) return null;

  return (
    <section aria-labelledby="robot-heading" className="rounded border border-line p-4">
      <h2 id="robot-heading" className="mb-3 text-lg font-semibold">
        Wall-e Robot
      </h2>
      <form action={action} className="space-y-4 text-sm">
        <input type="hidden" name="args" value={JSON.stringify({ seconds })} />
        <label className="flex items-center gap-3">
          <span className="w-16 shrink-0">Drive for</span>
          <input
            type="range"
            min={0.5}
            max={MAX_SECONDS}
            step={0.5}
            value={seconds}
            onChange={(e) => setSeconds(Number(e.target.value))}
            className="flex-1"
            aria-valuetext={`${seconds} seconds`}
          />
          <span className="w-10 text-right font-mono">{seconds} s</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {available.map((m) => (
            <button
              key={m.tool}
              type="submit"
              name="tool"
              value={m.tool}
              disabled={pending}
              className="rounded border border-line px-3 py-4 text-base font-medium disabled:opacity-50"
            >
              {m.label}
              {"hint" in m ? <span className="block text-xs font-normal text-muted">{m.hint}</span> : null}
            </button>
          ))}
        </div>
        <p className="text-xs text-muted" aria-live="polite">
          {pending ? "Queuing…" : state ? state.message : "Runs when the lab-agent on the Mac picks it up."}
        </p>
      </form>
    </section>
  );
}
