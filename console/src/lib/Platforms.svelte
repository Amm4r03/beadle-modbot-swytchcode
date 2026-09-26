<script lang="ts">
	import { fetchPlatforms, type Platforms } from '$lib/api';

	let { refreshKey }: { refreshKey: number } = $props();

	let platforms = $state<Platforms | null>(null);

	async function load() {
		try {
			platforms = await fetchPlatforms();
		} catch {
			platforms = null;
		}
	}

	$effect(() => {
		void refreshKey;
		void load();
	});

	const dot = (status: string) =>
		status === 'connected'
			? 'bg-emerald-500'
			: status === 'degraded'
				? 'bg-amber-500'
				: 'bg-red-500';
</script>

<section aria-label="Connected communities" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Connected communities</h2>
	{#if platforms === null}
		<p class="text-sm text-muted-foreground">Loading platform status…</p>
	{:else}
		<ul class="grid gap-2 sm:grid-cols-2">
			{#each Object.entries(platforms) as [name, info] (name)}
				<li class="flex items-center gap-2 rounded-xl border px-3 py-2">
					<span
						class={`inline-block size-2 shrink-0 rounded-full ${dot(info.status)}`}
						aria-hidden="true"
					></span>
					<span class="text-sm font-medium capitalize">{name}</span>
					<span class="truncate font-mono text-xs text-muted-foreground" title={info.detail}>
						{info.detail}
					</span>
					<span class="ml-auto text-xs text-muted-foreground tabular-nums">{info.status}</span>
				</li>
			{/each}
		</ul>
	{/if}
</section>
