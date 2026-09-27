<script lang="ts">
	import { fetchAlerts, parseAlertDetail, type AlertRow } from '$lib/api';
	import Badge from '$lib/components/ui/badge/badge.svelte';
	import { timeAgo } from '$lib/format';

	let { refreshKey, now }: { refreshKey: number; now: number } = $props();

	let alerts = $state<AlertRow[] | null>(null);

	async function load() {
		try {
			alerts = await fetchAlerts(20);
		} catch {
			alerts = null;
		}
	}

	$effect(() => {
		void refreshKey;
		void load();
	});
</script>

<section aria-label="Alerts" class="flex flex-col gap-2">
	<h2 class="text-base font-semibold">Alerts</h2>
	<p class="text-sm text-muted-foreground">
		What "moderators notified" means: escalation pings and quarantine resolutions from the audit
		log.
	</p>
	{#if alerts === null}
		<p class="text-sm text-muted-foreground">Loading alerts…</p>
	{:else if alerts.length === 0}
		<p class="text-sm text-muted-foreground">No alerts yet.</p>
	{:else}
		<ol class="flex flex-col gap-2">
			{#each alerts as a (a.id)}
				{@const d = parseAlertDetail(a)}
				<li class="rounded-xl border px-4 py-3">
					<div class="flex flex-wrap items-center gap-2">
						<Badge variant={a.action === 'escalation_alert' ? 'destructive' : 'secondary'}>
							{a.action === 'escalation_alert' ? 'escalation' : 'resolved'}
						</Badge>
						{#if d.event_id}
							<a href="#event-{d.event_id}" class="font-mono text-xs underline underline-offset-2">
								{d.event_id}
							</a>
						{/if}
						<span class="text-xs text-muted-foreground tabular-nums" title={a.created_at}>
							{timeAgo(a.created_at, now)} · {a.actor}
						</span>
					</div>
					{#if a.action === 'escalation_alert'}
						<p class="mt-1 text-sm">
							{d.trigger ?? 'escalation'}
							{#if d.confidence !== undefined}
								<span class="text-muted-foreground tabular-nums">
									· conf {Number(d.confidence).toFixed(2)}</span
								>
							{/if}
						</p>
						{#if d.reason}
							<p class="mt-0.5 text-xs text-muted-foreground">{d.reason}</p>
						{/if}
					{:else}
						<p class="mt-1 text-sm">
							{d.verdict ?? 'resolved'}
							{#if d.resulting_action}
								<span class="text-muted-foreground"> → {d.resulting_action}</span>
							{/if}
						</p>
					{/if}
				</li>
			{/each}
		</ol>
	{/if}
</section>
