import { sleep } from '../utils/index.js';

export class HttpClient {
  constructor({ timeout, retries, logger }) {
    this.timeout = timeout;
    this.retries = retries;
    this.logger = logger;
  }

  async attempt(url) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);
    try {
      const response = await fetch(url, { method: 'HEAD', signal: controller.signal });
      return response.status;
    } finally {
      clearTimeout(timer);
    }
  }

  // Network errors and 5xx are retried; 4xx is a definite answer.
  async check(url) {
    let status = 0;
    for (let attempt = 0; attempt <= this.retries; attempt += 1) {
      this.logger.debug(`HEAD ${url} (attempt ${attempt + 1})`);
      try {
        status = await this.attempt(url);
      } catch {
        status = 0;
      }
      if (status !== 0 && status < 500) {
        break;
      }
      if (attempt < this.retries) {
        await sleep(20 * (attempt + 1));
      }
    }
    return { url, status, ok: status >= 200 && status < 400 };
  }
}
