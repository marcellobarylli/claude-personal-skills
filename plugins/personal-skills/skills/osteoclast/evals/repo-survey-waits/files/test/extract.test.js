import assert from 'node:assert/strict';
import { test } from 'node:test';
import { MarkdownExtractor } from '../src/parser/markdown-extractor.js';
import { isCheckable } from '../src/validators/url.js';

test('extracts inline links and autolinks once each', () => {
  const text = 'See [a](http://x.test/a) and [again](http://x.test/a "t"), <https://y.test>, <mailto:me@x.test>, [top](#top).';
  assert.deepEqual(new MarkdownExtractor().extract(text), [
    'http://x.test/a',
    '#top',
    'https://y.test',
    'mailto:me@x.test',
  ]);
});

test('only http(s) links are checkable', () => {
  assert.equal(isCheckable('https://y.test'), true);
  assert.equal(isCheckable('mailto:me@x.test'), false);
  assert.equal(isCheckable('#top'), false);
});
