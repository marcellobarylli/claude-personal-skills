#!/usr/bin/env python3
"""Read-only scan of the home layout for the audit-and-cleanup skill.

Two parts, so the heavy work runs in a Slurm job:
  live  login node, seconds: layout listing, git worktrees, tmux panes, process cwds, Slurm jobs.
  deep  sbatch job: sizes of every candidate and a search for references to each candidate path.

Both write JSON into --out. Nothing is moved, deleted or written outside --out.
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
ALLOWED_TOP = {"workspace", "data", "sandboxes", "bin"}
KNOWN_DOT = {".bashrc", ".bash_logout", ".bash_history", ".profile", ".cache", ".config", ".local", ".ssh",
             ".claude", ".claude.json", ".codex", ".gitconfig", ".netrc", ".apptainer", ".conda", ".mamba",
             ".npm", ".nv", ".pki", ".triton", ".vscode-server", ".wget-hsts", ".zcompdump", ".dspy_cache", ".warp"}
BACKUP_RE = re.compile(r"\.(bak|orig|old)([-.]?\w*)?$|~$")
TEXT_EXT = {".sh", ".sbatch", ".slurm", ".py", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".md", ".txt",
            ".conf", ".env", ".r", ".R", ".jl", ".ipynb", ".mk", ""}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "site-packages", ".ruff_cache"}
MAX_TEXT = 2 * 1024 * 1024


def run(cmd, cwd=None):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60).stdout
    except Exception as e:  # tool missing or timed out
        return f"__error__ {e}"


def entry(p: Path):
    st = p.lstat()
    d = {"path": str(p), "name": p.name, "mtime": time.strftime("%Y-%m-%d", time.localtime(st.st_mtime))}
    if p.is_symlink():
        d["kind"] = "symlink"
        d["target"] = os.readlink(p)
        d["target_exists"] = p.exists()
    else:
        d["kind"] = "dir" if p.is_dir() else "file"
    return d


def git_info(repo: Path):
    info = {"is_git": (repo / ".git").exists()}
    if not info["is_git"]:
        return info
    info["is_linked_worktree"] = (repo / ".git").is_file()
    if info["is_linked_worktree"]:
        info["gitdir"] = (repo / ".git").read_text().strip().removeprefix("gitdir: ")
    info["status_short"] = run(["git", "status", "--porcelain"], cwd=repo).count("\n")
    info["unpushed"] = run(["git", "log", "--oneline", "@{u}..HEAD"], cwd=repo).strip().splitlines()[:20]
    info["branch"] = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo).strip()
    gi = repo / ".gitignore"
    info["gitignores_worktrees"] = gi.exists() and any(
        l.strip().rstrip("/") in (".worktrees", "/.worktrees") for l in gi.read_text(errors="ignore").splitlines())
    wts, cur = [], {}
    for line in run(["git", "worktree", "list", "--porcelain"], cwd=repo).splitlines() + [""]:
        if not line:
            if cur:
                wts.append(cur)
            cur = {}
            continue
        k, _, v = line.partition(" ")
        cur[k] = v or True
    info["worktrees"] = wts
    # untracked or ignored top-level paths inside the repo (outputs that may belong in ~/data)
    out = run(["git", "status", "--porcelain", "--ignored", "--untracked-files=normal"], cwd=repo)
    info["untracked_or_ignored"] = sorted({l[3:].split("/")[0] for l in out.splitlines() if l[:2] in ("??", "!!")})
    return info


def live(out: Path):
    res = {"home": str(HOME), "time": time.strftime("%Y-%m-%d %H:%M")}
    res["top"] = [entry(p) for p in sorted(HOME.iterdir())]
    res["workspace"] = []
    for p in sorted((HOME / "workspace").iterdir()):
        e = entry(p)
        if e["kind"] == "dir":
            e["git"] = git_info(p)
            e["data_folder"] = str(HOME / "data" / p.name.lower())
            e["data_folder_exists"] = (HOME / "data" / p.name.lower()).exists()
        res["workspace"].append(e)
    res["data"] = [entry(p) for p in sorted((HOME / "data").iterdir())]
    res["sandboxes"] = [entry(p) for p in sorted((HOME / "sandboxes").iterdir())] if (HOME / "sandboxes").exists() else []
    res["bin"] = [entry(p) for p in sorted((HOME / "bin").iterdir())] if (HOME / "bin").exists() else []
    readme = HOME / "data" / "README.md"
    res["data_readme"] = readme.read_text() if readme.exists() else None
    res["tmux_panes"] = run(["tmux", "list-panes", "-a", "-F",
                             "#{session_name}\t#{session_created}\t#{session_activity}\t#{pane_current_path}"])
    procs = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.stat(f"/proc/{pid}").st_uid != os.getuid():
                continue
            cwd = os.readlink(f"/proc/{pid}/cwd")
            cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")[:200]
            procs.append({"pid": int(pid), "cwd": cwd, "cmd": cmd})
        except OSError:
            pass
    res["processes"] = procs
    jobs = []
    for line in run(["squeue", "--me", "-h", "-o", "%i"]).split():
        if line.startswith("__error__"):
            break
        show = run(["scontrol", "show", "job", line])
        f = dict(re.findall(r"(\w+)=(\S+)", show))
        jobs.append({k: f.get(k) for k in ("JobId", "JobName", "JobState", "WorkDir", "StdOut", "Command")})
    res["jobs"] = jobs
    res["crontab"] = run(["crontab", "-l"])
    (out / "live.json").write_text(json.dumps(res, indent=1))
    print(out / "live.json")


def walk_size(p: Path):
    total = 0
    for root, dirs, files in os.walk(p, followlinks=False):
        for f in files:
            try:
                total += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return total


def deep(out: Path, candidates):
    live_json = json.loads((out / "live.json").read_text())
    if not candidates:  # default: every non-allowed entry at the top of ~, every workspace entry, every data entry
        candidates = [e["path"] for e in live_json["top"] if not e["name"].startswith(".")
                      and e["name"] not in ALLOWED_TOP]
        candidates += [e["path"] for e in live_json["workspace"]] + [e["path"] for e in live_json["data"]]
    res = {"sizes": {}, "envs": {}, "references": {c: [] for c in candidates}}
    for c in candidates:
        p = Path(c)
        res["sizes"][c] = walk_size(p) if p.is_dir() and not p.is_symlink() else (p.lstat().st_size if p.exists() or p.is_symlink() else 0)
        envs = [str(x.parent) for x in p.rglob("pyvenv.cfg")] if p.is_dir() and not p.is_symlink() else []
        envs += [str(x.parent) for x in p.rglob("conda-meta")] if p.is_dir() and not p.is_symlink() else []
        if envs:
            res["envs"][c] = envs[:50]
    # Patterns: absolute path, ~/rel and $HOME/rel forms of each candidate.
    pats = {}
    for c in candidates:
        rel = os.path.relpath(c, HOME)
        alts = [c, f"~/{rel}", f"$HOME/{rel}", f"${{HOME}}/{rel}"]
        # a match must not continue the name: ~/workspace/proj must not match ~/workspace/proj-r024
        pats[c] = re.compile("(?:" + "|".join(re.escape(x) for x in alts) + r")(?![\w.-])")
    roots = [HOME / "workspace", HOME / "bin", HOME / "data", HOME / ".claude" / "skills",
             HOME / ".claude" / "projects", HOME / "sandboxes"]
    singles = [HOME / ".bashrc", HOME / ".profile", HOME / ".claude" / "CLAUDE.md", HOME / ".claude" / "settings.json",
               HOME / ".gitconfig"]

    own = (str(HOME / "data" / "home-audit") + "/", str(Path(__file__).resolve().parent.parent) + "/")

    def scan_file(fp: Path, shebang_only=False):
        if str(fp).startswith(own):
            return  # the audit's own output and this skill would match every candidate
        try:
            if fp.is_symlink() or fp.stat().st_size > MAX_TEXT:
                return
            data = fp.read_bytes()
        except OSError:
            return
        if shebang_only:
            data = data.split(b"\n", 1)[0]
        if b"\0" in data[:4096]:
            return
        text = data.decode(errors="ignore")
        for c, rx in pats.items():
            inside = str(fp).startswith(c + "/")
            if not rx.search(text):
                continue
            for n, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    # self-references inside the candidate move with it, unless it is an environment (hardcoded prefix)
                    res["references"][c].append({"file": str(fp), "line": n, "inside": inside,
                                                 "text": line.strip()[:200]})
                    break

    for fp in singles:
        if fp.exists():
            scan_file(fp)
    for r in roots:
        for root, dirs, files in os.walk(r, followlinks=False):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            in_bin = os.path.basename(root) == "bin" and any(Path(root, "..", m).exists()
                                                             for m in ("pyvenv.cfg", "conda-meta"))
            for f in files:
                fp = Path(root, f)
                if in_bin:
                    scan_file(fp, shebang_only=True)
                elif f == "pyvenv.cfg" or fp.suffix in TEXT_EXT or f.endswith(".sbatch"):
                    scan_file(fp)
    for c in res["references"]:
        res["references"][c] = res["references"][c][:200]
    (out / "deep.json").write_text(json.dumps(res, indent=1))
    print(out / "deep.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["live", "deep"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--candidate", action="append", default=[], help="absolute path; repeatable (deep only)")
    a = ap.parse_args()
    o = Path(a.out)
    o.mkdir(parents=True, exist_ok=True)
    live(o) if a.part == "live" else deep(o, a.candidate)
