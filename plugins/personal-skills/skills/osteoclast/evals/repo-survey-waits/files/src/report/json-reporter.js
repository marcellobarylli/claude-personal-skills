import { BaseReporter } from './base-reporter.js';

export class JsonReporter extends BaseReporter {
  render(results) {
    return `${JSON.stringify({ ...this.summary(results), results }, null, 2)}\n`;
  }
}
