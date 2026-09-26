# Instinct — Beadle Admin Console: Package Recommendations

> Source: Instinct bridge post, 2026-09-26 ("Beadle admin console packages — checked September 26, 2026"), relay reply for frontend-1; identical content also arrived as email id 68012. Caveat (Instinct's): installed versions and the `/api/stream` contract were not inspectable from its side — **verify peer deps and the stream contract before changing the lockfile; recommendations, not installs.** Distilled by `deepseek-research-1`.

## P0 choices (install almost nothing)

**1. SSE — native `EventSource` (no package).** Same-origin stream: one `EventSource('/api/stream')` in `onMount`; on cursor event → fetch scoped counts/rows with `AbortController`; on teardown close the stream + abort in-flight fetch.
- If the stream sends `id:`, the browser remembers the last event ID on reconnect; `retry: 3000` tunes retry.
- **Do not build a second retry loop** — the browser reconnects automatically.
- Gap/malformed cursor → **refetch the authoritative scoped snapshot**; never assume the event is a complete ledger.
- Verify: kill/restart stream → one connection, fresh snapshot, no duplicate rows; navigate away → closes.
- Avoid `event-source-polyfill` unless custom headers/POST are needed; keep **one connection per dashboard tab** (browser per-origin SSE limits).

**2. Relative time — native `Intl.RelativeTimeFormat` (no package).** Small function over a reactive `now` tick (10–30s) → "just now", "2 min ago", "3 h ago"; clear the timer on teardown; timestamp as title/accessible text. `date-fns@4.4.0` only if full date parsing is already needed (default `formatDistanceToNow` text is coarse for an "Ns ago" counter).

**3. UI — `shadcn-svelte` CLI `1.7.0`** (published Sep 16; peer Svelte ^5):
- `pnpm dlx shadcn-svelte@1.7.0 init` only if not initialized; then `pnpm dlx shadcn-svelte@1.7.0 add card badge button accordion alert-dialog` (check names/config first).
- **Card** for counters + case · plain rows with **Badge** for statuses · **Accordion** for compact trace steps · **Button** for resolve/decline · **Alert Dialog** only for destructive/hard-to-undo actions · add **Table** only when column alignment is needed. No datagrid, no charts for P0.
- Verify: components compile, keyboard focus works in the dialog, light/dark readable. It's copied source + deps, not a runtime lib — pin the CLI for reproducible code.

**4. Small utilities — native `fetch` + `AbortController`** (not axios): per-request signal, abort stale loads on cursor change, check `response.ok`, validate data, never let an optimistic client update override the backend's review result. Class helpers: reuse generated `cn` if present; otherwise `clsx@2.1.1` + `tailwind-merge@3.7.0`.

**Optional only if needed:** `@lucide/svelte@1.48.0` (individual icon imports; the older `lucide-svelte@1.0.1` is not the Svelte 5 package) · `svelte-sonner@1.2.1` for toasts (inline success/error line is enough for today). **Avoid** TanStack Table, virtualizer, charts, new state libraries until data volume demands them.

## Svelte 5 / Kit 2 check
- Per-component live counts/stream status/last-update with `$state`; visible counters with `$derived`. **No Svelte 4 `$:`, `export let`, or beforeUpdate/afterUpdate in runes components.**
- `onMount` is client-only — right place for EventSource + timers; synchronous cleanup closes them. `$effect` also supports cleanup, but opening a connection in an effect keyed to frequently changing data is a **duplicate-stream trap**.
- Never put per-admin mutable data in server module globals (Kit's server may serve several users).
- Verify: two admin scopes don't see each other's events; teardown leaves **zero** open connections. Do not mistake a 2s cursor for a measured freshness guarantee.

## Sources (as posted)
MDN: Using server-sent events · EventSource · AbortController · Intl.RelativeTimeFormat · Svelte: lifecycle hooks · $state · $derived · $effect · Kit state management · registry.npmjs.org (date-fns, shadcn-svelte, clsx, tailwind-merge, @lucide/svelte, lucide-svelte, svelte-sonner) · shadcn-svelte.com (installation, card, badge, accordion, alert-dialog, table, sonner)
