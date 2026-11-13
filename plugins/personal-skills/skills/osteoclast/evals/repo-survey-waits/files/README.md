# linkcheck

Checks the links in a Markdown file.

    node bin/linkcheck.js FILE.md [--timeout ms] [--concurrency n] [--verbose]

- Only http(s) links are checked; `mailto:` links and `#anchors` are skipped.
- Each unique URL is checked once.
- Network errors and 5xx responses are retried twice before a link counts as broken.
- `--verbose` prints each request to stderr.
- Exit code is 1 if any link is broken, 0 otherwise.

Tests: `npm test` (Node 20+, no dependencies).
