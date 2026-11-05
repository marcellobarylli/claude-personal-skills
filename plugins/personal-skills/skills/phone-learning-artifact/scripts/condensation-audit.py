#!/usr/bin/env python3
"""Condensation audit — does the artifact's prose still say what the source said?

  condensation-audit.py <artifact.html> <source.md> [source2.md ...]

Catches a failure mode the other gates miss. They check fidelity to the CORPUS:
precedence, levels, mis-citation coverage. This checks fidelity to the
SENTENCE - whether shortening a source sentence dropped something that changes
what it claims. The corpus can be perfectly faithful and the artifact still
wrong, because the artifact is a compression step.

Currently detects one high-precision pattern, the one found in real review:
a comparative or quantity word survives while the noun it governed is dropped
("preserves far more per step" - more WHAT?), where the source supplies it.

Low recall by design. A clean run is not proof the prose is faithful; it means
this specific, mechanically-checkable error is absent. Read the prose too.
"""
import re, sys, json
from pathlib import Path

COMP = (r"\b(?:far |orders of magnitude |much |substantially |significantly |vastly )?"
        r"(more|less|fewer|greater|higher|lower|larger|smaller|longer|shorter)\b")
DANGLE = {"per","at","in","on","for","by","with","from","to","over","under","across",
          ",",".",";","—","-"}
STOP = set("the a an of to in and or is are was were be been it its this that for on "
           "with as at by from than then so but".split())
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()
cw   = lambda s: {w for w in re.findall(r"[a-z][a-z'\-]{2,}", s.lower()) if w not in STOP}

def artifact_prose(path):
    """Works on any artifact: visible text nodes AND long strings inside scripts,
    so it covers both static-HTML and data-block designs."""
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    out = []
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", raw, flags=re.S | re.I)
    for sc in scripts:
        out += [x for x in re.findall(r"'((?:[^'\\]|\\.){60,}?)'", sc)]
        out += [x for x in re.findall(r'"((?:[^"\\]|\\.){60,}?)"', sc)]
        out += [x for x in re.findall(r"`((?:[^`\\]|\\.){60,}?)`", sc)]
    body = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.S | re.I)
    body = re.sub(r"<style[^>]*>.*?</style>", " ", body, flags=re.S | re.I)
    for chunk in re.split(r"</(?:p|li|td|div|h[1-6]|summary|figcaption)>", body):
        t = norm(chunk)
        if len(t.split()) >= 10:
            out.append(t)
    clean = []
    for s in out:
        s = norm(s.replace("\\u2019", "'").replace("\\'", "'").replace('\\"', '"'))
        if len(s.split()) >= 10:
            clean.append(s)
    return clean

def source_sentences(paths):
    out = []
    for p in paths:
        t = Path(p).read_text(encoding="utf-8", errors="replace")
        t = re.sub(r"`[^`]*`", " ", t)
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
        t = re.sub(r"[*_#>|]", " ", t)
        for line in t.split("\n"):
            for s in re.split(r"(?<=[.;])\s+", line):
                s = re.sub(r"\s+", " ", s).strip()
                if len(s.split()) >= 8:
                    out.append(s)
    return out

def audit(artifact, sources):
    prose, src = artifact_prose(artifact), source_sentences(sources)
    flags = []
    for p in prose:
        words = p.split()
        for m in re.finditer(COMP + r"\s+(\S+)", p):
            nxt = m.group(2).strip('“”"\'').lower().rstrip('.,;:')
            if nxt not in DANGLE:
                continue
            i = len(p[:m.start()].split())
            win = " ".join(words[max(0, i - 10): i + 10])
            wc = cw(win)
            if not wc: continue
            best, bc = None, 0.0
            for s in src:
                scw = cw(s)
                if not scw: continue
                c = len(wc & scw) / len(wc | scw)
                if c > bc: bc, best = c, s
            if not best or bc < 0.25: continue
            sm = re.search(COMP + r"\s+(\w+)", best)
            if not sm: continue
            obj = sm.group(2).lower()
            if obj in DANGLE or obj in p.lower(): continue
            flags.append({"artifact_fragment": m.group(0), "context": win,
                          "dropped_word": obj, "source": best, "similarity": round(bc, 2)})
    return prose, src, flags

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    prose, src, flags = audit(sys.argv[1], sys.argv[2:])
    print(f"── condensation audit · {Path(sys.argv[1]).name}")
    print(f"   {len(prose)} prose passages vs {len(src)} source sentences")
    if not prose:
        print("   NO PROSE EXTRACTED — check the artifact path; audit is vacuous."); sys.exit(2)
    if not flags:
        print("   no dangling comparatives found (low-recall check; read the prose too)")
        sys.exit(0)
    print(f"   {len(flags)} FLAGGED\n")
    for f in flags:
        print(f"   artifact : ...{f['artifact_fragment']}...   <- object missing")
        print(f"   context  : {f['context']}")
        print(f"   source   : {f['source'][:180]}")
        print(f"   dropped  : '{f['dropped_word']}'  (similarity {f['similarity']})\n")
    sys.exit(1)
