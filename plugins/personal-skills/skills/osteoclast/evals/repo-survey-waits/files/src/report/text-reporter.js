import { BaseReporter } from './base-reporter.js';

export class TextReporter extends BaseReporter {
  render(results) {
    const lines = results.map((result) => `${result.ok ? 'ok  ' : 'FAIL'} ${result.status} ${result.url}`);
    const { total, broken } = this.summary(results);
    lines.push(`${total} links, ${broken} broken`);
    return `${lines.join('\n')}\n`;
  }
}
