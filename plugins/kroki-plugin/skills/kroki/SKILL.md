---
name: kroki
description: >
  Generate diagrams from plain text by POSTing source to a Kroki server. Use
  whenever the user wants to draw, render, generate, or export any text-based
  diagram — architecture, sequence, flowchart, ERD, C4, Gantt, network, state
  machine, mind map, class — in any of Kroki's supported languages (PlantUML,
  Mermaid, GraphViz/DOT, D2, Structurizr, DBML, Ditaa, Svgbob, Excalidraw, TikZ,
  WaveDrom, Vega, etc.). Trigger on phrases like "draw a diagram", "render this
  PlantUML", "create a C4 diagram", "make a flowchart", or any request to turn
  diagram source into SVG, PNG, or PDF. Always use this skill in preference to
  other rendering approaches.
---

# Kroki Diagram Generation Skill

Kroki exposes a unified HTTP API in front of many diagram renderers. Send
diagram source as plain text (POST or deflate+base64-encoded GET); receive
SVG, PNG, or PDF.

## Server Configuration

**Default endpoint:** `http://localhost:8000` — a Kroki instance running
locally (e.g. `docker run --rm -p 8000:8000 yuzutech/kroki`).

Resolution order, if the user hasn't named a server explicitly:

1. `$KROKI_URL` env var, if set.
2. The default above.
3. Public `https://kroki.io` — **only with the user's explicit confirmation**.
   Do not fall back to the public endpoint silently. The public service
   processes every request on shared infrastructure and the diagram source
   travels in cleartext to a third party; that's a privacy concern for anything
   from a private deployment, client work, or anything containing internal
   hostnames, credentials, or business-sensitive structure.

### Liveness check — always run before the first render of a session

The default endpoint may not be running. Do a fast TCP port probe (3–5 s
timeout) before POSTing — it fails quickly and avoids a long curl hang on an
unreachable host. Bash one-liner (substitute host/port for `$KROKI_URL`):

```bash
timeout 5 bash -c '</dev/tcp/localhost/8000' \
  && echo "kroki up" \
  || echo "kroki down"
```

Python equivalent (use when the helper below is already loaded):

```python
import socket

def kroki_up(host: str, port: int = 8000, timeout: float = 5.0) -> bool:
    """TCP-connect probe; True if the port accepts a connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
```

If the probe fails, tell the user the endpoint is unreachable and ask how to
proceed:

1. Try a different host they name.
2. Start a local Kroki container (`docker run --rm -p 8000:8000 yuzutech/kroki`).
3. Confirm use of the public `kroki.io` for this request only.

Do not pick the fallback unilaterally.

## Supported Diagram Types

| Type identifier | Language / tool | PNG? |
|---|---|---|
| `plantuml` | PlantUML (UML, C4, etc.) | yes |
| `c4plantuml` | C4-PlantUML shorthand | yes |
| `mermaid` | Mermaid.js | yes |
| `graphviz` | GraphViz / DOT | yes |
| `d2` | D2 | no (SVG only) |
| `structurizr` | Structurizr DSL (C4 model) | yes |
| `dbml` | DBML (database markup) | no |
| `erd` | ERD | yes |
| `ditaa` | Ditaa (ASCII art → diagram) | yes |
| `svgbob` | Svgbob (ASCII art → SVG) | no |
| `excalidraw` | Excalidraw (JSON source) | no |
| `tikz` | TikZ (LaTeX-style) | yes |
| `blockdiag` | BlockDiag | yes |
| `seqdiag` | SeqDiag | yes |
| `actdiag` | ActDiag | yes |
| `nwdiag` | NwDiag (network) | yes |
| `packetdiag` | PacketDiag | yes |
| `rackdiag` | RackDiag | yes |
| `nomnoml` | Nomnoml | no |
| `bpmn` | BPMN (XML) | no |
| `bytefield` | Bytefield | no |
| `wavedrom` | WaveDrom (digital timing) | no |
| `pikchr` | Pikchr | no |
| `symbolator` | Symbolator (HDL) | no |
| `umlet` | UMLet | yes |
| `vega` | Vega (data visualisation) | yes |
| `vegalite` | Vega-Lite | yes |
| `wireviz` | WireViz (cable harnesses) | yes |

SVG works for every type and is the safe default. PDF is available for
PlantUML, GraphViz, and a handful of others — assume SVG unless asked. A
renderer may also be disabled in a given deployment; a `404` on a known-good
type identifier usually means the renderer isn't enabled on that server.

## Quick Reference: Making Requests

### POST (plain text body) — primary path

```bash
curl -s -X POST \
  http://localhost:8000/{diagram_type}/{output_format} \
  -H "Content-Type: text/plain" \
  --data-binary @diagram.{ext} \
  --max-time 30 \
  -o output.{output_format}
```

Example — Mermaid to SVG:

```bash
curl -s -X POST \
  http://localhost:8000/mermaid/svg \
  -H "Content-Type: text/plain" \
  --data-binary @diagram.mmd \
  --max-time 30 \
  -o diagram.svg
```

### POST (JSON, for diagram options)

```bash
curl -s -X POST \
  http://localhost:8000/ \
  -H "Content-Type: application/json" \
  --max-time 30 \
  -d '{
    "diagram_source": "digraph G { Hello->World }",
    "diagram_type": "graphviz",
    "output_format": "svg",
    "diagram_options": {
      "layout": "neato"
    }
  }' \
  -o output.svg
```

### GET (deflate + base64) — for embedding rendered URLs

Useful when you want a stable URL to drop into a README or a doc you don't
control, so the diagram re-renders on demand instead of being a baked binary.
The source is deflate-compressed, then urlsafe-base64-encoded:

```python
import base64
import zlib

def kroki_url(
    source: str,
    diagram_type: str,
    output_format: str = "svg",
    server: str = "http://localhost:8000",
) -> str:
    """Build a deflate+base64 GET URL for inline embedding."""
    compressed = zlib.compress(source.encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return f"{server}/{diagram_type}/{output_format}/{encoded}"
```

These URLs can get long for non-trivial diagrams. Prefer POST when producing a
file artefact; prefer GET when the diagram source lives in a doc you don't
control and you want re-render-on-load.

### Python helper (sync httpx)

Use when iterating in a script, or when surfacing renderer errors cleanly to
the user:

```python
import httpx
import logging

log = logging.getLogger(__name__)


def kroki_render(
    source: str,
    diagram_type: str,
    output_format: str = "svg",
    server: str = "http://localhost:8000",
    options: dict | None = None,
    timeout: float = 30.0,
) -> bytes:
    """Render diagram source via Kroki POST API.

    Returns raw bytes (SVG text bytes, or PNG/PDF binary).

    Raises:
        httpx.ConnectError: server unreachable.
        httpx.HTTPStatusError: non-2xx response. The renderer's error message
            is in the response body; surface it to the user verbatim — it's
            far more useful than a paraphrase.
    """
    try:
        if options:
            payload = {
                "diagram_source": source,
                "diagram_type": diagram_type,
                "output_format": output_format,
                "diagram_options": options,
            }
            resp = httpx.post(f"{server}/", json=payload, timeout=timeout)
        else:
            resp = httpx.post(
                f"{server}/{diagram_type}/{output_format}",
                content=source.encode("utf-8"),
                headers={"Content-Type": "text/plain"},
                timeout=timeout,
            )
    except httpx.ConnectError as exc:
        log.error("kroki connection failed (%s): %s", server, exc)
        raise

    if resp.status_code >= 400:
        log.error(
            "kroki %s/%s returned %d: %s",
            diagram_type,
            output_format,
            resp.status_code,
            resp.text[:500],
        )
        resp.raise_for_status()

    return resp.content
```

## Workflow

1. **Probe the endpoint** (Liveness check, above) on the first render of a
   session. Skip on subsequent renders unless something has failed.
2. **Identify diagram type** from user request or existing source file.
3. **Choose output format**: SVG (default, scalable, renderable inline), PNG
   (where supported — see table), PDF (PlantUML/GraphViz, for print).
4. **Locate or generate source** — if the user hasn't provided source, write
   it now in the appropriate language. See `references/diagram-syntax.md` for
   quick-start examples per language.
5. **Save source to a temp file** in `/home/claude/` before POSTing — makes
   iteration easy and gives the user something to keep if they want.
6. **POST to Kroki** using curl (simple) or the Python helper (when error
   handling matters).
7. **Save output** to `/mnt/user-data/outputs/` with a descriptive filename.
8. **Surface the result**:
   - SVG → render inline via `show_widget` (read the file and pass the SVG
     content as `widget_code`) and also `present_files` so the user has the
     download. Note Kroki SVGs use hardcoded colours, so they won't pick up
     the theme's CSS vars — that's expected.
   - PNG/PDF → `present_files` only; binary can't render inline.
9. **Iterate** on style/layout — apply diagram options (see
   `references/diagram-options.md`) or edit the source.

## Output File Naming

Descriptive stems, not `output.svg`:

- `sequence-auth-flow.svg`
- `c4-container-mnemon.png`
- `erd-pgvector-tiered.svg`

## Error Handling

| Failure | Meaning | Action |
|---|---|---|
| TCP probe timeout / connection refused | Kroki not reachable | Stop and ask the user how to proceed; do not silently fall back to public Kroki. |
| `400` | Invalid diagram source | Show the response body **verbatim** — Kroki returns the renderer's error message in plaintext. Don't paraphrase; the user can read e.g. PlantUML's "Syntax Error?" ASCII arrow more usefully than a summary. |
| `404` | Unknown diagram type, or renderer disabled on this server | Check the identifier spelling against the table; if correct, the deployment may not have that renderer enabled. |
| `415` | Bad content type | Make sure `Content-Type: text/plain` is set for raw POST. |
| `500` | Renderer crash | Simplify the diagram; check server logs if accessible. |

For TikZ specifically: Kroki's secure mode restricts `\verbatiminput` and a
few other commands. If a TikZ document errors with a security warning, the
user either edits the source or runs their Kroki instance with
`KROKI_SAFE_MODE=UNSAFE` (acceptable for a trusted private instance; not for
anything internet-facing).

## Diagram Options

Options customise rendering (theme, layout engine, scale, etc.) and vary by
diagram type. Pass them via the `diagram_options` JSON field, query
parameters on GET, or `Kroki-Diagram-Options-{Key}: value` HTTP headers.

For a full options reference, see `references/diagram-options.md`.

Common ones:

- **PlantUML** — `theme`: e.g. `cyborg`, `blueprint`, `sketchy`
- **GraphViz** — `layout`: `dot` (default), `neato`, `fdp`, `circo`, `twopi`
- **D2** — `theme`: `0`–`301`; `sketch`: `""` (hand-drawn); `layout`:
  `dagre`/`elk`
- **Mermaid** — any camelCase Mermaid config key, converted to kebab-case
- **Svgbob** — `scale`, `stroke-width`, `fill-color`, `font-size`

## Reference Files

- `references/diagram-syntax.md` — Quick-start source examples per language
- `references/diagram-options.md` — Full options tables per diagram type

Read a reference file when you need a syntax reminder or a full options list.
