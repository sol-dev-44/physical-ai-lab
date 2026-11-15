import { Badge, type Tone } from "./badge";

type Status = "planned" | "running" | "done" | "abandoned" | "building" | "working" | "retired";

const map: Record<Status, { tone: Tone; label: string; pulse?: boolean }> = {
  planned: { tone: "info", label: "Planned" },
  running: { tone: "accent", label: "Running", pulse: true },
  done: { tone: "ok", label: "Done" },
  abandoned: { tone: "neutral", label: "Abandoned" },
  building: { tone: "accent", label: "Building", pulse: true },
  working: { tone: "ok", label: "Working" },
  retired: { tone: "neutral", label: "Retired" },
};

export function StatusBadge({ status }: { status: Status }) {
  const s = map[status];
  return (
    <Badge tone={s.tone} pulse={s.pulse}>
      {s.label}
    </Badge>
  );
}
