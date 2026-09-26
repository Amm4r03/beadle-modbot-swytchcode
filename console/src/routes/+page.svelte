<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
</script>

<svelte:head>
	<title>Beadle — the community agent with a gate that learns</title>
</svelte:head>

<div class="mx-auto flex max-w-3xl flex-col gap-8 px-4 py-12">
	<header class="flex flex-col gap-4">
		<p class="text-sm text-muted-foreground">Beadle · Track 3</p>
		<h1 class="text-3xl font-semibold tracking-tight">
			The community agent with a gate that learns.
		</h1>
		<p class="max-w-xl text-muted-foreground">
			Every message passes a gate: confident answers go through, unsure cases wait for a human, and
			every decision carries its reason. Staged demo data where labeled — live ledger everywhere
			else.
		</p>
		<div class="flex gap-2">
			<Button href="/admin">Open the admin console</Button>
			<Button href="/admin#queue" variant="outline">Review the queue</Button>
		</div>
	</header>

	<div class="grid gap-3 sm:grid-cols-3">
		<Card>
			<CardHeader><CardTitle>Watch</CardTitle></CardHeader>
			<CardContent>
				<p class="text-sm text-muted-foreground">
					Live counts tick as the gate decides — no refresh.
				</p>
			</CardContent>
		</Card>
		<Card>
			<CardHeader><CardTitle>Inspect</CardTitle></CardHeader>
			<CardContent>
				<p class="text-sm text-muted-foreground">
					Every case shows its score, threshold, and reason.
				</p>
			</CardContent>
		</Card>
		<Card>
			<CardHeader><CardTitle>Teach</CardTitle></CardHeader>
			<CardContent>
				<p class="text-sm text-muted-foreground">
					Your resolutions become the examples later cases use.
				</p>
			</CardContent>
		</Card>
	</div>
</div>
