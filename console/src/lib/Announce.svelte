<script lang="ts">
	import { postAnnounce } from '$lib/api';
	import { Button } from '$lib/components/ui/button/index.js';

	const PLATFORMS = ['telegram', 'slack', 'discord'] as const;

	let text = $state('');
	let selected = $state<Record<string, boolean>>({ telegram: true, slack: true, discord: true });
	let busy = $state(false);
	let results = $state<Record<string, string> | null>(null);
	let error = $state<string | null>(null);

	async function send(e: Event) {
		e.preventDefault();
		const msg = text.trim();
		const platforms = PLATFORMS.filter((p) => selected[p]);
		if (!msg || platforms.length === 0 || busy) return;
		busy = true;
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
	{#if error}
		<p role="alert" class="text-sm text-red-700">Announce failed: {error}</p>
	{/if}
	{#if results}
		<ul class="flex flex-col gap-1" role="status">
			{#each Object.entries(results) as [platform, outcome] (platform)}
				<li class="text-sm">
					<span class="font-medium">{platform}</span>
					<span class="text-muted-foreground"> — {outcome}</span>
				</li>
			{/each}
		</ul>
	{/if}
</section>
