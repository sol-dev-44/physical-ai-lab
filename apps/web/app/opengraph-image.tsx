import { readFile } from "node:fs/promises";
import path from "node:path";
import { ImageResponse } from "next/og";
import { site } from "@/lib/site";

export const alt = `${site.name}: ${site.tagline}`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

// The image is rendered at build time. Fonts come from the geist package already used by the site.
const fonts = path.join(/*turbopackIgnore: true*/ process.cwd(), "node_modules/geist/dist/fonts");

// Literal colors: the image renderer can't read CSS variables. These match the light tokens.
const c = { bg: "#f7f6f2", fg: "#16161a", muted: "#55555e", line: "#cbc8bd", accent: "#c2410c", ok: "#11703a", danger: "#b42318" };

const lines: [string, string, string][] = [
  ["command.requested", "robot.forward", c.muted],
  ["safety.checked", "allowed", c.ok],
  ["command.sent", "78 ms", c.accent],
  ["safety.checked", "denied · requires_confirmation", c.danger],
];

// Read once at module load, as in the Next docs, so the route stays static (built once, then served).
const [sans, mono] = await Promise.all([
  readFile(path.join(fonts, "geist-sans/Geist-SemiBold.ttf")),
  readFile(path.join(fonts, "geist-mono/GeistMono-Regular.ttf")),
]);

export default function Image() {
  return new ImageResponse(
    (
      <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", background: c.bg, padding: 72, fontFamily: "Geist" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 44, height: 44, borderRadius: 10, background: c.accent }}>
            <div style={{ width: 16, height: 16, borderRadius: 8, background: "#ffffff" }} />
          </div>
          <div style={{ fontSize: 34, color: c.fg }}>{site.name}</div>
        </div>
        <div style={{ display: "flex", marginTop: 64, fontSize: 82, lineHeight: 1.04, letterSpacing: -3, color: c.fg, maxWidth: 980 }}>
          {site.tagline}
        </div>
        <div style={{ display: "flex", flexDirection: "column", marginTop: "auto", borderTop: `2px solid ${c.line}`, paddingTop: 28, gap: 10, fontFamily: "Geist Mono", fontSize: 24 }}>
          {lines.map(([type, detail, color]) => (
            <div key={type + detail} style={{ display: "flex", gap: 28 }}>
              <div style={{ display: "flex", width: 300, color: c.fg }}>{type}</div>
              <div style={{ display: "flex", color }}>{detail}</div>
            </div>
          ))}
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [
        { name: "Geist", data: sans, style: "normal", weight: 600 },
        { name: "Geist Mono", data: mono, style: "normal", weight: 400 },
      ],
    },
  );
}
