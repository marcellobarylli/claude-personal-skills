export class TextFormatter {
  format({ level, message }) {
    return `[${level}] ${message}`;
  }
}

export class JsonFormatter {
  format({ level, message, meta, time }) {
    return JSON.stringify({ level, message, ...meta, time: time.toISOString() });
  }
}
