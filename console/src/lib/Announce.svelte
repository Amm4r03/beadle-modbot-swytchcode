<script lang="ts">
	import { postAnnounce } from '$lib/api';
	import { Button } from '$lib/components/ui/button/index.js';
	import Badge from '$lib/components/ui/badge/badge.svelte';

	const PLATFORMS = ['telegram', 'slack', 'discord'] as const;

	let text = $state('');
	let selected = $state<Record<string, boolean>>({ telegram: true, slack: true, discord: true });
	let busy = $state(false);
	let sentTo = $state<string[] | null>(null);
	let results = $state<Record<string, string> | null>(null);
	let error = $state<string | null>(null);

	function isOk(outcome: string): boolean {
		const s = outcome.toLowerCase();
		return s.startsWith('sent') || s === 'ok' || s.startsWith('posted');
	}

	async function send(e: Event) {
		e.preventDefault();
		const msg = text.trim();
		const platforms = PLATFORMS.filter((p) => selected[p]);
		if (!msg || platforms.length === 0 || busy) return;
		busy = true;
		sentTo = [...platforms];
		error = null;
		results = null;
		try {
			const r = await postAnnounce(msg, [...platforms]);
			results = r.results;
		} catch (err) {
			error = (err as Error).message;
		} finally {
			busy = false;
		}
	}
</script>

<section aria-label="Announcements" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Announce</h2>
	<p class="text-sm text-muted-foreground">
		One message, three platforms. Each result below is the live adapter response — not a preview.
	</p>
	<form class="flex flex-col gap-2" onsubmit={send}>
		<textarea
			class="min-h-20 rounded-md border border-input bg-background px-3 py-2 text-sm"
			placeholder="Announcement for the community…"
			bind:value={text}
			disabled={busy}
			aria-label="Announcement text"
			maxlength="1000"></textarea>
		<div class="flex flex-wrap items-center gap-3">
			{#each PLATFORMS as p (p)}
				<label class="flex items-center gap-1.5 text-sm">
					<input type="checkbox" bind:checked={selected[p]} disabled={busy} class="rounded" />
					{p}
				</label>
			{/each}
			<Button type="submit" size="sm" disabled={busy || text.trim().length === 0}>
				{busy ? 'Sending…' : 'Send announcement'}
			</Button>
		</div>
	</form>
	{#if busy && sentTo}
		<ul class="flex flex-wrap gap-2" role="status" aria-label="Posting in progress">
			{#each sentTo as p (p)}
				<li>
					<Badge variant="secondary">{p}: posting…</Badge>
				</li>
			{/each}
		</ul>
	{/if}
	{#if error}
		<p role="alert" class="text-sm text-red-700">
			Announce failed before any platform responded: {error}
		</p>
	{/if}
	{#if results}
		<ul class="flex flex-wrap gap-2" role="status" aria-label="Per-platform results">
			{#each Object.entries(results) as [platform, outcome] (platform)}
				<li title={outcome}>
					<Badge variant={isOk(outcome) ? 'secondary' : 'destructive'}>
						{platform}: {isOk(outcome) ? 'sent' : 'error'}
					</Badge>
				</li>
			{/each}
		</ul>
		<ul class="flex flex-col gap-1">
			{#each Object.entries(results) as [platform, outcome] (platform)}
				<li class="text-xs text-muted-foreground">
					<span class="font-medium text-foreground">{platform}</span> — {outcome}
				</li>
			{/each}
		</ul>
	{/if}
</section>
