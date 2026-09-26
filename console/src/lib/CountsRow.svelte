<script lang="ts">
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import type { Counts } from '$lib/api';

	let { counts }: { counts: Counts | null } = $props();

	const cards = $derived([
		{ key: 'observed', label: 'Observed', value: counts?.observed ?? null, href: '#events' },
		{
			key: 'gated',
			label: 'Gated',
			value: counts ? Object.values(counts.by_band).reduce((a, b) => a + b, 0) : null,
			href: '#events'
		},
		{
			key: 'quarantined',
			label: 'Quarantined',
			value: counts?.quarantined ?? null,
			href: '#queue'
		},
		{ key: 'resolved', label: 'Resolved', value: counts?.resolved ?? null, href: '#events' }
	]);
</script>

<div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
	{#each cards as card (card.key)}
		<a {...{ href: card.href }} class="block rounded-xl">
			<Card>
				<CardHeader>
					<CardTitle>{card.label}</CardTitle>
				</CardHeader>
				<CardContent>
					{#if card.value === null}
						<p class="text-sm text-muted-foreground">loading…</p>
					{:else}
						<p class="text-3xl font-semibold tabular-nums">{card.value}</p>
					{/if}
				</CardContent>
			</Card>
		</a>
	{/each}
</div>
