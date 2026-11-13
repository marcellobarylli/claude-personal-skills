export class ConsoleTransport {
  write(line) {
    process.stderr.write(`${line}\n`);
  }
}

export class MemoryTransport {
  constructor() {
    this.lines = [];
  }

  write(line) {
    this.lines.push(line);
  }

  clear() {
    this.lines = [];
  }
}
