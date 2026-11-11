#!/usr/bin/env python3
"""Citation audit (gate 11): does every sourced sentence link to the right card?

  cite-audit.py <artifact.html> [--against <previous.html>] [--corpus <file>...] [--all]

The artifact cites inline. A marker {{id}} or {{id|locator}} sits inside the
sentence it supports, and `id` is a source card's `id`. Because the marker is
part of the sentence string, it survives every edit that keeps the claim. This
script checks that nothing dropped or misdirected one.

Gates (any FAIL exits 1):
  C1  card ids       every source card has an id: lowercase letters, digits and
                     hyphens, unique, and not "nocite"
  C2  resolution     every marker and every `ev` entry names an existing card
  C3  unsourced      a sentence on an argument or domain screen that carries a
                     number or a quotation has no marker. Exempt one explicitly
                     with {{nocite|reason}}; the reason is listed below.
  C4  quotation      a quotation in a cited sentence appears on none of the cards
                     it cites. With --corpus, a quotation found in the corpus but
                     not on the card is a warning instead: add it to the card's
                     text, or check that the marker points to the right source.

Warnings (listed, no effect on exit code):
  number       a number in a cited sentence appears on none of the cited cards
               (cards summarise, so judge each one)
  dropped      with --against, a card one screen cited before and no longer
               cites. Each is either a deleted claim or a lost marker.
  uncited      a card no screen cites (fine for a card that exists for its
               "do not cite for" field)

Sentences tagged "ours" (cav t:'ours') are unsourced by definition and exempt
from C3. The open tab and the anchor panel are checked for C2 and C4 only.
Needs node on PATH to read the DATA block.
"""
import json, re, subprocess, sys
from pathlib import Path

MARK = re.compile(r"\{\{([^{}|]+)(?:\|([^{}]*))?\}\}")
ID_OK = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ABBREV = ["et al.", "e.g.", "i.e.", "vs.", "cf.", "Fig.", "fig.", "Eq.", "approx.",
          "St.", "Dr.", "No.", "al.", "U.S.", "Ref.", "refs.", "p.", "pp.", "v."]
ENT = (("&mdash;", "—"), ("&ndash;", "–"), ("&rsquo;", "’"), ("&lsquo;", "‘"), ("&ldquo;", "“"),
       ("&rdquo;", "”"), ("&amp;", "&"), ("&nbsp;", " "), ("&thinsp;", " "), ("&minus;", "−"),
       ("&rarr;", "→"), ("&hellip;", "…"), ("&#39;", "'"), ("&times;", "×"), ("&delta;", "δ"),
       ("&sup2;", "²"), ("&lt;", "<"), ("&gt;", ">"))
NUM = re.compile(r"(?<![\w§.\-])[−-]?\d[\d,]*(?:\.\d+)?")
QUOTE = re.compile(r"“([^”]+)”")


def ent(s):
    for a, b in ENT:
        s = s.replace(a, b)
    return s

def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", ent(s or ""))).strip()

def norm(s):
    s = plain(MARK.sub(" ", s)).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("−", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s)

def nums(s):
    return {n.replace(",", "").replace("−", "-").lstrip("-") for n in NUM.findall(s)}


def load_data(path):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"const DATA\s*=\s*(\{.*?\n\});", raw, flags=re.S)
    if not m:
        sys.exit(f"cite-audit: no `const DATA = {{...}};` block in {path}")
    js = "const DATA=" + m.group(1) + ";process.stdout.write(JSON.stringify(DATA));"
    try:
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("cite-audit: node not found on PATH; it is needed to read the DATA block.")
    except subprocess.CalledProcessError as e:
        sys.exit("cite-audit: the DATA block did not evaluate:\n" + e.stderr[-800:])
    return json.loads(out)


def units(D):
    """Yield (screen, field, html, required) for every prose string."""
    for n in D.get("spine") or []:
        scr = "link " + str(n.get("k", "?"))
        for f in ("claim", "because", "forces"):
            yield scr, f, n.get(f) or "", True
        for c in n.get("cav") or []:
            yield scr, "cav", c.get("x") or "", c.get("t") != "ours"
    for k, c in (D.get("clusters") or {}).items():
        yield k, "lead", c.get("lead") or "", True
        for s in c.get("subs") or []:
            yield s.get("c", k), "d", s.get("d") or "", True
            yield s.get("c", k), "t", s.get("t") or "", True
    o = D.get("open") or {}
    yield "open", "intro", o.get("intro") or "", False
    for q in o.get("questions") or []:
        yield "open", "question", (q.get("q") or "") + " " + (q.get("w") or ""), False
    for key in ("incomplete", "ours"):
        for i in o.get(key) or []:
            yield "open", key, (i.get("h") or "") + ". " + (i.get("x") or ""), False
    a = D.get("anchor") or {}
    if a:
        yield "anchor", "key", a.get("key") or "", False


def sentences(h):
    """Split prose into sentences. Markers stay with the sentence they sit in,
    or with the one they directly follow."""
    marks = []
    def keep(m):
        marks.append((m.group(1).strip(), (m.group(2) or "").strip()))
        return f"\x02{len(marks) - 1}\x03"
    p = ent(re.sub(r"\s+", " ", MARK.sub(keep, h))).strip()
    for a in ABBREV:
        p = p.replace(" " + a, " " + a.replace(".", "\x00"))
    p = re.sub(r"([.?!][”\"’)]?)((?:</[a-z]+>|\x02\d+\x03)*)\s+(?=(?:<[a-z]+[^>]*>)*[A-Z“\"‘(0-9<])",
               "\\1\\2\x01", p)
    for part in p.split("\x01"):
        part = part.replace("\x00", ".")
        ms = [marks[int(i)] for i in re.findall(r"\x02(\d+)\x03", part)]
        text = plain(re.sub(r"\x02\d+\x03", " ", part))
        if text:
            yield text, ms


def card_text(c):
    ann = (c.get("ann") or {}).get("x") or ""
    return norm(" ".join([c.get("n") or "", c.get("m") or "", c.get("s") or "", c.get("not") or "", ann]))


def panel_marks(D):
    out = {}
    for scr, f, h, _ in units(D):
        for m in MARK.finditer(h):
            if m.group(1).strip() != "nocite":
                out.setdefault(scr, set()).add(m.group(1).strip())
    for n in D.get("spine") or []:
        out.setdefault("link " + str(n.get("k", "?")), set()).update(n.get("ev") or [])
    for c in (D.get("clusters") or {}).values():
        for s in c.get("subs") or []:
            out.setdefault(s.get("c"), set()).update(s.get("ev") or [])
    return out


def audit(path, against=None, corpus=()):
    D = load_data(path)
    cards = D.get("sources") or []
    fails = {k: [] for k in ("C1 card ids", "C2 resolution", "C3 unsourced", "C4 quotation")}
    warns = {k: [] for k in ("quotation in corpus only", "number", "dropped", "uncited")}
    exempt = []

    ids = {}
    for i, c in enumerate(cards):
        cid = c.get("id")
        name = plain(c.get("n") or f"card {i + 1}")
        if not cid:
            fails["C1 card ids"].append(f"no id: {name}")
        elif not ID_OK.match(cid) or cid == "nocite":
            fails["C1 card ids"].append(f"bad id '{cid}': {name}")
        elif cid in ids:
            fails["C1 card ids"].append(f"duplicate id '{cid}': {name}")
        else:
            ids[cid] = c
    text = {cid: card_text(c) for cid, c in ids.items()}
    cnums = {cid: nums(t) for cid, t in text.items()}
    corp = norm(" ".join(Path(f).read_text(encoding="utf-8", errors="replace") for f in corpus))

    n_marks = n_need = n_cited_sent = n_quote_ok = 0
    used = set()
    for scr, f, h, required in units(D):
        for m in MARK.finditer(h):
            cid = m.group(1).strip()
            if cid == "nocite":
                continue
            n_marks += 1
            used.add(cid)
            if cid not in ids:
                fails["C2 resolution"].append(f"{scr} · {f}: {{{{{cid}}}}} names no card")
        for t, ms in sentences(h):
            refs = [cid for cid, _ in ms if cid != "nocite"]
            for cid, why in ms:
                if cid == "nocite":
                    exempt.append(f"{scr} · {plain(why) or 'NO REASON GIVEN'} · {t[:120]}")
            quotes = [q for q in QUOTE.findall(t) if len(q.split()) >= 3]
            ns = nums(t)
            if required and (ns or quotes):
                n_need += 1
                if not ms:
                    fails["C3 unsourced"].append(f"{scr} · {f}: {t}")
            if not refs:
                continue
            n_cited_sent += 1
            have = " ".join(text.get(cid, "") for cid in refs)
            for q in quotes:
                nq = norm(q).strip(" .,;:")
                if nq in have:
                    n_quote_ok += 1
                elif corp and nq in corp:
                    warns["quotation in corpus only"].append(f"{scr} → {', '.join(refs)}: “{q}”")
                else:
                    fails["C4 quotation"].append(f"{scr} → {', '.join(refs)}: “{q}”")
            onc = set().union(*(cnums.get(cid, set()) for cid in refs))
            miss = sorted(n for n in ns if n not in onc)
            if miss:
                warns["number"].append(f"{scr} → {', '.join(refs)}: {', '.join(miss)} · {t[:110]}")

    for scr, ev in panel_marks(D).items():
        for cid in ev:
            used.add(cid)
            if cid not in ids:
                fails["C2 resolution"].append(f"{scr} · ev: '{cid}' names no card")
    warns["uncited"] = [f"{cid}: {plain(c.get('n'))}" for cid, c in ids.items() if cid not in used]

    note = None
    if against:
        old, new = panel_marks(load_data(against)), panel_marks(D)
        if not any(old.values()):
            note = f"--against {Path(against).name}: it carries no markers, so there is nothing to compare"
        for scr, before in old.items():
            for cid in sorted(before - new.get(scr, set())):
                warns["dropped"].append(f"{scr} no longer cites {cid}"
                                        + ("" if scr in new else " (screen removed)"))

    return dict(cards=len(cards), ids=len(ids), marks=n_marks, need=n_need, cited=n_cited_sent,
                quote_ok=n_quote_ok, fails=fails, warns=warns, exempt=exempt, note=note)


def main():
    argv = sys.argv[1:]
    show_all = "--all" in argv
    against, corpus, pos, i = None, [], [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--against":
            against = argv[i + 1]; i += 2; continue
        if a == "--corpus":
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                corpus.append(argv[i]); i += 1
            continue
        if not a.startswith("--"):
            pos.append(a)
        i += 1
    if len(pos) != 1:
        print(__doc__); sys.exit(2)
    r = audit(pos[0], against, corpus)
    print(f"── citation audit · {Path(pos[0]).name}")
    print(f"   {r['cards']} cards, {r['ids']} with valid ids · {r['marks']} markers · "
          f"{r['cited']} cited sentences · {r['need']} sentences carry a number or quotation")
    for k, v in r["fails"].items():
        print(f"   {k:<15}{len(v):>4}  {'FAIL' if v else 'pass'}")
    print(f"   quotations matched on the cited card: {r['quote_ok']}")
    print(f"   exemptions ({{{{nocite|…}}}}): {len(r['exempt'])}")
    if r["note"]:
        print("   " + r["note"])
    print("   warnings: " + (", ".join(f"{k} {len(v)}" for k, v in r["warns"].items() if v) or "none"))
    blocks = list(r["fails"].items()) + [("exemptions", r["exempt"])] + list(r["warns"].items())
    for k, v in blocks:
        if not v:
            continue
        print(f"\n   ── {k} ({len(v)})")
        for item in (v if show_all else v[:15]):
            print("   · " + (item if len(item) <= 240 else item[:237] + "..."))
        if not show_all and len(v) > 15:
            print(f"   · ... {len(v) - 15} more (--all)")
    sys.exit(1 if any(r["fails"].values()) else 0)


if __name__ == "__main__":
    main()
