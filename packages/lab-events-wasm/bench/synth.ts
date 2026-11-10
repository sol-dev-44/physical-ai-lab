/**
 * Deterministic synthetic logs for benchmarks: realistic command cycles
 * (requested -> safety.checked -> sent/failed -> outcome), with denials,
 * failures and notes, so every branch of the fold runs.
 */
const ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
const ulid = (n: number) => {
  let s = "";
  for (let i = 0; i < 26; i++) {
    s = ALPHABET[n % 32] + s;
    n = Math.floor(n / 32);
  }
  return s;
};
const TOOLS = ["fan.power", "fan.speed", "tv.power", "robot.forward", "fireplace.power"];

export function synthLog(target: number): string {
  const runId = "exp000-bench-r1";
  const t0 = Date.UTC(2026, 10, 10, 20);
  const lines: string[] = [];
  let seq = 0;
  const add = (e: Record<string, unknown>) => {
    const id = ulid(1_000_000_000 + seq);
    lines.push(
      JSON.stringify({
        v: 0,
        event_id: id,
        run_id: runId,
        seq,
        ts: new Date(t0 + seq * 250).toISOString(),
        ...e,
      }),
    );
    seq++;
    return id;
  };
  add({ actor: "cli", type: "run.started", payload: { experiment_id: "exp000-ir-bridge", git_sha: "abc1234" } });
  for (let i = 0; lines.length < target - 1; i++) {
    const tool = TOOLS[i % TOOLS.length]!;
    const args = tool === "robot.forward" ? { seconds: 1 } : {};
    const req = add({ actor: "cli", type: "command.requested", tool, args, device: "rm4", payload: {} });
    const deny = tool === "fireplace.power";
    const chk = add({
      actor: "system", type: "safety.checked", tool, args, parent_id: req,
      payload: deny ? { decision: "deny", rule: "manual_only", reason: "manual only" } : { decision: "allow", rule: "allow" },
    });
    if (deny) continue;
    if (i % 17 === 0) {
      add({ actor: "system", type: "command.failed", tool, args, parent_id: chk, payload: { error: "device timeout" } });
      continue;
    }
    const sent = add({ actor: "system", type: "command.sent", tool, args, device: "rm4", parent_id: chk, payload: { latency_ms: 40 + (i % 50) } });
    add({ actor: "human", type: "outcome.observed", tool, parent_id: sent, payload: { success: i % 10 !== 0, method: "human" } });
    if (i % 50 === 0) add({ actor: "human", type: "note", payload: { text: `checkpoint ${i}` } });
  }
  add({ actor: "cli", type: "run.ended", payload: { status: "completed" } });
  return lines.join("\n") + "\n";
}
