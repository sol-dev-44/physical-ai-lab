import "server-only";

import { readFile } from "node:fs/promises";
import path from "node:path";
import { ImageResponse } from "next/og";
import type { ReactNode } from "react";
import { site } from "./site";

/** Share-card renderer for every Open Graph image on the site (1200x630, light theme). */
export const ogSize = { width: 1200, height: 630 };

const fonts = path.join(/*turbopackIgnore: true*/ process.cwd(), "node_modules/geist/dist/fonts");
// Read once at module load so image routes stay static.
const [sans, mono] = await Promise.all([
  readFile(path.join(fonts, "geist-sans/Geist-SemiBold.ttf")),
  readFile(path.join(fonts, "geist-mono/GeistMono-Regular.ttf")),
]);

// Literal colors: the image renderer can't read CSS variables. These match the light tokens.
export const og = {
  bg: "#f7f6f2",
  fg: "#16161a",
  muted: "#55555e",
  line: "#cbc8bd",
  accent: "#c2410c",
  ok: "#11703a",
  danger: "#b42318",
} as const;

export function renderCard({ eyebrow, title, footer }: { eyebrow?: string; title: string; footer?: ReactNode }) {
  return new ImageResponse(
    (
      <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", background: og.bg, padding: 72, fontFamily: "Geist" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 44, height: 44, borderRadius: 10, background: og.accent }}>
            <div style={{ width: 16, height: 16, borderRadius: 8, background: "#ffffff" }} />
          </div>
          <div style={{ fontSize: 34, color: og.fg }}>{site.name}</div>
        </div>
        {eyebrow ? (
          <div style={{ display: "flex", marginTop: 56, fontFamily: "Geist Mono", fontSize: 24, letterSpacing: 3, color: og.accent, textTransform: "uppercase" }}>
            {eyebrow}
          </div>
        ) : null}
        <div
          style={{
            display: "flex",
            marginTop: eyebrow ? 18 : 64,
            fontSize: title.length > 60 ? 64 : 82,
            lineHeight: 1.05,
            letterSpacing: -2.5,
            color: og.fg,
            maxWidth: 1040,
          }}
        >
          {title}
        </div>
        {footer ? (
          <div style={{ display: "flex", flexDirection: "column", marginTop: "auto", borderTop: `2px solid ${og.line}`, paddingTop: 28, gap: 10, fontFamily: "Geist Mono", fontSize: 24, color: og.muted }}>
            {footer}
          </div>
        ) : null}
      </div>
    ),
    {
      ...ogSize,
      fonts: [
        { name: "Geist", data: sans, style: "normal", weight: 600 },
        { name: "Geist Mono", data: mono, style: "normal", weight: 400 },
      ],
    },
  );
}
