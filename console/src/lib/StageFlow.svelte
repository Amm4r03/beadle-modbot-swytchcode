<script lang="ts">
	import type { Metrics } from '$lib/api';

	// Hand-rolled Sankey-style flow: stage nodes on the left, band outcomes on
	// the right, band widths proportional to live counts. No chart library.
	let { metrics }: { metrics: Metrics | null } = $props();

	const STAGES = [
		'received',
		'signals_ready',
		'decided',
		'approval_pending',
		'action_pending'
	] as const;

	const counts = $derived(() => {
		const m: Record<string, number> = {};
		for (const t of metrics?.transitions ?? []) m[t.to_state] = t.n;
		return m;
	});
	const bands = $derived(() => {
		const m: Record<string, number> = {};
		for (const b of metrics?.bands ?? []) m[b.band] = b.n;
		return m;
	});
	const total = $derived(() => Math.max(1, metrics?.totals.decisions ?? 1));
	const bandColor = (b: string) =>
		b === 'AUTO' ? 'var(--chart-2)' : b === 'DRAFT' ? 'var(--chart-3)' : 'var(--chart-5)';
</script>

<section aria-label="Stage flow" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Stage flow</h2>
	{#if !metrics}
		<p class="text-sm text-muted-foreground">Loading flow…</p>
	{:else}
		<svg viewBox="0 0 560 220" class="w-full" role="img" aria-label="Stage to outcome flow">
			{#each STAGES as stage, i (stage)}
				{@const n = counts()[stage] ?? 0}
				{@const y = 14 + i * 40}
				{@const w = 90 + (190 * n) / total()}
				<rect
					x="8"
					{y}
					width={w}
					height="26"
					rx="6"
					fill="none"
					stroke="currentColor"
					opacity="0.35"
				/>
				<text x="18" y={y + 17} font-size="12" fill="currentColor">
					{stage} · {n}
				</text>
				{#if i < STAGES.length - 1}
					<line
						x1={8 + w}
						y1={y + 13}
						x2="330"
						y2={14 + (i + 1) * 40 + 13}
						stroke="currentColor"
						opacity="0.2"
					/>
				{/if}
			{/each}
			{#each ['AUTO', 'DRAFT', 'DENY'] as band, j (band)}
				{@const n = bands()[band] ?? 0}
				{@const h = 14 + (120 * n) / total()}
				<rect
					x="360"
					y={30 + j * 62}
					width={150 - j * 18}
					height={Math.max(18, h)}
					rx="6"
					fill={bandColor(band)}
					opacity="0.25"
					stroke="currentColor"
				/>
				<text x="370" y={30 + j * 62 + 20} font-size="12" fill="currentColor">
					{band} · {n}
				</text>
			{/each}
			<line x1="310" y1="60" x2="360" y2="45" stroke="currentColor" opacity="0.2" />
			<line x1="310" y1="100" x2="360" y2="105" stroke="currentColor" opacity="0.2" />
		</svg>
		<p class="text-xs text-muted-foreground tabular-nums">
			{metrics.totals.transitions} transitions · {metrics.totals.decisions} decisions · widths scaled
			to live counts
		</p>
	{/if}
</section>
