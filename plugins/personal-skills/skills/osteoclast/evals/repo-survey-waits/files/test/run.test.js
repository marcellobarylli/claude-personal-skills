import assert from 'node:assert/strict';
import { mkdtemp, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { run } from '../src/app.js';

async function withServer(fn) {
  const hits = {};
  const server = createServer((req, res) => {
    hits[req.url] = (hits[req.url] ?? 0) + 1;
    if (req.url === '/ok') res.statusCode = 200;
    else if (req.url === '/flaky') res.statusCode = hits[req.url] < 3 ? 500 : 200;
    else if (req.url === '/down') res.statusCode = 503;
    else res.statusCode = 404;
    res.end();
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    return await fn(`http://127.0.0.1:${server.address().port}`, hits);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

async function check(markdown, argv = []) {
  const dir = await mkdtemp(join(tmpdir(), 'linkcheck-'));
  const file = join(dir, 'doc.md');
  await writeFile(file, markdown);
  let out = '';
  const code = await run([file, ...argv], { cwd: dir, env: {}, stdout: { write: (text) => { out += text; } } });
  return { code, out };
}

test('reports broken links and exits 1', async () => {
  await withServer(async (base) => {
    const { code, out } = await check(`[ok](${base}/ok) [gone](${base}/missing) <mailto:a@b.test>`);
    assert.equal(code, 1);
    assert.equal(out, `ok   200 ${base}/ok\nFAIL 404 ${base}/missing\n2 links, 1 broken\n`);
  });
});

test('retries 5xx twice, then gives up', async () => {
  await withServer(async (base, hits) => {
    const { code, out } = await check(`[flaky](${base}/flaky) [down](${base}/down)`);
    assert.equal(code, 1);
    assert.match(out, /ok {3}200 .*\/flaky/);
    assert.match(out, /FAIL 503 .*\/down/);
    assert.equal(hits['/flaky'], 3);
    assert.equal(hits['/down'], 3);
  });
});

test('checks each unique URL once and exits 0 when all pass', async () => {
  await withServer(async (base, hits) => {
    const { code } = await check(`[a](${base}/ok) [b](${base}/ok)`);
    assert.equal(code, 0);
    assert.equal(hits['/ok'], 1);
  });
});

test('prints usage without a file', async () => {
  let out = '';
  const code = await run([], { cwd: tmpdir(), env: {}, stdout: { write: (text) => { out += text; } } });
  assert.equal(code, 2);
  assert.match(out, /^usage:/);
});
