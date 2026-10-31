#!/usr/bin/env python3
"""Query the bundled social media image sizes data.

Usage:
  sizes.py list                         # platforms and their asset ids
  sizes.py show PLATFORM [ASSET]        # full detail for a platform or one asset
  sizes.py search TERM                  # match platform/asset names, labels, notes
  sizes.py check PLATFORM ASSET W H     # does a W x H image fit this asset?
  sizes.py markdown                     # render the whole dataset as Markdown
  sizes.py refresh [OUT]                # download the latest sizes.json and rebuild sizes.md

Stdlib only. Platform matching accepts ids, names and aliases (e.g. "twitter" -> x).
"""

import contextlib
import io
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REFERENCES = Path(__file__).resolve().parent.parent / "references"
DATA = REFERENCES / "sizes.json"
MARKDOWN = REFERENCES / "sizes.md"
UPSTREAM = (
    "https://raw.githubusercontent.com/chuckreynolds/"
    "social-profile-image-sizes/master/data/sizes.json"
)


def load():
    with DATA.open(encoding="utf-8") as f:
        return json.load(f)


def find_platform(data, query):
    q = query.lower().strip()
    for p in data["platforms"]:
        names = [p["id"], p["name"]] + p.get("aka", [])
        if q in (n.lower() for n in names):
            return p
    for p in data["platforms"]:
        if q in p["id"] or q in p["name"].lower():
            return p
    sys.exit(f"No platform matching {query!r}. Try: sizes.py list")


def find_asset(platform, query):
    q = query.lower().strip()
    for a in platform["assets"]:
        if q in (a["id"], a["label"].lower()):
            return a
    for a in platform["assets"]:
        if q in a["id"] or q in a["label"].lower():
            return a
    ids = ", ".join(a["id"] for a in platform["assets"])
    sys.exit(f"No asset matching {query!r} on {platform['name']}. Assets: {ids}")


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:g}{unit}" if unit == "B" else f"{n:.0f}{unit}"
        n /= 1024


def dims(d):
    return f"{d.get('width', 'any')} x {d.get('height', 'any')}"


def describe(asset):
    lines = [f"{asset['label']} ({asset['id']})", f"  render:    {asset['render']}"]
    if "aspect" in asset:
        lines.append(f"  aspect:    {asset['aspect']}")
    for key in ("min", "max"):
        if key in asset:
            lines.append(f"  {key}:       {dims(asset[key])}")
    if "sizes" in asset:
        lines.append("  sizes:     " + ", ".join(f"{s['width']}x{s['height']}" for s in asset["sizes"]))
    if "max_bytes" in asset:
        lines.append(f"  max file:  {fmt_bytes(asset['max_bytes'])}")
    if "formats" in asset:
        lines.append(f"  formats:   {', '.join(asset['formats'])}")
    if "qualifier" in asset:
        lines.append(f"  qualifier: {asset['qualifier']}")
    for alt in asset.get("also", []):
        lines.append(f"  also:      {alt['label']} {alt['width']}x{alt['height']} - {alt.get('description', '')}")
    for item in asset.get("detail", []) + asset.get("notes", []):
        lines.append(f"  note:      {item}")
    status = "published (first-party)" if asset["published"] else "UNPUBLISHED convention - not citable"
    lines.append(f"  status:    {status}; verified {asset['verified']}")
    if "source_url" in asset:
        lines.append(f"  source:    {asset['source_url']}")
    return "\n".join(lines)


def cmd_list(data):
    print(f"Data last verified {data['meta']['last_verified']} (units: {data['meta']['units']})")
    for p in data["platforms"]:
        print(f"{p['id']:<24} {', '.join(a['id'] for a in p['assets'])}")


def cmd_show(data, platform, asset=None):
    p = find_platform(data, platform)
    if asset:
        print(describe(find_asset(p, asset)))
        return
    print(p["name"] + (f" - {p['subtitle']}" if "subtitle" in p else ""))
    if "note" in p:
        print(f"NOTE: {p['note']}")
    print()
    print("\n\n".join(describe(a) for a in p["assets"]))
    print("\nSources:")
    for s in p["sources"]:
        print(f"  {s['title']}: {s['url']}")


def cmd_search(data, term):
    t = term.lower()
    hits = 0
    for p in data["platforms"]:
        for a in p["assets"]:
            blob = json.dumps([p["id"], p["name"], p.get("aka", []), a]).lower()
            if t in blob:
                hits += 1
                print(f"{p['id']}/{a['id']}: {a['label']} - {a['render']}")
    if not hits:
        print(f"No matches for {term!r}")


def ratio(w, h):
    return w / h if h else 0


RATIO = r"(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)"
TOLERANCE = 0.02


def close(r, target):
    return abs(r - target) / target <= TOLERANCE


def primary_ratio(a):
    """The asset's main aspect ratio, from width/height or the aspect string."""
    if "width" in a and "height" in a:
        return ratio(a["width"], a["height"])
    m = re.fullmatch(RATIO, a.get("aspect", ""))
    return ratio(float(m[1]), float(m[2])) if m else None


def alternatives(a):
    """Other accepted shapes: `also` alternates, plus ratios the prose says are also accepted."""
    alts = [(f"{x['width']}x{x['height']}", ratio(x["width"], x["height"]))
            for x in a.get("also", []) if x.get("label") == "alternate"]
    for text in [a.get("qualifier", "")] + a.get("detail", []):
        if "also" in text.lower():
            alts += [(f"{m[1]}:{m[2]}", ratio(float(m[1]), float(m[2]))) for m in re.finditer(RATIO, text)]
    return alts


def ratio_range(a):
    """An "A:B to C:D" aspect range stated in the asset's prose, as (low, high)."""
    for text in [a.get("qualifier", "")] + a.get("detail", []):
        m = re.search(RATIO + r"\s+to\s+" + RATIO, text)
        if m:
            r1, r2 = ratio(float(m[1]), float(m[2])), ratio(float(m[3]), float(m[4]))
            return min(r1, r2), max(r1, r2), f"{m[1]}:{m[2]} to {m[3]}:{m[4]}"
    return None


def cmd_check(data, platform, asset, width, height):
    p = find_platform(data, platform)
    a = find_asset(p, asset)
    w, h = int(width), int(height)
    if w <= 0 or h <= 0:
        sys.exit(f"Width and height must be positive integers, got {w}x{h}")
    problems, warnings = [], []
    r = ratio(w, h)
    target = primary_ratio(a)
    shape_ok = target is None or close(r, target)
    alt = None
    if not shape_ok:
        alt = next((label for label, ar in alternatives(a) if close(r, ar)), None)
    rng = ratio_range(a)

    # min/max describe the primary shape; an alternative shape has its own limits in prose
    lo, hi = (a.get("min", {}), a.get("max", {})) if alt is None else ({}, {})
    if w < lo.get("width", 0) or h < lo.get("height", 0):
        problems.append(f"below minimum {dims(lo)}")
    if w > hi.get("width", w) or h > hi.get("height", h):
        # some maxes are display sizes the platform scales down to, not upload limits
        if re.search(r"displays up to|resized", a.get("qualifier", ""), re.I):
            warnings.append(f"above display maximum {dims(hi)}; the platform scales it down")
        else:
            problems.append(f"above maximum {dims(hi)}")

    if "exact" in a["render"].lower() and (w, h) != (a.get("width"), a.get("height")):
        problems.append(f"must be exactly {a['width']}x{a['height']}")
    elif alt:
        warnings.append(f"matches alternative {alt}, not the primary {a.get('aspect', '?')}; check notes for its limits")
    elif not shape_ok:
        accepted = ", ".join(label for label, _ in alternatives(a))
        problems.append(f"aspect {w}:{h} differs from {a.get('aspect', '?')}"
                        + (f" ({a['width']}x{a['height']})" if "height" in a else "")
                        + (f"; accepted alternatives: {accepted}" if accepted else ""))
    elif "width" in a and "height" in a and w < a["width"]:
        warnings.append(f"right shape but smaller than recommended {a['width']}x{a['height']}")

    if rng and not (rng[0] * (1 - TOLERANCE) <= r <= rng[1] * (1 + TOLERANCE)):
        problems.append(f"aspect {w}:{h} is outside the supported range {rng[2]}")
    if target is None and rng is None and "sizes" not in a:
        warnings.append("no structured aspect ratio for this asset; read its notes")
    if "sizes" in a and not any(s["width"] == w and s["height"] == h for s in a["sizes"]):
        problems.append("not one of the required sizes: " + ", ".join(f"{s['width']}x{s['height']}" for s in a["sizes"]))
    print(f"{p['name']} / {a['label']}: {w}x{h}")
    for x in warnings:
        print(f"  warning: {x}")
    if problems:
        print("\n".join(f"  - {x}" for x in problems))
        sys.exit(1)
    print("  OK")


def cmd_markdown(data):
    m = data["meta"]
    print(f"# {m['title']}\n")
    print(f"Source: {m['repository']} ({m['license']}). Last verified {m['last_verified']}. Units: {m['units']}.\n")
    print(f"`published: false` (marked † below): {m['about_published_flag']}\n")
    for p in data["platforms"]:
        title = p["name"] + (f" ({p['subtitle']})" if "subtitle" in p else "")
        print(f"## {title}\n")
        if "note" in p:
            print(f"> {p['note']}\n")
        print("| Asset | Size | Aspect | Notes |")
        print("|---|---|---|---|")
        for a in p["assets"]:
            notes = [a.get("qualifier", "")]
            notes += [f"{x['label']}: {x['width']}x{x['height']}" for x in a.get("also", [])]
            notes += a.get("detail", []) + a.get("notes", [])
            if "formats" in a:
                notes.append("formats: " + ", ".join(a["formats"]))
            if "sizes" in a:
                notes.append("sizes: " + ", ".join(f"{s['width']}x{s['height']}" for s in a["sizes"]))
            label = a["label"].replace("|", "\\|") + ("" if a["published"] else " †")
            cell = "; ".join(n for n in notes if n).replace("|", "\\|")
            print(f"| {label} | {a['render']} | {a.get('aspect', '')} | {cell} |")
        print("\nSources: " + "; ".join(f"[{s['title']}]({s['url']})" for s in p["sources"]) + "\n")


META_KEYS = ("title", "repository", "license", "last_verified", "units", "about_published_flag")
PLATFORM_KEYS = ("id", "name", "sources", "assets")
ASSET_KEYS = ("id", "label", "render", "published", "verified")


def validate(data):
    """Return a list of missing required fields; empty means the shape is usable."""
    missing = [f"meta.{k}" for k in META_KEYS if k not in data.get("meta", {})]
    if not isinstance(data.get("platforms"), list):
        return missing + ["platforms"]
    for p in data["platforms"]:
        missing += [f"{p.get('id', '?')}.{k}" for k in PLATFORM_KEYS if k not in p]
        for a in p.get("assets", []):
            missing += [f"{p.get('id', '?')}/{a.get('id', '?')}.{k}" for k in ASSET_KEYS if k not in a]
    return missing


def write_atomic(path, text):
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def cmd_refresh(out=None):
    target = Path(out) if out else DATA
    with urllib.request.urlopen(UPSTREAM, timeout=30) as r:
        fresh = json.loads(r.read().decode("utf-8"))
    missing = validate(fresh)
    if missing:
        sys.exit("Upstream file is missing required fields; not writing it:\n  " + "\n  ".join(missing[:20]))
    # upstream points at a schema.json it doesn't ship alongside the data
    fresh.pop("$schema", None)
    write_atomic(target, json.dumps(fresh, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {target} (last_verified {fresh['meta']['last_verified']})")
    if out is None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_markdown(fresh)
        write_atomic(MARKDOWN, buf.getvalue())
        print(f"Regenerated {MARKDOWN}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, args = argv[0], argv[1:]
    if cmd == "refresh":
        return cmd_refresh(*args)
    data = load()
    commands = {
        "list": cmd_list,
        "show": cmd_show,
        "search": cmd_search,
        "check": cmd_check,
        "markdown": cmd_markdown,
    }
    if cmd not in commands:
        sys.exit(f"Unknown command {cmd!r}\n{__doc__}")
    commands[cmd](data, *args)


if __name__ == "__main__":
    main(sys.argv[1:])
