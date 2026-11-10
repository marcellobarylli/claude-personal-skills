#!/usr/bin/env python3
"""Parse the level-4 judge's output on the host. Run with `python3 -I`; the input is untrusted data.

Input: the `claude -p --output-format json` result. The judge must end its answer with one fenced ```json block:
  {"criteria": [{"name": "...", "pass": true, "score": 0-10, "evidence": "..."}]}
Prints TOTAL <sum of scores>, ALLPASS 0|1, then FEEDBACK and one line per criterion. Exit 1 if unparseable.
"""
import json, re, sys

def main(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    try:
        result = json.loads(text).get("result", "")
    except (ValueError, AttributeError):
        return 1
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", result, re.S)
    if not blocks:
        return 1
    try:
        crit = json.loads(blocks[-1])["criteria"]
        assert isinstance(crit, list) and crit
        rows = []
        for c in crit:
            name, ok, score = str(c["name"])[:80], c["pass"], c["score"]
            assert isinstance(ok, bool) and isinstance(score, (int, float)) and 0 <= score <= 10
            rows.append((name, ok, float(score), str(c.get("evidence", ""))[:300].replace("\n", " ")))
    except (ValueError, KeyError, TypeError, AssertionError):
        return 1
    print(f"TOTAL {sum(r[2] for r in rows):g}")
    print(f"ALLPASS {int(all(r[1] for r in rows))}")
    print("FEEDBACK")
    for name, ok, score, ev in rows:
        print(f"- {name}: {'PASS' if ok else 'FAIL'} ({score:g}/10) {ev}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
