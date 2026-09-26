export function timeAgo(ts: string | null, now: number): string {
	if (!ts) return 'unknown time';
	const t = new Date(ts).getTime();
	if (Number.isNaN(t)) return 'unknown time';
	const s = Math.max(0, Math.round((now - t) / 1000));
	if (s < 5) return 'just now';
	if (s < 60) return `${s}s ago`;
	const m = Math.floor(s / 60);
	if (m < 60) return `${m}m ago`;
	const h = Math.floor(m / 60);
	if (h < 24) return `${h}h ago`;
	return `${Math.floor(h / 24)}d ago`;
}

export function ageMinutes(ts: string | null, now: number): string {
	if (!ts) return '—';
	const t = new Date(ts).getTime();
	if (Number.isNaN(t)) return '—';
	return `${Math.max(0, Math.round((now - t) / 60000))}m`;
}

const BAND_LABEL: Record<string, string> = {
	AUTO: 'auto-answered',
	DRAFT: 'quarantined',
	DENY: 'blocked'
};

export function bandLabel(band: string | null): string {
	if (!band) return 'observed';
	return BAND_LABEL[band] ?? band.toLowerCase();
}

// Threshold parsed from the gate's own reason text (e.g. "0.98 at/above 0.70").
// Source is the ledger row itself — null when the pattern is absent, never guessed.
export function thresholdFromReason(reason: string | null): number | null {
	if (!reason) return null;
	const m = reason.match(/at\/above\s+(\d(?:\.\d+)?)/);
	return m ? Number(m[1]) : null;
}

// Split reason text into segments, linking evt:<id> evidence tokens.
export interface ReasonSegment {
	text: string;
	eventId?: string;
}

export function linkifyEvidence(reason: string): ReasonSegment[] {
	const parts = reason.split(/(evt:[A-Za-z0-9:_-]+)/g);
	return parts
		.filter((p) => p.length > 0)
		.map((p) => (p.startsWith('evt:') ? { text: p, eventId: p.slice(4) } : { text: p }));
}
