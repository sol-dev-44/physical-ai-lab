import path from "node:path";
import type { NextConfig } from "next";

const repoRoot = path.join(__dirname, "../..");

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // Internal workspace packages ship TypeScript source.
  transpilePackages: ["@lab/schema", "@lab/events-wasm"],
  // Content lives at the repo root, outside this app.
  outputFileTracingRoot: repoRoot,
  outputFileTracingIncludes: {
    "/**": [
      "../../content/**/*",
      // Fonts for the share images (lib/og.tsx), in case an image re-renders at runtime.
      "./node_modules/geist/dist/fonts/geist-sans/Geist-SemiBold.ttf",
      "./node_modules/geist/dist/fonts/geist-mono/GeistMono-Regular.ttf",
    ],
  },
  turbopack: {
    root: repoRoot,
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
