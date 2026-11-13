import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { DEFAULTS } from './defaults.js';
import { deepClone, isNil } from '../utils/index.js';

function fromRcFile(cwd) {
  const path = join(cwd, '.linkcheckrc.json');
  if (!existsSync(path)) {
    return {};
  }
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return {};
  }
}

function fromEnv(env) {
  const out = {};
  if (!isNil(env.LINKCHECK_TIMEOUT)) {
    out.timeout = Number(env.LINKCHECK_TIMEOUT);
  }
  if (!isNil(env.LINKCHECK_CONCURRENCY)) {
    out.concurrency = Number(env.LINKCHECK_CONCURRENCY);
  }
  return out;
}

function fromArgv(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--timeout') {
      out.timeout = Number(argv[i += 1]);
    } else if (arg === '--concurrency') {
      out.concurrency = Number(argv[i += 1]);
    } else if (arg === '--verbose') {
      out.verbose = true;
    } else if (!arg.startsWith('--')) {
      out.file = arg;
    }
  }
  return out;
}

// Precedence: defaults < rc file < environment < command line
export function loadConfig(argv, { cwd, env }) {
  return { ...deepClone(DEFAULTS), ...fromRcFile(cwd), ...fromEnv(env), ...fromArgv(argv) };
}
