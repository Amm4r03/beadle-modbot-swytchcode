<script lang="ts">
	import { addKnowledge, fetchKnowledge, type KnowledgeDoc } from '$lib/api';
	import { Button } from '$lib/components/ui/button/index.js';
	import type { Metrics } from '$lib/api';

	let { metrics, refreshKey }: { metrics: Metrics | null; refreshKey: number } = $props();

	let docs = $state<KnowledgeDoc[] | null>(null);
	let title = $state('');
	let text = $state('');
	let busy = $state(false);
	let notice = $state<string | null>(null);

	async function load() {
		try {
			docs = await fetchKnowledge();
		} catch {
			docs = null;
		}
	}

	$effect(() => {
		void refreshKey;
		void load();
	});

	async function add(e: Event) {
		e.preventDefault();
		if (!title.trim() || !text.trim() || busy) return;
		busy = true;
		notice = null;
		try {
			const r = await addKnowledge(title.trim(), text.trim());
			notice = `Saved ${r.doc_id} — ${r.docs} docs total.`;
			title = '';
			text = '';
			await load();
		} catch (err) {
			notice = `Save failed: ${(err as Error).message}`;
		} finally {
			busy = false;
		}
	}
</script>

<section aria-label="Knowledge" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Knowledge</h2>
	<p class="text-sm text-muted-foreground tabular-nums">
		{#if docs === null}
			Loading docs…
		{:else}
			{docs.length} approved docs · FTS5 baseline, scoped to this community
		{/if}
	</p>
	{#if metrics?.knowledge}
		{@const k = metrics.knowledge}
		<dl class="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
			<div class="rounded-xl border px-3 py-2">
				<dt class="text-xs text-muted-foreground">Docs</dt>
				<dd class="font-semibold tabular-nums">{k.docs}</dd>
			</div>
			<div class="rounded-xl border px-3 py-2">
				<dt class="text-xs text-muted-foreground">Retrievals</dt>
				<dd class="font-semibold tabular-nums">{k.retrievals}</dd>
			</div>
			<div class="rounded-xl border px-3 py-2">
				<dt class="text-xs text-muted-foreground">Drafts attempted</dt>
				<dd class="font-semibold tabular-nums">{k.drafts_attempted}</dd>
			</div>
			<div class="rounded-xl border px-3 py-2">
				<dt class="text-xs text-muted-foreground">Citation coverage</dt>
				<dd class="font-semibold tabular-nums">
					{k.drafts_attempted === 0
						? 'no drafts yet'
						: `${Math.round((100 * k.drafts_cited) / k.drafts_attempted)}% (${k.drafts_cited}/${k.drafts_attempted})`}
				</dd>
			</div>
		</dl>
		<p class="text-xs text-muted-foreground">
			Coverage = drafts with valid cited sources ÷ drafts attempted. Not a correctness claim.
		</p>
	{/if}
	{#if docs && docs.length > 0}
		<ul class="flex flex-col gap-1">
			{#each docs.slice(0, 8) as d (d.doc_id)}
				<li class="text-sm">
					<span class="font-medium">{d.title}</span>
					<span class="font-mono text-xs text-muted-foreground"> {d.doc_id}</span>
				</li>
			{/each}
		</ul>
	{/if}
	<form class="flex flex-col gap-2" onsubmit={add}>
		<input
			class="rounded-md border border-input bg-background px-3 py-2 text-sm"
			placeholder="Doc title (e.g. refund policy)"
			bind:value={title}
			disabled={busy}
			aria-label="Doc title"
			maxlength="120"
		/>
		<textarea
			class="min-h-20 rounded-md border border-input bg-background px-3 py-2 text-sm"
			placeholder="Paste the doc text…"
			bind:value={text}
			disabled={busy}
			aria-label="Doc text"
			maxlength="8000"></textarea>
		<div>
			<Button type="submit" size="sm" disabled={busy || !title.trim() || !text.trim()}>
				{busy ? 'Saving…' : 'Add to knowledge'}
			</Button>
		</div>
	</form>
	{#if notice}
		<p class="text-sm text-muted-foreground" role="status">{notice}</p>
	{/if}
</section>
