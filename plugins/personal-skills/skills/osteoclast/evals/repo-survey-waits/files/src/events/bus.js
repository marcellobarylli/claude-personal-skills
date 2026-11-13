// Lightweight publish/subscribe bus so components stay decoupled.
export class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(event, listener) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(listener);
    return () => this.off(event, listener);
  }

  once(event, listener) {
    const off = this.on(event, (payload) => {
      off();
      listener(payload);
    });
    return off;
  }

  off(event, listener) {
    this.listeners.get(event)?.delete(listener);
  }

  emit(event, payload) {
    for (const listener of this.listeners.get(event) ?? []) {
      try {
        listener(payload);
      } catch {
        // A failing listener must never break the run
      }
    }
  }
}
