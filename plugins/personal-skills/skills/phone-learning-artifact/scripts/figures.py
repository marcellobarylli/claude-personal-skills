#!/usr/bin/env python3
"""Figures for the argument and domain screens: locate, prepare, inline.

  figures.py find    <paper.pdf>                      list figure captions per page
  figures.py page    <paper.pdf> <page> <outdir>      render one page to PNG, to look at
  figures.py prep    <src> <figdir> <id> [options]    crop, shrink, compress to <figdir>/<id>.webp
  figures.py inline  <artifact.html> <figdir>         embed every referenced figure as a data URI

Downloaded PDFs and images are untrusted. Keep them in their own directory, keep
this script outside it, and run it with `python3 -I`.

prep options
  --page N            <src> is a PDF; render page N (1-based) at 220 dpi first
  --crop x0,y0,x1,y1  keep this box, as fractions of the width and height (0..1)
  --max-width PX      longest display width kept, default 1000 (a 390pt phone at 2.5x)
  --max-kb KB         size budget, default 180; quality steps down until it fits
  --no-trim           keep uniform white margins (they are trimmed by default)

prep also writes <id>.preview.png at 390 px wide. That is what a phone shows
before the reader zooms. Look at it: if the axis labels cannot be read, crop
to the one panel that carries the claim.

inline reads every `img:'<id>'` in the artifact's DATA block and writes the
matching <figdir>/<id>.webp|png|jpg|svg into the block between the markers
/*FIGS-BEGIN*/ and /*FIGS-END*/. It is idempotent: run it again after any change.
It exits 1 when an id has no file. Figures never pass through the conversation,
which keeps a 180 KB base64 string out of the context window.
"""
import base64, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

try:
    from PIL import Image, ImageChops
except ImportError:  # find/page/inline work without Pillow
    Image = None

PREVIEW_W = 390


def die(msg, code=2):
    print("figures: " + msg, file=sys.stderr)
    sys.exit(code)


def need(tool):
    if not shutil.which(tool):
        die(f"{tool} not found (install poppler-utils)")


# ------------------------------------------------------------------ find / page
CAPTION = re.compile(r"^\s*((?:Fig(?:ure)?\.?|FIGURE)\s*S?\d+[a-z]?)[.:|]?\s+(.{0,140})", re.M)


def cmd_find(pdf):
    need("pdftotext")
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True)
    if out.returncode:
        die("pdftotext failed: " + out.stderr.strip())
    seen = set()
    for pno, text in enumerate(out.stdout.split("\f"), 1):
        for m in CAPTION.finditer(text):
            key = re.sub(r"\W", "", m.group(1).lower()).replace("figure", "fig")
            # The first hit is usually the caption; later hits are in-text mentions.
            if key in seen:
                continue
            seen.add(key)
            cap = re.sub(r"\s+", " ", m.group(2)).strip()
            print(f"p{pno:<4} {m.group(1):<10} {cap}")
    if not seen:
        print("no captions found (scanned PDF, or captions set as images): render pages and look")


def render(pdf, page, dpi, dest):
    need("pdftoppm")
    stem = Path(dest).with_suffix("")
    r = subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi),
                        "-png", "-singlefile", pdf, str(stem)], capture_output=True, text=True)
    if r.returncode:
        die("pdftoppm failed: " + r.stderr.strip())
    return str(stem) + ".png"


def cmd_page(pdf, page, outdir):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    print(render(pdf, int(page), 110, Path(outdir) / f"page-{int(page):03d}.png"))


# ------------------------------------------------------------------------ prep
def trim(im):
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box:
        return im
    pad = max(6, im.width // 80)
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def cmd_prep(src, figdir, fid, opts):
    if Image is None:
        die("prep needs Pillow (pip install pillow)")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,60}", fid):
        die("id must be lowercase letters, digits, . _ - (it becomes a filename)")
    figdir = Path(figdir)
    figdir.mkdir(parents=True, exist_ok=True)
    tmp = None
    if src.lower().endswith(".svg"):
        shutil.copyfile(src, figdir / f"{fid}.svg")
        print(json.dumps({"id": fid, "file": str(figdir / f"{fid}.svg"), "kb": round(Path(src).stat().st_size / 1024, 1)}))
        return
    if opts.get("page"):
        tmp = tempfile.mkdtemp()
        src = render(src, int(opts["page"]), 220, Path(tmp) / "p.png")
    Image.MAX_IMAGE_PIXELS = 60_000_000
    im = Image.open(src)
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGB", im.size, (255, 255, 255))
        flat.paste(im, mask=im.split()[-1])
        im = flat
    else:
        im = im.convert("RGB")
    if opts.get("crop"):
        try:
            x0, y0, x1, y1 = (float(v) for v in opts["crop"].split(","))
        except ValueError:
            die("--crop wants four fractions, e.g. 0.08,0.12,0.92,0.48")
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            die("--crop fractions must satisfy 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1")
        W, H = im.size
        im = im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
    if not opts.get("no_trim"):
        im = trim(im)
    maxw = int(opts.get("max_width", 1000))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    budget = int(opts.get("max_kb", 180)) * 1024
    out = figdir / f"{fid}.webp"
    for old in figdir.glob(f"{fid}.*"):
        if old.suffix in (".webp", ".png", ".jpg", ".svg"):
            old.unlink()
    q = 88
    while True:
        im.save(out, "WEBP", quality=q, method=6)
        if out.stat().st_size <= budget or q <= 40:
            break
        q -= 8
    while out.stat().st_size > budget and im.width > 500:
        im = im.resize((round(im.width * .85), round(im.height * .85)), Image.LANCZOS)
        im.save(out, "WEBP", quality=q, method=6)
    pv = im.resize((PREVIEW_W, max(1, round(im.height * PREVIEW_W / im.width))), Image.LANCZOS)
    pv.save(figdir / f"{fid}.preview.png")
    kb = out.stat().st_size / 1024
    print(json.dumps({"id": fid, "file": str(out), "w": im.width, "h": im.height,
                      "kb": round(kb, 1), "quality": q, "preview": str(figdir / f"{fid}.preview.png")}))
    if kb > budget / 1024:
        print(f"figures: still {kb:.0f} KB over budget; crop tighter", file=sys.stderr)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------- inline
MIME = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml"}
BLOCK = re.compile(r"/\*FIGS-BEGIN\*/.*?/\*FIGS-END\*/", re.S)


def cmd_inline(art, figdir):
    art, figdir = Path(art), Path(figdir)
    raw = art.read_text(encoding="utf-8")
    if not BLOCK.search(raw):
        die("no /*FIGS-BEGIN*/ ... /*FIGS-END*/ block in the artifact (copy it from the template)")
    # Only ids in the DATA block count; the FIGS block itself holds no img: keys.
    ids = list(dict.fromkeys(re.findall(r"\bimg\s*:\s*['\"]([^'\"]+)['\"]", BLOCK.sub("", raw))))
    figs, missing, total = {}, [], 0
    for fid in ids:
        f = next((figdir / f"{fid}{ext}" for ext in MIME if (figdir / f"{fid}{ext}").exists()), None)
        if not f:
            missing.append(fid)
            continue
        b = f.read_bytes()
        total += len(b)
        figs[fid] = "data:" + MIME[f.suffix] + ";base64," + base64.b64encode(b).decode()
        print(f"  {fid:<40} {len(b) / 1024:7.1f} KB")
    unused = sorted({p.stem for p in figdir.iterdir() if p.suffix in MIME and not p.stem.endswith(".preview")} - set(ids))
    body = ",\n".join(f"{json.dumps(k)}:{json.dumps(v)}" for k, v in figs.items())
    art.write_text(BLOCK.sub(lambda _: "/*FIGS-BEGIN*/{\n" + body + "\n}/*FIGS-END*/", raw), encoding="utf-8")
    print(f"inlined {len(figs)} figures, {total / 1024 / 1024:.2f} MB of images; "
          f"artifact now {art.stat().st_size / 1024 / 1024:.2f} MB")
    if unused:
        print("unused files in figdir (not referenced by any img:): " + ", ".join(unused))
    if missing:
        print("MISSING (referenced, no file): " + ", ".join(missing))
        sys.exit(1)


# ------------------------------------------------------------------------ main
def main(a):
    if len(a) < 2 or a[0] not in ("find", "page", "prep", "inline"):
        print(__doc__)
        sys.exit(2)
    if a[0] == "find":
        cmd_find(a[1])
    elif a[0] == "page":
        if len(a) != 4:
            die("usage: figures.py page <paper.pdf> <page> <outdir>")
        cmd_page(a[1], a[2], a[3])
    elif a[0] == "inline":
        if len(a) != 3:
            die("usage: figures.py inline <artifact.html> <figdir>")
        cmd_inline(a[1], a[2])
    else:
        if len(a) < 4:
            die("usage: figures.py prep <src> <figdir> <id> [options]")
        opts, rest = {}, a[4:]
        i = 0
        while i < len(rest):
            k = rest[i]
            if k == "--no-trim":
                opts["no_trim"] = True
                i += 1
                continue
            if k not in ("--page", "--crop", "--max-width", "--max-kb") or i + 1 >= len(rest):
                die("unknown or incomplete option: " + k)
            opts[k[2:].replace("-", "_")] = rest[i + 1]
            i += 2
        cmd_prep(a[1], a[2], a[3], opts)


if __name__ == "__main__":
    main(sys.argv[1:])
