<script lang="ts">
	import StatusChip from '$lib/StatusChip.svelte';
	import {
		Accordion,
		AccordionContent,
		AccordionItem,
		AccordionTrigger
	} from '$lib/components/ui/accordion/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import {
		AlertDialog,
		AlertDialogCancel,
		AlertDialogContent,
		AlertDialogDescription,
		AlertDialogFooter,
		AlertDialogHeader,
		AlertDialogTitle,
		AlertDialogTrigger
	} from '$lib/components/ui/alert-dialog/index.js';
	import { linkifyEvidence, thresholdFromReason, timeAgo } from '$lib/format';
	import { latestSignals, type EventRow, type Trace } from '$lib/api';

	let {
		event,
		trace,
		now,
		busy,
		notice,
		onResolve
	}: {
		event: EventRow;
		trace: Trace | null;
		now: number;
		busy: string | null;
		notice: string | null;
		onResolve: (eventId: string, verdict: 'approve' | 'deny' | 'edit', label?: string) => void;
	} = $props();

	let editing = $state(false);
	let denyOpen = $state(false);
	let label = $state('');

	const latest = $derived(trace?.decisions?.[0] ?? null);
	const threshold = $derived(thresholdFromReason(latest?.reason ?? event.reason));
	const signals = $derived(trace ? latestSignals(trace.signals) : []);
</script>

<Card id="event-{event.event_id}">
	<CardHeader>
		<div class="flex items-baseline justify-between gap-3">
			<CardTitle>{event.event_id}</CardTitle>
			<StatusChip band={event.band} verdict={event.verdict} />
		</div>
		<p class="text-xs text-muted-foreground tabular-nums" title={event.received_at}>
			{event.author_id ?? 'unknown'} · {timeAgo(event.received_at, now)}
		</p>
	</CardHeader>
	<CardContent>
		<p class="text-sm">{event.text ?? '(no text recorded)'}</p>

		{#if latest}
			<dl class="grid gap-1 text-sm">
				<div class="flex gap-2">
					<dt class="text-muted-foreground">Gate score</dt>
					<dd class="font-semibold tabular-nums">
						{latest.confidence === null ? '—' : latest.confidence.toFixed(2)}
						{#if threshold !== null}
							<span class="font-normal text-muted-foreground tabular-nums">
								vs {threshold.toFixed(2)} threshold
							</span>
						{/if}
					</dd>
				</div>
			</dl>
			{#if latest.reason}
				<p class="text-sm">
					{#each linkifyEvidence(latest.reason) as seg (seg.text)}
						{#if seg.eventId}
							<a class="underline underline-offset-2" href="#event-{seg.eventId}">{seg.text}</a>
						{:else}
							{seg.text}
						{/if}
					{/each}
				</p>
			{/if}
			<p class="text-xs text-muted-foreground tabular-nums">
				{latest.model_id ?? 'no model'} · {latest.prompt_version ?? 'no prompt version'} ·
				{latest.result_status ?? 'no status'}
			</p>
		{/if}

		{#if trace === null}
			<p class="text-sm text-muted-foreground">Loading trace…</p>
		{:else}
			<Accordion type="single">
				<AccordionItem value="trace">
					<AccordionTrigger>Reason chain ({trace.transitions.length})</AccordionTrigger>
					<AccordionContent>
						<ol class="flex flex-col gap-2">
							{#each trace.transitions as t, i (i)}
								<li class="text-sm">
									<span class="text-muted-foreground tabular-nums">{t.from_state ?? '∅'} →</span>
									<span class="font-medium">{t.to_state}</span>
									{#if t.reason_code}
										<span class="text-muted-foreground"> — {t.reason_code}</span>
									{/if}
								</li>
							{/each}
						</ol>
					</AccordionContent>
				</AccordionItem>
				<AccordionItem value="signals">
					<AccordionTrigger>Signals ({signals.length})</AccordionTrigger>
					<AccordionContent>
						<ul class="flex flex-col gap-1">
							{#each signals as s (s.signal_version)}
								<li class="text-xs text-muted-foreground">
									<span class="font-medium text-foreground">{s.signal_version}</span>
									· {s.evaluated_at}
								</li>
							{/each}
						</ul>
					</AccordionContent>
				</AccordionItem>
			</Accordion>
		{/if}

		{#if event.band === 'DRAFT'}
			{@const isBusy = busy === event.event_id}
			<div class="flex flex-col gap-2">
				<div class="flex gap-2">
					<Button size="sm" disabled={isBusy} onclick={() => onResolve(event.event_id, 'approve')}>
						{isBusy ? 'Working…' : 'Approve'}
					</Button>
					<Button
						size="sm"
						variant="outline"
						disabled={isBusy}
						onclick={() => {
							editing = !editing;
						}}
					>
						Edit label
					</Button>
					<AlertDialog bind:open={denyOpen}>
						<AlertDialogTrigger>
							<Button size="sm" variant="destructive" disabled={isBusy}>Deny</Button>
						</AlertDialogTrigger>
						<AlertDialogContent>
							<AlertDialogHeader>
								<AlertDialogTitle>Deny this case?</AlertDialogTitle>
								<AlertDialogDescription>
									This records your deny decision against {event.event_id} as a labeled example.
								</AlertDialogDescription>
							</AlertDialogHeader>
							<AlertDialogFooter>
								<AlertDialogCancel>Cancel</AlertDialogCancel>
								<Button
									size="sm"
									variant="destructive"
									disabled={isBusy}
									onclick={() => {
										denyOpen = false;
										onResolve(event.event_id, 'deny');
									}}
								>
									Deny and record
								</Button>
							</AlertDialogFooter>
						</AlertDialogContent>
					</AlertDialog>
				</div>
				{#if editing}
					<form
						class="flex gap-2"
						onsubmit={(e) => {
							e.preventDefault();
							onResolve(event.event_id, 'edit', label);
						}}
					>
						<input
							class="min-w-0 flex-1 rounded-md border border-input bg-background px-2 py-1 text-sm"
							placeholder="Type a corrected label to enable Save"
							bind:value={label}
							disabled={isBusy}
							aria-label="Corrected label"
						/>
						<Button size="sm" type="submit" disabled={isBusy || label.trim().length === 0}>
							Save
						</Button>
					</form>
				{/if}
				{#if notice}
					<p class="text-xs text-muted-foreground" role="status">{notice}</p>
				{/if}
			</div>
		{/if}
	</CardContent>
</Card>
