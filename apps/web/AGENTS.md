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
- Share images (`opengraph-image.tsx`) go through `lib/og.tsx`. Reading files inside the handler
  counts as uncached data and makes the route dynamic (ƒ); read fonts at module load instead, and give
  `[slug]` image routes their own `generateStaticParams`. Check the build output shows ○ or ●.
- `export const dynamicParams` (and other route segment configs) fail the build under Cache Components.
- Above-the-fold animation is CSS (see `animate-log-line`), so it paints before hydration. A `motion`
  animation that starts at `opacity: 0` stays invisible until JavaScript runs.
- The admin console needs a real Supabase sign-in, so local checks cannot reach it.
  Test its data layer with mocks (`test/admin-data.test.ts`).

## Design system

- Colors are semantic tokens only (`bg-surface`, `text-muted`, `border-line`, `text-accent`,
  `bg-ok-soft`...), defined in `app/globals.css` with light and dark values. The default Tailwind
  palette is switched off (`--color-*: initial`), so `text-red-600` does nothing: use `text-danger`.
- Type, widths, radii and easing are tokens too: `text-display`, `text-title`, `max-w-page`,
  `max-w-prose`, `rounded-card`, `rounded-control`, `ease-out-quint`, `duration-base`.
- Reuse `components/ui/*` (Container, Badge, StatusBadge, Eyebrow, SectionHeading, ButtonLink, Stat)
  before writing new markup. Join classes with `cn` from `lib/design/cn.ts`.
- Animation uses `motion` (the framer-motion successor) through `LazyMotion`: import `m` from
  `motion/react`, never `motion.div`, or the full bundle ships. Timings come from `lib/design/motion.ts`.
  CSS transitions for hover and focus; `motion` for enter, reveal and layout animation.
- `Reveal`/`RevealList` only below the fold. The hero and a page's main text render without it so
  they paint immediately. `MotionConfig reducedMotion="user"` already honors reduced motion.
- Tap targets are at least 44px (`min-h-11`). Check new pages at 375px wide and in dark mode.
- Long-form MDX uses `prose prose-lab` (tokens mapped onto the typography plugin).
