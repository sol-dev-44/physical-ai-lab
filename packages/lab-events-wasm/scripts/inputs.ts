/**
 * The Rust sources the committed WASM is built from. `generated/SOURCE_HASH`
 * records their hash at build time; the package test recomputes it, so CI
 * fails when Rust changes without `pnpm --filter @lab/events-wasm wasm`.
 * Checking a hash instead of rebuilding keeps the TypeScript job free of Rust.
 */
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

export const repoRoot = fileURLToPath(new URL("../../../", import.meta.url));
export const generatedDir = fileURLToPath(new URL("../generated/", import.meta.url));

const INPUTS = [
  "Cargo.toml",
  "Cargo.lock",
  "crates/lab-events/Cargo.toml",
  "crates/lab-events/src",
  "crates/lab-events-wasm/Cargo.toml",
  "crates/lab-events-wasm/src",
];

function walk(path: string): string[] {
  if (!statSync(path).isDirectory()) return [path];
  return readdirSync(path)
    .sort()
    .flatMap((name) => walk(join(path, name)));
}

export function sourceHash(): string {
  const h = createHash("sha256");
  for (const file of INPUTS.flatMap((p) => walk(join(repoRoot, p)))) {
    h.update(relative(repoRoot, file).replaceAll("\\", "/"));
    h.update("\0");
    // Normalize line endings so a Windows checkout hashes the same.
    h.update(readFileSync(file, "utf8").replaceAll("\r\n", "\n"));
    h.update("\0");
  }
  return h.digest("hex");
}
