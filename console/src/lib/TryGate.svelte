<script lang="ts">
	import { ingestMessage, type IngestResult } from '$lib/api';
	import { Button } from '$lib/components/ui/button/index.js';
	import StatusChip from '$lib/StatusChip.svelte';

	let { onIngested }: { onIngested: () => void } = $props();

	let text = $state('');
	let busy = $state(false);
	let result = $state<IngestResult | null>(null);
	let error = $state<string | null>(null);

	async function send(e: Event) {
		e.preventDefault();
		const msg = text.trim();
		if (!msg || busy) return;
		busy = true;
		error = null;
		result = null;
		try {
			result = await ingestMessage(msg);
			text = '';
			onIngested();
		} catch (err) {
			error = (err as Error).message;
		} finally {
			busy = false;
		}
	}
</script>

<section aria-label="Try the gate" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Try the gate</h2>
	<p class="text-sm text-muted-foreground">
		Runs the full agent live (observe → classify → gate → escalate/resolve → learn) with real Jev
		scores. Staged demo input is fine — the output is always a real ledger row.
	</p>
	<form class="flex gap-2" onsubmit={send}>
		<input
			class="min-w-0 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
			placeholder="Type a community message…"
			bind:value={text}
			disabled={busy}
			aria-label="Community message"
			maxlength="500"
		/>
		<Button type="submit" size="sm" disabled={busy || text.trim().length === 0}>
			{busy ? 'Running…' : 'Send'}
		</Button>
	</form>
	{#if error}
		<p role="alert" class="text-sm text-red-700">Ingest failed: {error}</p>
	{/if}
	{#if result}
		<div class="rounded-xl border px-4 py-3" role="status">
			<div class="flex flex-wrap items-center gap-2">
				<a href="#event-{result.event_id}" class="font-mono text-xs underline underline-offset-2">
					{result.event_id}
				</a>
				<StatusChip band={result.band} verdict={result.verdict} />
				<span class="text-xs text-muted-foreground tabular-nums">
					conf {result.confidence === null ? '—' : result.confidence.toFixed(2)}
				</span>
			</div>
			<p class="mt-1 text-sm">{result.reason ?? 'no reason recorded'}</p>
			<p class="mt-1 text-xs text-muted-foreground">
				{result.transitions.join(' → ')}
			</p>
		</div>
	{/if}
</section>
