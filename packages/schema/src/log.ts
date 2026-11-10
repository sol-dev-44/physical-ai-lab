/**
 * Log-level rules. A log is valid only if every line is a valid Event AND:
 *  1. all events share one run_id
 *  2. seq starts at 0 and increases by exactly 1
 *  3. the first event is run.started; nothing follows run.ended
 *  4. event_id is unique
 *  5. parent_id, when set, refers to an earlier event in the same log
 *
 * Python (lab_agent.log) and Rust (labctl) implement the same rules and are
 * tested against the same fixtures in fixtures/logs.
 */
import { Event } from "./event";

export type LogIssue = { line: number; message: string };

export function validateLog(lines: string[]): LogIssue[] {
  const issues: LogIssue[] = [];
  const seen = new Set<string>();
  let runId: string | undefined;
  let ended = false;
  let expectedSeq = 0;

  lines.forEach((raw, i) => {
    const line = i + 1;
    if (raw.trim() === "") return;
    let json: unknown;
    try {
      json = JSON.parse(raw);
    } catch {
      issues.push({ line, message: "not valid JSON" });
      return;
    }
    const parsed = Event.safeParse(json);
    if (!parsed.success) {
      issues.push({ line, message: parsed.error.issues.map((x) => `${x.path.join(".")}: ${x.message}`).join("; ") });
      return;
    }
    const e = parsed.data;
    if (expectedSeq === 0 && e.type !== "run.started") issues.push({ line, message: "first event must be run.started" });
    if (ended) issues.push({ line, message: "event after run.ended" });
    runId ??= e.run_id;
    if (e.run_id !== runId) issues.push({ line, message: `run_id ${e.run_id} != ${runId}` });
    if (e.seq !== expectedSeq) issues.push({ line, message: `seq ${e.seq}, expected ${expectedSeq}` });
    if (seen.has(e.event_id)) issues.push({ line, message: `duplicate event_id ${e.event_id}` });
    if (e.parent_id && !seen.has(e.parent_id)) issues.push({ line, message: `parent_id ${e.parent_id} not found earlier in log` });
    seen.add(e.event_id);
    expectedSeq = e.seq + 1;
    if (e.type === "run.ended") ended = true;
  });

  if (seen.size === 0) issues.push({ line: 0, message: "log is empty" });
  return issues;
}
