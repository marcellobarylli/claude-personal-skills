#!/usr/bin/env python3
"""Prose audit: does the artifact's prose follow references/style.md?

  prose-audit.py <artifact.html | text.md | text.txt> [--all]

Counts the habits that make generated prose tiring to read. The rules come from
Savage & Yeh, "Novelist Cormac McCarthy's tips on how to write a great science
paper", Nature 574 (2019). See references/style.md for each rule and its source.

Gates (any FAIL exits 1):
  G1  dash rate      more than 6 dash uses per 1000 words (a pair of dashes
                     around one clause counts as one use)
  G2  dash runs      two consecutive sentences that both use a dash
  G3  bold in prose  more than 2 bold/strong spans per 1000 words inside
                     sentences (labels rendered by code are not prose)

Warnings (listed, no effect on exit code):
  contrast     reflexive "X, not Y" / "is not X. It is Y" constructions
  stacked      two or more transition joins in one sentence (but, so, or, yet,
               thus, hence, however, which means)
  opener       decorative sentence-initial transition (However, Moreover, ...)
  meta         intensifiers and talk about the text ("the whole question",
               "importantly", "worth noting", ...)
  staged       staged imperative ("Name them, and you can ...")
  long         sentence over 35 words
  semicolon    any semicolon in prose
  exclaim      any exclamation mark
  italic       italic/em span longer than two characters (likely emphasis;
               journal titles and variables are fine, judge by eye)
  surprising   "surprisingly"/"intriguingly"/"remarkably" more than twice

Low recall, like condensation-audit.py. A clean run means these patterns are
rare, not that the prose is good. Read every screen aloud afterwards.
Prints the first 12 flags per kind; --all prints every flag.
"""
import re, sys
from pathlib import Path

DASH_RATE_MAX = 6.0      # uses per 1000 words; the Nature column runs at about 4
BOLD_RATE_MAX = 2.0      # bold spans in sentences per 1000 words
LONG_SENTENCE = 35

ABBREV = ["et al.", "e.g.", "i.e.", "vs.", "cf.", "Fig.", "fig.", "Eq.", "approx.",
          "St.", "Dr.", "No.", "al.", "U.S.", "Ref.", "refs."]

CONTRAST = [
    r"\b[a-z]+(?:ed|al|ic|ive|ous|ent|ant|ble|ly)?, not [a-z]+\b",          # adapted, not inherited
    r"\bnot\b[^.!?]{1,80}?\.\s+(?:It|They|This|That)\s+(?:is|are|was|were)\b",  # not X. It is Y
    r"\bnot (?:just|merely|only|simply)\b[^.!?]{0,80}\bbut\b",
    r"\bis not (?:a|an|the)\b[^.!?;]{0,60}[,;—]\s*(?:but|it is|it[’']s)\b",
]
JOIN = r"(?:^|[,;:—–]\s*)(but|so|or|yet|thus|hence|however|which means)\b"
OPENER = r"^(?:However|Moreover|Furthermore|Indeed|Crucially|Importantly|Notably|Thus|Hence|Additionally|Ultimately|Interestingly)\b"
META = [
    "the whole question", "the whole point", "the real question", "the real point",
    "the key point", "the key question", "the key insight", "worth noting", "worth stressing",
    "importantly", "crucially", "notably", "here is the thing", "here's the thing",
    "make no mistake", "this matters", "that is the point", "the point is", "simply put",
    "in other words", "at its core", "fundamentally", "genuinely", "precisely the",
    "exactly the", "everybody expects", "everyone expects", "what breaks", "nothing says",
    "it turns out", "the short answer", "the honest answer", "let that sink in",
]
STAGED = r"^[A-Z][a-z]+ (?:it|them|this|that|these|those)(?: [a-z]+)?, and (?:you|we) (?:can|will|get|see)\b"
SURPRISE = r"\b(?:surprisingly|intriguingly|remarkably|strikingly)\b"
DASH_CHARS = re.compile(r"—|\s–\s|\s--\s")


# ---------------------------------------------------------------- extraction
def _join_js_concat(sc):
    sc = re.sub(r"/\*.*?\*/", " ", sc, flags=re.S)
    sc = re.sub(r"(?m)^\s*//.*$", " ", sc)
    for q in ("'", '"'):
        sc = re.sub(re.escape(q) + r"\s*\+\s*" + re.escape(q), "", sc)
    return sc

def _looks_like_code(s):
    return bool(re.search(r"=>|\+\s*['\"]|['\"]\s*\+|class=|\$\{|\(\)\s*[;{]|\bfunction\b|"
                          r"querySelector|innerHTML|\.map\(|\.join\(", s))

def html_passages(raw):
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    raw = re.sub(r"data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+", "DATAURI", raw)   # embedded figures
    out = []
    for sc in re.findall(r"<script[^>]*>(.*?)</script>", raw, flags=re.S | re.I):
        sc = _join_js_concat(sc)
        for pat in (r"'((?:[^'\\\n]|\\.){40,}?)'", r'"((?:[^"\\\n]|\\.){40,}?)"',
                    r"`((?:[^`\\]|\\.){40,}?)`"):
            out += re.findall(pat, sc)
    body = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.S | re.I)
    body = re.sub(r"<style[^>]*>.*?</style>", " ", body, flags=re.S | re.I)
    out += re.split(r"</(?:p|li|td|th|div|h[1-6]|summary|figcaption|blockquote)>", body)
    clean = []
    for s in out:
        s = (s.replace("\\u2019", "’").replace("\\u2014", "—").replace("\\'", "'")
              .replace('\\"', '"').replace("\\n", " "))
        if _looks_like_code(s):
            continue
        clean.append(s)
    return clean

def text_passages(raw):
    raw = re.sub(r"```.*?```", " ", raw, flags=re.S)
    # Blank lines end a paragraph; a list marker starts a new passage.
    paras = re.split(r"\n\s*\n|\n(?=\s*(?:[-*>]|\d+\.)\s)", raw)
    out = []
    for p in paras:
        if re.match(r"\s*(#|\||<!--|---)", p):
            continue
        p = re.sub(r";\s*$", ".", p.rstrip())   # list-item punctuation, not a joined clause
        p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", p)
        p = re.sub(r"`[^`]*`", "CODE", p)
        p = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", p)
        p = re.sub(r"(?m)^\s*(?:[-*>]|\d+\.)\s+", "", p)
        out.append(p)
    return out


# ---------------------------------------------------------------- sentences
def html_entities(s):
    for a, b in (("&mdash;", "—"), ("&ndash;", "–"), ("&rsquo;", "’"), ("&lsquo;", "‘"),
                 ("&ldquo;", "“"), ("&rdquo;", "”"), ("&amp;", "&"), ("&nbsp;", " "),
                 ("&minus;", "−"), ("&rarr;", "→"), ("&hellip;", "…"), ("&#39;", "'")):
        s = s.replace(a, b)
    return s

def sentences(passage):
    """Yield (plain_text, bold_count, italic_spans) per sentence.

    A bold span that opens the passage is a run-in label ("<b>Cut.</b> Apply
    ..."), which style.md allows, so it is not counted."""
    p = html_entities(re.sub(r"\s+", " ", passage)).strip()
    for a in ABBREV:
        p = p.replace(a, a.replace(".", "\x00"))
    p = re.sub(r"^((?:<[a-z]+[^>]*>)*)<(?:b|strong)\b[^>]*>(.*?)</(?:b|strong)>", r"\1\2", p,
               count=1, flags=re.I | re.S)
    p = re.sub(r"([.?!][”\"’)]?)((?:</[a-z]+>)*)\s+(?=(?:<[a-z]+[^>]*>)*[A-Z“\"‘(0-9])",
               "\\1\\2\x01", p)
    parts = p.split("\x01")
    for part in parts:
        part = part.replace("\x00", ".")
        bold = len(re.findall(r"<(?:b|strong)\b[^>]*>", part, flags=re.I))
        ital = [m for m in re.findall(r"<(?:i|em)\b[^>]*>(.*?)</(?:i|em)>", part, flags=re.I | re.S)
                if len(re.sub(r"<[^>]+>", "", m).strip()) > 2]
        text = re.sub(r"<[^>]+>", " ", part)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text.split()) >= 4:
            yield text, bold, ital


# ---------------------------------------------------------------- audit
def audit(path):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    is_html = path.lower().endswith((".html", ".htm")) or "<html" in raw[:500].lower()
    passages = html_passages(raw) if is_html else text_passages(raw)

    words = dash_uses = bold_total = 0
    flags = {k: [] for k in ("G2 dash run", "G3 bold", "contrast", "stacked", "opener", "meta",
                             "staged", "long", "semicolon", "exclaim", "italic")}
    surprise = []
    n_sent = 0
    seen = set()
    for passage in passages:
        prev_dash, prev_text = False, None
        for text, bold, ital in sentences(passage):
            if text in seen:          # the same string can be extracted twice
                continue
            seen.add(text)
            n_sent += 1
            w = len(text.split())
            words += w
            d = len(DASH_CHARS.findall(text))
            uses = (d + 1) // 2
            dash_uses += uses
            if uses and prev_dash:
                flags["G2 dash run"].append(prev_text + "  ⟶  " + text)
            prev_dash, prev_text = bool(uses), text
            if bold:
                bold_total += bold
                flags["G3 bold"].append(text)
            low = text.lower()
            if any(re.search(c, text) for c in CONTRAST):
                flags["contrast"].append(text)
            if len(re.findall(JOIN, low)) >= 2:
                flags["stacked"].append(text)
            if re.search(OPENER, text):
                flags["opener"].append(text)
            hits = [m for m in META if re.search(r"\b" + re.escape(m) + r"\b", low)]
            if hits:
                flags["meta"].append(f"[{', '.join(hits)}] {text}")
            if re.search(STAGED, text):
                flags["staged"].append(text)
            if w > LONG_SENTENCE:
                flags["long"].append(f"({w} words) {text}")
            if ";" in text:
                flags["semicolon"].append(text)
            if "!" in re.sub(r"!=", "", text):
                flags["exclaim"].append(text)
            if ital:
                flags["italic"].append(f"[{'; '.join(re.sub('<[^>]+>', '', i) for i in ital)}] {text}")
            surprise += re.findall(SURPRISE, low)
    return words, n_sent, dash_uses, bold_total, flags, surprise


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    if len(args) != 1:
        print(__doc__); sys.exit(2)
    path = args[0]
    words, n_sent, dash_uses, bold_total, flags, surprise = audit(path)
    print(f"── prose audit · {Path(path).name}")
    if words < 50:
        print("   NO PROSE EXTRACTED: check the path or the DATA block. The audit is vacuous.")
        sys.exit(2)
    per_k = lambda n: 1000.0 * n / words
    dash_rate, bold_rate = per_k(dash_uses), per_k(bold_total)
    g1 = dash_rate > DASH_RATE_MAX
    g2 = bool(flags["G2 dash run"])
    g3 = bold_rate > BOLD_RATE_MAX
    print(f"   {words} words, {n_sent} sentences")
    print(f"   G1 dash rate   {dash_uses} uses, {dash_rate:.1f}/1000 words (max {DASH_RATE_MAX:g})"
          f"  {'FAIL' if g1 else 'pass'}")
    print(f"   G2 dash runs   {len(flags['G2 dash run'])} consecutive pairs  {'FAIL' if g2 else 'pass'}")
    print(f"   G3 bold        {bold_total} spans in sentences, {bold_rate:.1f}/1000 words"
          f" (max {BOLD_RATE_MAX:g})  {'FAIL' if g3 else 'pass'}")
    if len(surprise) > 2:
        flags.setdefault("surprising", []).append(f"{len(surprise)} uses: {', '.join(surprise)}")
    warn = {k: v for k, v in flags.items() if v and k not in ("G2 dash run", "G3 bold")}
    print("   warnings: " + (", ".join(f"{k} {len(v)}" for k, v in warn.items()) or "none"))
    for k, v in flags.items():
        if not v:
            continue
        print(f"\n   ── {k} ({len(v)})")
        for item in (v if show_all else v[:12]):
            print("   · " + (item if len(item) <= 260 else item[:257] + "..."))
        if not show_all and len(v) > 12:
            print(f"   · ... {len(v) - 12} more (--all)")
    print("\n   Low-recall floor. Read every screen aloud and apply the cut test.")
    sys.exit(1 if (g1 or g2 or g3) else 0)


if __name__ == "__main__":
    main()
