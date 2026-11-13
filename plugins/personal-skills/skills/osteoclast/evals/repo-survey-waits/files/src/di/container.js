// Minimal dependency injection container with singleton support and cycle detection.
export class Container {
  constructor() {
    this.factories = new Map();
    this.instances = new Map();
    this.resolving = new Set();
  }

  register(name, factory, { singleton = true } = {}) {
    if (typeof factory !== 'function') {
      throw new TypeError(`factory for ${name} must be a function`);
    }
    this.factories.set(name, { factory, singleton });
    return this;
  }

  has(name) {
    return this.factories.has(name);
  }

  resolve(name) {
    if (this.instances.has(name)) {
      return this.instances.get(name);
    }
    const entry = this.factories.get(name);
    if (!entry) {
      throw new Error(`nothing registered for ${name}`);
    }
    if (this.resolving.has(name)) {
      throw new Error(`circular dependency while resolving ${name}`);
    }
    this.resolving.add(name);
    try {
      const instance = entry.factory(this);
      if (entry.singleton) {
        this.instances.set(name, instance);
      }
      return instance;
    } finally {
      this.resolving.delete(name);
    }
  }

  reset() {
    this.instances.clear();
  }
}
