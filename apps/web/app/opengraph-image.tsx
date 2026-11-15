import { og, ogSize, renderCard } from "@/lib/og";
import { site } from "@/lib/site";

export const alt = `${site.name}: ${site.tagline}`;
export const size = ogSize;
export const contentType = "image/png";

const lines: [string, string, string][] = [
  ["command.requested", "robot.forward", og.muted],
  ["safety.checked", "allowed", og.ok],
  ["command.sent", "78 ms", og.accent],
  ["safety.checked", "denied · requires_confirmation", og.danger],
];

export default function Image() {
  return renderCard({
    title: site.tagline,
    footer: lines.map(([type, detail, color]) => (
      <div key={type + detail} style={{ display: "flex", gap: 28 }}>
        <div style={{ display: "flex", width: 300, color: og.fg }}>{type}</div>
        <div style={{ display: "flex", color }}>{detail}</div>
      </div>
    )),
  });
}
