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
  outputFileTracingIncludes: { "/**": ["../../content/**/*"] },
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
