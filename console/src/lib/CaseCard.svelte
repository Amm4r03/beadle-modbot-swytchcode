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
		AlertDialogAction,
		AlertDialogCancel,
		AlertDialogContent,
		AlertDialogDescription,
		AlertDialogFooter,
		AlertDialogHeader,
		AlertDialogTitle
	} from '$lib/components/ui/alert-dialog/index.js';
	import { linkifyEvidence, thresholdFromReason, timeAgo } from '$lib/format';
	import type { EventRow, Trace } from '$lib/api';

	let {
		event,
		trace,
		now,
		confirming
	}: {
		event: EventRow;
		trace: Trace | null;
		now: number;
		confirming: string | null;
	} = $props();

	const latest = $derived(trace?.decisions?.[0] ?? null);
	const threshold = $derived(thresholdFromReason(latest?.reason ?? event.reason));
</script>

<Card id="event-{event.event_id}">
	<CardHeader>
		<div class="flex items-baseline justify-between gap-3">
			<CardTitle>{event.event_id}</CardTitle>
			<StatusChip band={event.band} verdict={event.verdict} />
		</div>
		<p class="text-muted-foreground text-xs tabular-nums" title={event.received_at}>
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
							<span class="text-muted-foreground font-normal tabular-nums">
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
			<p class="text-muted-foreground text-xs tabular-nums">
				{latest.model_id ?? 'no model'} · {latest.prompt_version ?? 'no prompt version'} ·
				{latest.result_status ?? 'no status'}
			</p>
		{/if}

		{#if trace === null}
			<p class="text-muted-foreground text-sm">Loading trace…</p>
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
					<AccordionTrigger>Signals ({trace.signals.length})</AccordionTrigger>
					<AccordionContent>
						<ul class="flex flex-col gap-1">
							{#each trace.signals as s (s.signal_version)}
								<li class="text-muted-foreground text-xs">
									<span class="text-foreground font-medium">{s.signal_version}</span>
									· {s.evaluated_at}
								</li>
							{/each}
						</ul>
					</AccordionContent>
				</AccordionItem>
			</Accordion>
		{/if}

		{#if event.band === 'DRAFT'}
			<div class="flex gap-2">
				<Button size="sm">Approve</Button>
				<AlertDialog>
					<Button size="sm" variant="destructive">Deny</Button>
					<AlertDialogContent>
						<AlertDialogHeader>
							<AlertDialogTitle>Deny this case?</AlertDialogTitle>
							<AlertDialogDescription>
								This records your decision against {event.event_id}. The review endpoint is not
								built yet — nothing is written until it lands.
							</AlertDialogDescription>
						</AlertDialogHeader>
						<AlertDialogFooter>
							<AlertDialogCancel>Cancel</AlertDialogCancel>
							<AlertDialogAction disabled>Deny (coming soon)</AlertDialogAction>
						</AlertDialogFooter>
					</AlertDialogContent>
				</AlertDialog>
				{#if confirming}
					<p class="text-muted-foreground text-xs">{confirming}</p>
				{/if}
			</div>
		{/if}
	</CardContent>
</Card>
