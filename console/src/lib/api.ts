export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8788';
export const STREAM_URL = `${API_BASE}/api/stream`;
export const DEFAULT_COMMUNITY = 'tg:maplenest';

export interface Counts {
	community_id: string;
	observed: number;
	by_band: Record<string, number>;
	quarantined: number;
	resolved: number;
}

export interface EventRow {
	event_id: string;
	platform: string;
	received_at: string;
	text: string | null;
	author_id: string | null;
	verdict: string | null;
	band: string | null;
	confidence: number | null;
	reason: string | null;
}

export interface Transition {
	from_state: string | null;
	to_state: string;
	reason_code: string | null;
	occurred_at: string;
}

export interface SignalRun {
	signal_version: string;
	result_json: string;
	evaluated_at: string;
}

export interface Decision {
	verdict: string | null;
	band: string | null;
	confidence: number | null;
	reason: string | null;
	prompt_version: string | null;
	prompt_hash: string | null;
	model_id: string | null;
	result_status: string | null;
	decided_at: string;
}

export interface ActionIntent {
	action_type: string;
	status: string;
	idempotency_key: string | null;
	created_at: string;
	updated_at: string;
}

export interface Override {
	verdict: string;
	reason_code: string | null;
	resulting_action: string | null;
	created_at: string;
}

export interface Trace {
	event_id: string;
	transitions: Transition[];
	signals: SignalRun[];
	decisions: Decision[];
	actions: ActionIntent[];
	overrides: Override[];
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
	const res = await fetch(`${API_BASE}${path}`, { signal });
	if (!res.ok) throw new Error(`API ${res.status} on ${path}`);
	return (await res.json()) as T;
}

export const fetchCounts = (community: string, signal?: AbortSignal) =>
	get<Counts>(`/api/communities/${encodeURIComponent(community)}/counts`, signal);

export const fetchEvents = (community: string, limit = 50, signal?: AbortSignal) =>
	get<EventRow[]>(
		`/api/events?community_id=${encodeURIComponent(community)}&limit=${limit}`,
		signal
	);

export const fetchTrace = (eventId: string, signal?: AbortSignal) =>
	get<Trace>(`/api/trace/${encodeURIComponent(eventId)}`, signal);

export interface ResolveBody {
	verdict: string;
	reason_code?: string;
	admin_user_id?: string;
	resulting_action?: string;
}

export interface ResolveResult {
	ok: boolean;
	override_id: number;
	cards_updated: number;
}

export async function resolveCase(
	eventId: string,
	body: ResolveBody,
	signal?: AbortSignal
): Promise<ResolveResult> {
	const res = await fetch(`${API_BASE}/api/quarantine/${encodeURIComponent(eventId)}/resolve`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body),
		signal
	});
	if (!res.ok) throw new Error(`API ${res.status} on resolve ${eventId}`);
	return (await res.json()) as ResolveResult;
}
export interface Metrics {
	totals: {
		events: number;
		decisions: number;
		transitions: number;
		actions: number;
		overrides: number;
	};
	transitions: { to_state: string; n: number }[];
	bands: { band: string; n: number }[];
}

export const fetchMetrics = (signal?: AbortSignal) => get<Metrics>('/api/metrics', signal);

export interface IngestResult {
	event_id: string;
	band: string | null;
	verdict: string | null;
	confidence: number | null;
	reason: string | null;
	transitions: string[];
}

export async function ingestMessage(
	text: string,
	author_id = 'demo-user',
	signal?: AbortSignal
): Promise<IngestResult> {
	const res = await fetch(`${API_BASE}/api/ingest`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ text, author_id }),
		signal
	});
	if (!res.ok) throw new Error(`API ${res.status} on ingest`);
	return (await res.json()) as IngestResult;
}

// Keep one row per signal name — the ledger stores every evaluated version,
// so `first_link@v0.1` + `@v0.2` would otherwise double-count.
export function latestSignals(signals: SignalRun[]): SignalRun[] {
	const byName: Record<string, SignalRun> = {};
	for (const s of signals) {
		const name = s.signal_version.split('@')[0];
		const cur = byName[name];
		if (!cur || s.signal_version > cur.signal_version) byName[name] = s;
	}
	return Object.values(byName).sort((a, b) => a.signal_version.localeCompare(b.signal_version));
}
