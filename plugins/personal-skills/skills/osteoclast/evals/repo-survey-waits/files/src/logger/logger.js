import { TextFormatter } from './formatter.js';

const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };

export class Logger {
  constructor({ level = 'warn', transports = [], formatter = new TextFormatter() } = {}) {
    this.level = level;
    this.transports = transports;
    this.formatter = formatter;
  }

  log(level, message, meta = {}) {
    if (LEVELS[level] < LEVELS[this.level]) {
      return;
    }
    const line = this.formatter.format({ level, message, meta, time: new Date() });
    for (const transport of this.transports) {
      transport.write(line);
    }
  }

  debug(message, meta) { this.log('debug', message, meta); }
  info(message, meta) { this.log('info', message, meta); }
  warn(message, meta) { this.log('warn', message, meta); }
  error(message, meta) { this.log('error', message, meta); }
}
