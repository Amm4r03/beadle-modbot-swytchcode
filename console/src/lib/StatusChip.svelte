<script lang="ts">
	import Badge from '$lib/components/ui/badge/badge.svelte';
	import { bandLabel } from '$lib/format';

	let { band, verdict }: { band: string | null; verdict: string | null } = $props();

	// Quiet by default; amber/red only for the thing needing a human.
	const variant = $derived(
		band === 'DRAFT' ? 'destructive' : band === 'DENY' ? 'destructive' : 'secondary'
	);
</script>

<Badge {variant}>{band ? bandLabel(band) : (verdict ?? 'observed')}</Badge>
