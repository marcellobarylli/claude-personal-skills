#!/usr/bin/env node
import { run } from '../src/app.js';

run(process.argv.slice(2)).then((code) => process.exit(code));
