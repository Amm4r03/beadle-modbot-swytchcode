<script lang="ts">
	import StatusChip from '$lib/StatusChip.svelte';
	import { timeAgo } from '$lib/format';
	import type { EventRow, Trace } from '$lib/api';

	let { events, traces, now }: { events: EventRow[]; traces: Record<string, Trace>; now: number } =
		$props();

	const rows = $derived(
		events.map((e) => {
			const t = traces[e.event_id];
			const d = t?.decisions?.[0];
			const sigs = (t?.signals ?? [])
				.map((s) => s.signal_version.split('@')[0])
				.filter((n) => !n.includes('jev'))
				.filter((n, i, a) => a.indexOf(n) === i)
				.slice(0, 4);
			return { e, d, sigs, action: t?.actions?.[0]?.action_type ?? null };
		})
	);
</script>

<section aria-label="Recent executions" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Execution log</h2>
	{#if rows.length === 0}
		<p class="text-sm text-muted-foreground">No executions yet.</p>
	{:else}
		<ol class="flex flex-col gap-2">
			{#each rows as r (r.e.event_id)}
				<li class="rounded-xl border px-4 py-3">
					<div class="flex flex-wrap items-center gap-2">
						<a href="#event-{r.e.event_id}" class="font-mono text-xs underline underline-offset-2">
							{r.e.event_id}
						</a>
						<StatusChip band={r.d?.band ?? r.e.band} verdict={r.d?.verdict ?? r.e.verdict} />
						<span class="text-xs text-muted-foreground tabular-nums" title={r.e.received_at}>
							{timeAgo(r.e.received_at, now)}
						</span>
					</div>
					<p class="mt-1 truncate text-sm">{r.e.text ?? '(no text)'}</p>
					<p class="mt-1 text-xs text-muted-foreground">
						signals: {r.sigs.length > 0 ? r.sigs.join(', ') : '—'}
						→ decision: {r.d
							? `${r.d.band ?? '?'}:${r.d.verdict ?? '?'}@${r.d.confidence === null ? '?' : r.d.confidence.toFixed(2)}`
							: '—'}
						→ action: {r.action ?? '—'}
					</p>
				</li>
			{/each}
		</ol>
	{/if}
</section>
