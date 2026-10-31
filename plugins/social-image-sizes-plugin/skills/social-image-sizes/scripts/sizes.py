#!/usr/bin/env python3
"""Query the bundled social media image sizes data.

Usage:
  sizes.py list                         # platforms and their asset ids
  sizes.py show PLATFORM [ASSET]        # full detail for a platform or one asset
  sizes.py search TERM                  # match platform/asset names, labels, notes
  sizes.py check PLATFORM ASSET W H     # does a W x H image fit this asset?
  sizes.py markdown                     # render the whole dataset as Markdown
  sizes.py refresh [OUT]                # download the latest sizes.json from upstream

Stdlib only. Platform matching accepts ids, names and aliases (e.g. "twitter" -> x).
"""

import json
import sys
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "references" / "sizes.json"
UPSTREAM = (
    "https://raw.githubusercontent.com/chuckreynolds/"
    "social-profile-image-sizes/master/data/sizes.json"
)


def load():
    with DATA.open() as f:
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


def cmd_check(data, platform, asset, width, height):
    p = find_platform(data, platform)
    a = find_asset(p, asset)
    w, h = int(width), int(height)
    problems, warnings = [], []
    lo, hi = a.get("min", {}), a.get("max", {})
    if w < lo.get("width", 0) or h < lo.get("height", 0):
        problems.append(f"below minimum {dims(lo)}")
    if w > hi.get("width", w) or h > hi.get("height", h):
        problems.append(f"above maximum {dims(hi)}")
    if "width" in a and "height" in a:
        target = ratio(a["width"], a["height"])
        if abs(ratio(w, h) - target) / target > 0.02:
            problems.append(f"aspect {w}:{h} differs from {a.get('aspect', '?')} ({a['width']}x{a['height']})")
        elif w < a["width"]:
            warnings.append(f"right shape but smaller than recommended {a['width']}x{a['height']}")
    elif "aspect" in a:
        try:
            aw, ah = (float(x) for x in a["aspect"].split(":"))
        except ValueError:
            aw = ah = 0
        if ah and abs(ratio(w, h) - aw / ah) / (aw / ah) > 0.02:
            problems.append(f"aspect {w}:{h} differs from {a['aspect']}")
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
            if "sizes" in a:
                notes.append("sizes: " + ", ".join(f"{s['width']}x{s['height']}" for s in a["sizes"]))
            label = a["label"].replace("|", "\\|") + ("" if a["published"] else " †")
            cell = "; ".join(n for n in notes if n).replace("|", "\\|")
            print(f"| {label} | {a['render']} | {a.get('aspect', '')} | {cell} |")
        print("\nSources: " + "; ".join(f"[{s['title']}]({s['url']})" for s in p["sources"]) + "\n")


def cmd_refresh(out=None):
    target = Path(out) if out else DATA
    with urllib.request.urlopen(UPSTREAM, timeout=30) as r:
        fresh = json.loads(r.read())
    if "platforms" not in fresh or "meta" not in fresh:
        sys.exit("Upstream file has an unexpected shape; not writing it.")
    target.write_text(json.dumps(fresh, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {target} (last_verified {fresh['meta'].get('last_verified')})")


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
