import { readFile } from 'node:fs/promises';
import { isCheckable } from './validators/url.js';
import { chunk, unique } from './utils/index.js';

export class Runner {
  constructor({ extractor, http, bus, concurrency }) {
    this.extractor = extractor;
    this.http = http;
    this.bus = bus;
    this.concurrency = concurrency;
  }

  async run(file) {
    const text = await readFile(file, 'utf8');
    const links = unique(this.extractor.extract(text)).filter(isCheckable);
    this.bus.emit('run:start', { file, count: links.length });
    const results = [];
    for (const batch of chunk(links, this.concurrency)) {
      const checked = await Promise.all(batch.map((link) => this.http.check(link)));
      for (const result of checked) {
        this.bus.emit('link:checked', result);
        results.push(result);
      }
    }
    this.bus.emit('run:end', { file, results });
    return results;
  }
}
