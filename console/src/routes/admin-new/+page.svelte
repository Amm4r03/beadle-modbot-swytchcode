<script lang="ts">
	import { onMount } from 'svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import CountsRow from '$lib/CountsRow.svelte';
	import EventsList from '$lib/EventsList.svelte';
	import CaseCard from '$lib/CaseCard.svelte';
	import Announce from '$lib/Announce.svelte';
	import Knowledge from '$lib/Knowledge.svelte';
	import Platforms from '$lib/Platforms.svelte';
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

	const SECTIONS = [
		{ id: 'overview', label: 'Live counts' },
		{ id: 'events', label: 'Recent events' },
		{ id: 'queue', label: 'Quarantine queue' },
		{ id: 'announce', label: 'Announcements' },
		{ id: 'knowledge', label: 'Knowledge' },
		{ id: 'taught', label: 'Because you taught me' },
		{ id: 'platforms', label: 'Platforms' }
	] as const;

	let active = $state<string>('overview');
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
	let syncTick = $state(0);

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
			notice = `Resolve failed: ${(err as Error).message}.`;
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
			syncTick += 1;
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

<Sidebar.Provider>
	<Sidebar.Root variant="inset">
		<Sidebar.Header>
			<div class="px-2 py-1">
				<p class="text-sm font-semibold">Beadle admin</p>
				<p class="text-xs text-muted-foreground tabular-nums">{DEFAULT_COMMUNITY}</p>
			</div>
		</Sidebar.Header>
		<Sidebar.Content>
			<Sidebar.Group>
				<Sidebar.GroupLabel>Sections</Sidebar.GroupLabel>
				<Sidebar.GroupContent>
					<Sidebar.Menu>
						{#each SECTIONS as s (s.id)}
							<Sidebar.MenuItem>
								<Sidebar.MenuButton
									isActive={active === s.id}
									onclick={() => {
										active = s.id;
										document
											.getElementById(`admin-new-${s.id}`)
											?.scrollIntoView({ behavior: 'smooth', block: 'start' });
									}}
								>
									{s.label}
									{#if s.id === 'queue' && quarantined.length > 0}
										<Sidebar.MenuBadge>{quarantined.length}</Sidebar.MenuBadge>
									{/if}
								</Sidebar.MenuButton>
							</Sidebar.MenuItem>
						{/each}
						<Sidebar.MenuItem>
							<Sidebar.MenuButton onclick={() => window.open('/admin', '_blank')}>
								Full console ↗
							</Sidebar.MenuButton>
						</Sidebar.MenuItem>
					</Sidebar.Menu>
				</Sidebar.GroupContent>
			</Sidebar.Group>
			<Sidebar.Group>
				<Sidebar.GroupLabel>Views</Sidebar.GroupLabel>
				<Sidebar.GroupContent>
					<Sidebar.Menu>
						<Sidebar.MenuItem>
							<Sidebar.MenuButton
								onclick={() => window.open('http://localhost:8788/test', '_blank')}
							>
								Agent journey ↗
							</Sidebar.MenuButton>
						</Sidebar.MenuItem>
						<Sidebar.MenuItem>
							<Sidebar.MenuButton
								onclick={() => window.open('http://localhost:8788/live', '_blank')}
							>
								Live agent view ↗
							</Sidebar.MenuButton>
						</Sidebar.MenuItem>
					</Sidebar.Menu>
				</Sidebar.GroupContent>
			</Sidebar.Group>
		</Sidebar.Content>
		<Sidebar.Footer>
			<p class="px-2 text-xs text-muted-foreground tabular-nums" aria-live="polite">
				{#if stale}
					reconnecting — data may be stale
				{:else if lastSync}
					live · synced {Math.round((now - lastSync) / 1000)}s ago
				{:else}
					connecting…
				{/if}
			</p>
		</Sidebar.Footer>
		<Sidebar.Rail />
	</Sidebar.Root>
	<Sidebar.Inset>
		<div class="flex items-center gap-2 px-4 py-3">
			<Sidebar.Trigger />
			<h1 class="text-lg font-semibold">Admin dashboard</h1>
		</div>
		<div class="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 pb-12">
			{#if error}
				<p
					role="alert"
					class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
				>
					Couldn't reach the read API ({error}). The API runs in your api tab — restart it there,
					not here.
				</p>
			{/if}

			<div id="admin-new-overview" class="flex scroll-mt-4 flex-col gap-2">
				<h2 class="text-base font-semibold">Live counts</h2>
				<CountsRow {counts} />
			</div>

			<div id="admin-new-events" class="flex scroll-mt-4 flex-col gap-2">
				<h2 class="text-base font-semibold">Recent events</h2>
				<EventsList {events} {now} />
			</div>

			<div id="admin-new-queue" class="flex scroll-mt-4 flex-col gap-4">
				<h2 class="text-base font-semibold tabular-nums">
					Quarantine queue ({quarantined.length})
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
			</div>

			<div id="admin-new-announce">
				<Announce />
			</div>

			<div id="admin-new-knowledge">
				<Knowledge {metrics} refreshKey={syncTick} />
			</div>

			<div id="admin-new-taught" class="flex flex-col gap-2">
				<h2 class="text-base font-semibold">Because you taught me</h2>
				{#if taught === 0}
					<p class="text-sm text-muted-foreground">
						No carried-over decisions yet. Resolve a case and a later one handled from it will
						appear here.
					</p>
				{:else}
					<p class="text-sm tabular-nums">{taught} later cases carried over your decisions.</p>
				{/if}
			</div>

			<div id="admin-new-platforms">
				<Platforms refreshKey={syncTick} />
			</div>
		</div>
	</Sidebar.Inset>
</Sidebar.Provider>
