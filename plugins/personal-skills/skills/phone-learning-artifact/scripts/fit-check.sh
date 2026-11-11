#!/bin/zsh
# fit-check.sh — measure criterion 1 (no reading unit requires scrolling or panning).
#
#   fit-check.sh <artifact.html> [width] [height]
#   fit-check.sh artifact.html 390 844     # iPhone 14/15
#   fit-check.sh artifact.html 360 800     # common Android
#
# WHY AN IFRAME, AND NOT --window-size
# Headless Chrome silently ignores --window-size for the viewport: ask for 390x844 and
# window.innerWidth still reports 500. Both old and new headless do this. Measuring at the
# wrong width gives confident wrong answers in BOTH directions, because a vw-based font
# shrinks with the viewport — a narrower screen can paradoxically fit more content. An
# iframe of the target size establishes a real viewport, so vw units and clamp() resolve
# exactly as they would on the device. Reading into that iframe from a file:// page needs
# --allow-file-access-from-files, which is why that flag is here.
#
# WHAT THE ARTIFACT MUST EXPOSE
#   window.__fitScreens = [{name: 'chain-1', show: function(){...}}, ...]
#       every reading screen, and how to display it. Without this only the opening view is
#       measured, and the script says so.
#   [data-fit] on each container that must fit without scrolling.
#       Containers WITHOUT the attribute are exempt by design — reference lists are browsed,
#       not read, and truncating them to fit a screen cuts the nuance that justifies them.
#   [data-fit-exempt] on the figure region inside a [data-fit] container.
#       Only the text above it must fit; the reader scrolls to reach the figures.
#
# FIGURES. On every screen it also counts figure.fig inside the [data-fit] containers.
#   FIGURE FAIL when a screen has none (and no data-nofig reason) or more than two, or a
#   figure is missing its image, alt text, caption or credit, or one image exceeds 300 KB,
#   or a figure has no brief (empty data-rel or data-form, or a data-kind outside KINDS,
#   which mirrors references/visuals.md; 'value' never takes a figure).
#   A screen with a data-nofig reason is listed as NO FIGURE, which does not fail the gate:
#   the reason goes to the user instead.

set -u
ART="${1:?usage: fit-check.sh <artifact.html> [width] [height]}"
W="${2:-390}"; H="${3:-844}"

CHROME=""
for p in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome 2>/dev/null)" "$(command -v chromium 2>/dev/null)"; do
  [ -n "$p" ] && [ -x "$p" ] && CHROME="$p" && break
done
[ -z "$CHROME" ] && { echo "fit-check: no Chrome or Chromium found." >&2; exit 2; }

[ -f "$ART" ] || { echo "fit-check: no such file: $ART" >&2; exit 2; }
case "$ART" in /*) ABS="$ART";; *) ABS="$PWD/$ART";; esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/wrap.html" <<HTML
<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{margin:0}</style></head><body>
<div id="OUT">pending</div>
<iframe id="f" src="file://$ABS" style="width:${W}px;height:${H}px;border:0"></iframe>
<script>
addEventListener('load', function(){
  var out = [], f = document.getElementById('f'), w, d;
  try { w = f.contentWindow; d = f.contentDocument; d.body.offsetHeight; }
  catch (e) { document.getElementById('OUT').textContent = 'BLOCKED ' + e.message; return; }

  out.push('viewport ' + w.innerWidth + 'x' + w.innerHeight +
           ' body-font ' + w.getComputedStyle(d.body).fontSize);

  function vertical(label){
    var bad = [], nodes = d.querySelectorAll('[data-fit]');
    for (var i = 0; i < nodes.length; i++) {
      var o, ex = nodes[i].querySelector('[data-fit-exempt]');
      if (ex) {   // text ends where the figure region starts
        var top = ex.getBoundingClientRect().top - nodes[i].getBoundingClientRect().top + nodes[i].scrollTop;
        o = Math.ceil(top - nodes[i].clientHeight);
      } else o = nodes[i].scrollHeight - nodes[i].clientHeight;
      if (o > 1) bad.push((nodes[i].getAttribute('data-fit') || 'unnamed') + ' +' + o + 'px');
    }
    return bad.length ? 'OVERFLOW ' + label + ': ' + bad.join(', ') : null;
  }

  var figFails = [], nofig = [], nfig = 0, figBytes = 0;
  // Mirrors the kind columns of references/visuals.md §2-3. Keep them in step.
  var KINDS = ['comparison', 'interval', 'pooled', 'trend', 'distribution', 'share', 'spread',
               'process', 'structure', 'taxonomy', 'contrast', 'spatial'];
  function figures(label){
    var nodes = d.querySelectorAll('[data-fit]'), figs = [], reason = null;
    for (var i = 0; i < nodes.length; i++) {
      if (!nodes[i].offsetParent) continue;   // not on screen
      figs = figs.concat([].slice.call(nodes[i].querySelectorAll('figure.fig')));
      var r = nodes[i].querySelector('[data-nofig]');
      if (r && r.getAttribute('data-nofig')) reason = r.getAttribute('data-nofig');
    }
    if (!figs.length) { if (reason) nofig.push(label + ': ' + reason.slice(0, 90));
                        else figFails.push(label + ' has no figure and no nofig reason'); return; }
    if (figs.length > 2) figFails.push(label + ' has ' + figs.length + ' figures (max 2)');
    figs.forEach(function(f, k){
      var img = f.querySelector('img'), id = label + ' fig ' + (k + 1);
      nfig++;
      var kind = f.getAttribute('data-kind') || '';
      if (!(f.getAttribute('data-rel') || '').trim() || !(f.getAttribute('data-form') || '').trim())
        figFails.push(id + ' no brief (rel and form)');
      if (kind === 'value') figFails.push(id + ' has a value brief: state the number in the text instead');
      else if (KINDS.indexOf(kind) < 0) figFails.push(id + ' brief kind "' + kind + '" is not in visuals.md');
      if (!img) { figFails.push(id + ' image missing'); return; }
      var kb = Math.round(img.getAttribute('src').length * 0.75 / 1024);
      figBytes += kb;
      if (kb > 300) figFails.push(id + ' is ' + kb + ' KB (max 300)');
      if (!(img.getAttribute('alt') || '').trim()) figFails.push(id + ' no alt text');
      var cap = f.querySelector('figcaption'), cr = f.querySelector('.cr');
      if (!cap || (cap.textContent.length - (cr ? cr.textContent.length : 0)) < 20) figFails.push(id + ' no caption');
      if (!cr || !cr.textContent.trim()) figFails.push(id + ' no credit');
    });
  }

  var screens = w.__fitScreens, fails = [], n = 0;
  if (screens && screens.length) {
    for (var s = 0; s < screens.length; s++) {
      try { screens[s].show(); } catch (e) { fails.push(screens[s].name + ' threw ' + e.message); continue; }
      d.body.offsetHeight; n++;
      var bad = vertical(screens[s].name);
      if (bad) fails.push(bad);
      figures(screens[s].name);
    }
    out.push(n + ' screens measured, ' + (fails.length ? fails.length + ' FAIL' : 'all fit'));
  } else {
    out.push('NOTE window.__fitScreens absent - only the opening view was measured');
    var b0 = vertical('opening view'); if (b0) fails.push(b0); n = 1;
    out.push('1 screen measured, ' + (fails.length ? 'FAIL' : 'fits'));
  }
  for (var k = 0; k < fails.length; k++) out.push('  ' + fails[k]);

  out.push(nfig + ' figures, ' + figBytes + ' KB of images, page ' +
           Math.round(d.documentElement.outerHTML.length / 1024) + ' KB');
  for (var q = 0; q < figFails.length; q++) out.push('FIGURE FAIL ' + figFails[q]);
  for (var q2 = 0; q2 < nofig.length; q2++) out.push('NO FIGURE ' + nofig[q2]);

  // horizontal pan: measured per element. documentElement.scrollWidth is useless here,
  // because it never falls below the viewport width.
  var hmax = 0, who = '';
  var all = d.querySelectorAll('*');
  for (var j = 0; j < all.length; j++) {
    var e2 = all[j];
    if (!e2.clientWidth) continue;
    var ho = e2.scrollWidth - e2.clientWidth;
    if (ho > hmax) { hmax = ho; who = e2.tagName.toLowerCase() + (e2.className ? '.' + String(e2.className).split(' ')[0] : ''); }
  }
  out.push(hmax > 1 ? 'HORIZONTAL OVERFLOW ' + hmax + 'px on ' + who : 'no horizontal overflow');

  // tap targets
  var small = [], ctl = d.querySelectorAll('button, a, [role=button], input, select');
  for (var m = 0; m < ctl.length; m++) {
    var r = ctl[m].getBoundingClientRect();
    if (r.width > 0 && r.height > 0 && r.height < 44)
      small.push((ctl[m].id || String(ctl[m].className).split(' ')[0] || ctl[m].tagName) + '@' + Math.round(r.height) + 'pt');
  }
  out.push(small.length ? 'TAP TARGETS UNDER 44pt: ' + small.join(', ') : 'all tap targets >= 44pt');

  // offline: anything that would need the network to render
  var ext = [];
  d.querySelectorAll('link[href], script[src], img[src], source[src]').forEach(function(e3){
    var u = e3.getAttribute('href') || e3.getAttribute('src') || '';
    if (/^(https?:)?\/\//.test(u)) ext.push(u.slice(0, 60));
  });
  out.push(ext.length ? 'EXTERNAL SUBRESOURCES (breaks offline): ' + ext.join(', ')
                      : 'no external subresources');

  // single line on purpose: --dump-dom is read with line-based tools, and a
  // newline inside the div makes the result unextractable.
  document.getElementById('OUT').textContent = out.join(' ||| ');
});
</script></body></html>
HTML

RAW="$("$CHROME" --headless --disable-gpu --no-sandbox --allow-file-access-from-files \
        --virtual-time-budget=5000 --dump-dom "file://$TMP/wrap.html" 2>/dev/null)"

RESULT="$(printf '%s' "$RAW" | grep -o '<div id="OUT">[^<]*' | sed 's|<div id="OUT">||' \
          | sed -e 's|&lt;|<|g' -e 's|&gt;|>|g' -e 's|&amp;|\&|g' -e 's|&quot;|"|g' \
          | awk '{gsub(/ \|\|\| /,"\n"); print}')"

echo "── fit check ${W}×${H} · $(basename "$ART") ──"
if [ -z "$RESULT" ] || [ "$RESULT" = "pending" ]; then
  echo "no result: the page did not finish loading, or it threw before measuring."
  echo "open it in a browser and check the console."
  exit 2
fi
printf '%s\n' "$RESULT"

printf '%s' "$RESULT" | grep -qE 'OVERFLOW|UNDER 44pt|EXTERNAL SUBRESOURCES|BLOCKED|FIGURE FAIL' && exit 1
exit 0
