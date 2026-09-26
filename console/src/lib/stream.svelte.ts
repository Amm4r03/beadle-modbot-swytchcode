import { STREAM_URL } from './api';

// SSE liveness hook. The stream only carries a change cursor
// {decisions, transitions, actions, ts} — payload refetch is the caller's job
// via onUpdate. Stale = no heartbeat for >5s (story A3).
export class LiveStream {
	lastMsg = $state<number | null>(null);
	stale = $state(true);
	connected = $state(false);
	onUpdate: () => void = () => void 0;
	private es: EventSource | null = null;
	private timer: number | null = null;

	connect() {
		this.disconnect();
		this.es = new EventSource(STREAM_URL);
		this.es.onmessage = () => {
			this.lastMsg = Date.now();
			this.stale = false;
			this.connected = true;
			this.onUpdate();
		};
		this.es.onerror = () => {
			this.connected = false;
			this.stale = true;
		};
		this.timer = window.setInterval(() => {
			if (this.lastMsg === null || Date.now() - this.lastMsg > 5000) {
				this.stale = true;
			}
		}, 1000);
	}

	disconnect() {
		this.es?.close();
		this.es = null;
		if (this.timer !== null) {
			window.clearInterval(this.timer);
			this.timer = null;
		}
	}
}
