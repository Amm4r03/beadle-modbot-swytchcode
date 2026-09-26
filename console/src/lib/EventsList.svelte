<script lang="ts">
	import StatusChip from '$lib/StatusChip.svelte';
	import { ageMinutes } from '$lib/format';
	import type { EventRow } from '$lib/api';

	let {
		events,
		now,
		emptyLabel = 'No events yet.'
	}: {
		events: EventRow[] | null;
		now: number;
		emptyLabel?: string;
	} = $props();
</script>

<section id="events" aria-label="Recent events">
	{#if events === null}
		<p class="text-sm text-muted-foreground">Loading events…</p>
	{:else if events.length === 0}
		<p class="text-sm text-muted-foreground">{emptyLabel}</p>
	{:else}
		<ul class="divide-y divide-border rounded-xl border">
			{#each events as ev (ev.event_id)}
				<li>
					<a
						href="#event-{ev.event_id}"
						class="flex items-baseline gap-3 px-4 py-3 transition-colors hover:bg-muted/50"
					>
						<span class="min-w-0 flex-1">
							<span class="block truncate text-sm">
								{ev.text ?? '(no text recorded)'}
							</span>
							<span class="block text-xs text-muted-foreground tabular-nums">
								{ev.event_id} · {ev.author_id ?? 'unknown'} · {ageMinutes(ev.received_at, now)} old
							</span>
						</span>
						<StatusChip band={ev.band} verdict={ev.verdict} />
					</a>
				</li>
			{/each}
		</ul>
	{/if}
</section>
