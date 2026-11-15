<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

## Gotchas in this app

- Run the site from `apps/web` (`pnpm dev` from the root does this). `content/` and the
  replay sample are read relative to `process.cwd()`, so starting `next` from another
  directory 500s on `/harness/replay` and loses the write-ups.
- Vitest has no config here, so the `@/` alias does not resolve in tests. `vi.mock("@/...")`
  still works because it matches the specifier, but a module under test must import any
  unmocked local helper by relative path (see `lib/data/rows.ts`).
- Next 16 error boundaries get `{ error, retry }`, not `reset`. For a boundary around one
  component instead of a route segment, use `catchError` from `next/error`
  (see `components/run-boundary.tsx`).
- Supabase under RLS: a refused `update` returns zero rows and no error. Add
  `.select(...)` and treat an empty result as a failure (see `setRunPublished`).
- Admin reads throw on a Supabase error (`rowsOrThrow`) so the console shows the error
  boundary instead of an empty table that looks like "no data yet".
- Tailwind v4 `focus:not-sr-only` resets padding; add `focus:px-* focus:py-*` after it.
- The admin console needs a real Supabase sign-in, so local checks cannot reach it.
  Test its data layer with mocks (`test/admin-data.test.ts`).
