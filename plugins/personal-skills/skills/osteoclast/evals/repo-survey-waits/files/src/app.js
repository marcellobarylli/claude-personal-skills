import { Container } from './di/container.js';
import { EventBus } from './events/bus.js';
import { Logger } from './logger/logger.js';
import { ConsoleTransport } from './logger/transports.js';
import { loadConfig } from './config/loader.js';
import { ExtractorFactory } from './parser/factory.js';
import { HttpClient } from './http/client.js';
import { Runner } from './runner.js';
import { TextReporter } from './report/text-reporter.js';

export function buildContainer(argv, { cwd, env }) {
  const container = new Container();
  container.register('config', () => loadConfig(argv, { cwd, env }));
  container.register('bus', () => new EventBus());
  container.register('logger', (c) => new Logger({
    level: c.resolve('config').verbose ? 'debug' : 'warn',
    transports: [new ConsoleTransport()],
  }));
  container.register('extractor', () => ExtractorFactory.create('markdown'));
  container.register('http', (c) => new HttpClient({
    timeout: c.resolve('config').timeout,
    retries: c.resolve('config').retries,
    logger: c.resolve('logger'),
  }));
  container.register('reporter', () => new TextReporter());
  container.register('runner', (c) => new Runner({
    extractor: c.resolve('extractor'),
    http: c.resolve('http'),
    bus: c.resolve('bus'),
    concurrency: c.resolve('config').concurrency,
  }));
  return container;
}

export async function run(argv, { cwd = process.cwd(), env = process.env, stdout = process.stdout } = {}) {
  const container = buildContainer(argv, { cwd, env });
  const config = container.resolve('config');
  if (!config.file) {
    stdout.write('usage: linkcheck FILE.md [--timeout ms] [--concurrency n] [--verbose]\n');
    return 2;
  }
  const results = await container.resolve('runner').run(config.file);
  stdout.write(container.resolve('reporter').render(results));
  return results.some((result) => !result.ok) ? 1 : 0;
}
