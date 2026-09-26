<script lang="ts">
	import { onMount } from 'svelte';
	import CountsRow from '$lib/CountsRow.svelte';
	import EventsList from '$lib/EventsList.svelte';
	import CaseCard from '$lib/CaseCard.svelte';
	import ExecLog from '$lib/ExecLog.svelte';
	import StageFlow from '$lib/StageFlow.svelte';
	import TryGate from '$lib/TryGate.svelte';
	import {
		DEFAULT_COMMUNITY,
		STREAM_URL,
		fetchCounts,
		fetchEvents,
		fetchMetrics,
		fetchTrace,
		resolveCase,
		type Counts,
		type EventRow,
		type Metrics,
		type Trace
	} from '$lib/api';
	let counts = $state<Counts | null>(null);
	let metrics = $state<Metrics | null>(null);
	let events = $state<EventRow[] | null>(null);
	let traces = $state<Record<string, Trace>>({});
	let error = $state<string | null>(null);
	let stale = $state(true);
	let now = $state(Date.now());
	let lastSync = $state<number | null>(null);
	let busy = $state<string | null>(null);
	let notice = $state<string | null>(null);

	async function handleResolve(eventId: string, verdict: 'approve' | 'deny' | 'edit', label = '') {
		busy = eventId;
		notice = null;
		try {
			const body =
				verdict === 'approve'
					? { verdict: 'approve', resulting_action: 'answer' }
					: verdict === 'deny'
						? { verdict: 'deny', resulting_action: 'no_action' }
						: { verdict: 'edit', reason_code: label, resulting_action: 'answer' };
			const r = await resolveCase(eventId, body);
			notice = `Recorded override #${r.override_id} — case leaves the queue on next sync.`;
			await refresh();
		} catch (err) {
			notice = `Resolve failed: ${(err as Error).message}. The API tab may need a restart for the new endpoint.`;
		} finally {
			busy = null;
		}
	}

	let quarantined = $derived((events ?? []).filter((e) => e.band === 'DRAFT'));
	let taught = $derived((events ?? []).filter((e) => (e.reason ?? '').includes('taught')).length);

	async function refresh(signal?: AbortSignal) {
		try {
			const [c, ev, m] = await Promise.all([
				fetchCounts(DEFAULT_COMMUNITY, signal),
				fetchEvents(DEFAULT_COMMUNITY, 20, signal),
				fetchMetrics(signal)
			]);
			counts = c;
			metrics = m;
			events = ev;
			lastSync = Date.now();
			stale = false;
			error = null;
			for (const e of ev.slice(0, 8)) {
				if (!traces[e.event_id]) {
					fetchTrace(e.event_id, signal)
						.then((t) => {
							traces = { ...traces, [e.event_id]: t };
						})
						.catch(() => {});
				}
			}
		} catch (err) {
			if ((err as Error).name === 'AbortError') return;
			error = (err as Error).message;
			stale = true;
		}
	}

	onMount(() => {
		const ctl = new AbortController();
		void refresh(ctl.signal);
		const es = new EventSource(STREAM_URL);
		es.onmessage = () => {
			ctl.abort();
			void refresh(new AbortController().signal);
		};
		es.onerror = () => {
			stale = true;
		};
		const tick = window.setInterval(() => {
			now = Date.now();
			if (lastSync !== null && Date.now() - lastSync > 5000) stale = true;
		}, 1000);
		return () => {
			es.close();
			ctl.abort();
			window.clearInterval(tick);
		};
	});
</script>

<svelte:head>
	<title>Beadle admin · {DEFAULT_COMMUNITY}</title>
</svelte:head>

<div class="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6">
	<header class="flex flex-wrap items-baseline justify-between gap-2">
		<div>
			<h1 class="text-xl font-semibold">Beadle admin</h1>
			<p class="text-sm text-muted-foreground tabular-nums">{DEFAULT_COMMUNITY}</p>
		</div>
		<p class="text-xs text-muted-foreground tabular-nums" aria-live="polite">
			{#if stale}
				reconnecting — data may be stale
			{:else if lastSync}
				live · synced {Math.round((now - lastSync) / 1000)}s ago
			{:else}
				connecting…
			{/if}
		</p>
	</header>

	{#if error}
		<p
			role="alert"
			class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
		>
			Couldn't reach the read API ({error}). The API runs in your api tab — restart it there, not
			here.
		</p>
	{/if}

	<CountsRow {counts} />
	<TryGate onIngested={() => void refresh()} />
	<StageFlow {metrics} />
	<EventsList {events} {now} />
	<ExecLog events={events ?? []} {traces} {now} />
	<section id="queue" aria-label="Quarantine queue" class="flex flex-col gap-4">
		<h2 class="text-base font-semibold tabular-nums">
			Quarantine ({quarantined.length})
		</h2>
		{#if quarantined.length === 0}
			<p class="text-sm text-muted-foreground">Queue empty — nothing waiting for review.</p>
		{:else}
			{#each quarantined as ev (ev.event_id)}
				<CaseCard
					event={ev}
					trace={traces[ev.event_id] ?? null}
					{now}
					{busy}
					{notice}
					onResolve={handleResolve}
				/>
			{/each}
		{/if}
	</section>

	<section aria-label="Learning" class="flex flex-col gap-2">
		<h2 class="text-base font-semibold">Because you taught me</h2>
		{#if taught === 0}
			<p class="text-sm text-muted-foreground">
				No carried-over decisions yet. Resolve a case and a later one handled from it will appear
				here.
			</p>
		{:else}
			<p class="text-sm tabular-nums">{taught} later cases carried over your decisions.</p>
		{/if}
	</section>
</div>
