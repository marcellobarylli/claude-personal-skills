#!/bin/zsh
# Mechanical checks for the assertions that do not need judgement.
# Usage: mechanical-grade.sh <run-outputs-dir> <case-name>
set -u
D="$1"; CASE="$2"
H0=$(find "$D" -name '*.html' 2>/dev/null | head -1)
# Strip HTML comments before grepping. A first pass flagged this skill's own
# provenance comment -- which documents "loads no @import" and "scope cut was
# excluded" -- as if those were content. Three false FAILs against a correct
# artifact. Grade what the reader sees, not the build notes.
H=""
if [ -n "$H0" ]; then
  H=$(mktemp); python3 - "$H0" "$H" <<'PYX'
import re,sys
src,dst=sys.argv[1],sys.argv[2]
open(dst,'w').write(re.sub(r'<!--.*?-->','',open(src,encoding='utf-8',errors='replace').read(),flags=re.S))
PYX
fi
say(){ printf '  %-46s %s\n' "$1" "$2"; }
echo "── $CASE :: ${D:h:t}"
[ -z "$H0" ] && { echo "  NO HTML OUTPUT FOUND"; exit 0; }
echo "  file: $(basename "$H0")  ($(wc -c < "$H0" | tr -d ' ') bytes, comments stripped for grading)"

# self-contained: external subresources only (outbound <a href> is fine)
EXT=$(grep -oE '<(link|script|img|source)[^>]*(href|src)="https?://[^"]*"' "$H" | wc -l | tr -d ' ')
EXTI=$(grep -coE '@import|url\(https?://' "$H" | tr -d ' ')
say "self-contained (0 ext subresources)" "$([ "$EXT" = 0 ] && [ "$EXTI" = 0 ] && echo PASS || echo "FAIL ext=$EXT import/url=$EXTI")"

# time / progress indicators
# Detect by IMPLEMENTATION, not by the word: a first pass looked for
# "progress-bar" and missed a baseline whose element was simply called `prog`.
P1=$(grep -icE '(id|class)="[^"]*prog|#prog\b|\.prog\b' "$H" | tr -d ' ')
P2=$(grep -icE 'style\.width *= *.*(scroll|/ *h|pct|percent)|scrollY.*100|100.*scrollY' "$H" | tr -d ' ')
P3=$(grep -icE 'min read|minute read|time (left|remaining)|[0-9]+% (read|complete)|reading time' "$H" | tr -d ' ')
PROG=$((P1+P2+P3))
say "no time/progress indicator" "$([ "$PROG" = 0 ] && echo PASS || echo "FAIL (elem=$P1 scroll-width=$P2 time=$P3)")"

case "$CASE" in
 connected-corpus-with-grades)
  for pat in 'E0' 'E1' 'E2'; do :; done
  LV=$(grep -coE '\bE0\b|\bE1\b|\bE2\b' "$H" | tr -d ' ')
  say "E0/E1/E2 vocabulary present" "$([ "$LV" -gt 0 ] && echo "PASS ($LV)" || echo FAIL)"
  DNC=$(grep -icE 'do not cite|must not be cited|not to be cited|don.t cite' "$H" | tr -d ' ')
  say "do-not-cite field present" "$([ "$DNC" -gt 0 ] && echo "PASS ($DNC)" || echo FAIL)"
  T=0
  grep -qiE 'gold passage' "$H" && T=$((T+1))
  grep -qiE 'Ferreira, ?Naidoo, ?Kaur' "$H" && T=$((T+1))
  grep -qiE 'readiness test' "$H" && T=$((T+1))
  grep -qiE 'closed[- ]world' "$H" && T=$((T+1))
  say "specific traps carried (>=3 of 4)" "$([ "$T" -ge 3 ] && echo "PASS ($T/4)" || echo "FAIL ($T/4)")"
  INC=$(grep -icE 'incomplete read|executive summary|full (report|text) (was )?not' "$H" | tr -d ' ')
  say "Marchetti incomplete read marked" "$([ "$INC" -gt 0 ] && echo PASS || echo FAIL)"
  VER=$(grep -coE '>[^<]*\b(verified|confirmed|solid)\b[^<]*<' "$H" | tr -d ' ')
  say "no 'verified' certification marker" "$([ "$VER" = 0 ] && echo PASS || echo "CHECK $VER hit(s) - judge")"
  AFF=$(grep -ic 'affiliation' "$H" | tr -d ' ')
  say "scope cut (affiliation) absent" "$([ "$AFF" = 0 ] && echo PASS || echo "FAIL $AFF")"
  ;;
 single-meta-analysis)
  M=0
  grep -qiE 'dosimetry' "$H" && M=$((M+1))
  grep -qiE 'within[- ]subject' "$H" && M=$((M+1))
  grep -qiE 'risk of bias' "$H" && M=$((M+1))
  say "moderators present (dosim/design/bias)" "$([ "$M" -ge 3 ] && echo "PASS ($M/3)" || echo "FAIL ($M/3)")"
  NS=$(grep -icE 'latitude|season' "$H" | tr -d ' ')
  say "non-significant moderators shown" "$([ "$NS" -gt 0 ] && echo PASS || echo FAIL)"
  S=0
  grep -qi 'Castellanos' "$H" && S=$((S+1))
  grep -qi 'Petrova' "$H" && S=$((S+1))
  grep -qiE 'Weller|overlapping cohort|double-count' "$H" && S=$((S+1))
  say "study-level caveats (>=2 of 3)" "$([ "$S" -ge 2 ] && echo "PASS ($S/3)" || echo "FAIL ($S/3)")"
  U=0
  grep -qiE 'prediction interval' "$H" && U=$((U+1))
  grep -qiE '0\.24|trim[- ]and[- ]fill|small[- ]study' "$H" && U=$((U+1))
  grep -qiE 'higher[- ]bias|bias gradient|0\.22' "$H" && U=$((U+1))
  say "uncomfortable findings (>=2 of 3)" "$([ "$U" -ge 2 ] && echo "PASS ($U/3)" || echo "FAIL ($U/3)")"
  OBS=$(grep -icE 'observational|not causal|causal direction|correlat' "$H" | tr -d ' ')
  say "non-causal framing present" "$([ "$OBS" -gt 0 ] && echo PASS || echo FAIL)"
  ;;
 survey-without-grading-vocabulary)
  INV=$(grep -icE 'evidence level|confidence level|quality (tier|score|rating)|certainty (level|rating)|grade [ABC]\b|tier [123]\b|\bL0\b|\bL1\b|\bL2\b|\bE0\b|\bE1\b|\bE2\b' "$H" | tr -d ' ')
  say "no invented grading vocabulary" "$([ "$INV" = 0 ] && echo PASS || echo "FAIL $INV hit(s)")"
  LIM=$(grep -icE 'no outcome was measured|not representative|did not assess|takes no view|does not contain' "$H" | tr -d ' ')
  say "survey limitations carried" "$([ "$LIM" -gt 0 ] && echo "PASS ($LIM)" || echo FAIL)"
  ARG=$(grep -icE 'we (argue|recommend|conclude that)|this (survey|report) (argues|recommends)|should adopt|best practice' "$H" | tr -d ' ')
  say "no fabricated argument (keyword)" "$([ "$ARG" = 0 ] && echo PASS || echo "CHECK $ARG - judge")"
  ;;
esac
