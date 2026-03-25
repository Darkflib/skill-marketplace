---
name: kroki
description: >
  Generate diagrams from plain text using a Kroki server. Use this skill whenever
  the user wants to create, render, or export a diagram of any kind — architecture
  diagrams, sequence diagrams, flowcharts, ERDs, C4 diagrams, Gantt charts, network
  diagrams, mind maps, and more — using any supported text-based diagram language
  such as PlantUML, Mermaid, GraphViz/DOT, D2, Structurizr, Ditaa, Svgbob, Excalidraw,
  or others. Trigger on phrases like "draw a diagram", "generate a sequence diagram",
  "render this PlantUML", "create a C4 diagram", "make a flowchart", "export this
  to SVG/PNG", or any request to turn text-based diagram source into an image file.
  Always use this skill rather than trying to render diagrams via other means.
---

# Kroki Diagram Generation Skill

Kroki exposes a unified HTTP API in front of many diagram renderers. Send diagram
source as plain text (POST); receive SVG, PNG, or PDF.

## Server Configuration

**Default:** `http://localhost:8000`

The user may override this with a different host/port (e.g. `https://kroki.io` for
the public instance, or `http://kroki.internal:8000` for a private deployment). If
the user specifies a server, use that; otherwise assume `http://localhost:8000`.

Check server liveness before rendering if there's any doubt:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
```
A `200` response confirms the server is up. Kroki's Docker default port is `8000`.

## Supported Diagram Types

| Type identifier | Language / tool |
|---|---|
| `plantuml` | PlantUML (UML, C4, etc.) |
| `mermaid` | Mermaid.js |
| `graphviz` | GraphViz / DOT |
| `d2` | D2 |
| `structurizr` | Structurizr DSL (C4 model) |
| `ditaa` | Ditaa (ASCII art → diagram) |
| `svgbob` | Svgbob (ASCII art → SVG) |
| `excalidraw` | Excalidraw (JSON source) |
| `blockdiag` | BlockDiag |
| `seqdiag` | SeqDiag |
| `actdiag` | ActDiag |
| `nwdiag` | NwDiag (network) |
| `packetdiag` | PacketDiag |
| `rackdiag` | RackDiag |
| `c4plantuml` | C4-PlantUML shorthand |
| `nomnoml` | Nomnoml |
| `bpmn` | BPMN (XML) |
| `bytefield` | Bytefield |
| `wavedrom` | WaveDrom (digital timing) |
| `vega` | Vega (data visualisation) |
| `vegalite` | Vega-Lite |
| `pikchr` | Pikchr |
| `umlet` | UMLet |

Not every type supports every output format. SVG is safest for most types.
PNG is available for most. PDF is available for PlantUML and a few others.

## Quick Reference: Making Requests

### Simplest POST (plain text body, recommended)

```bash
curl -s -X POST \
  http://localhost:8000/{diagram_type}/{output_format} \
  -H "Content-Type: text/plain" \
  --data-binary @diagram.{ext} \
  -o output.{output_format}
```

Example — Mermaid to SVG:
```bash
curl -s -X POST \
  http://localhost:8000/mermaid/svg \
  -H "Content-Type: text/plain" \
  --data-binary @diagram.mmd \
  -o diagram.svg
```

### Inline source (no file needed)

```bash
curl -s -X POST \
  http://localhost:8000/plantuml/svg \
  -H "Content-Type: text/plain" \
  -d '@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi!
@enduml' \
  -o sequence.svg
```

### JSON POST (useful when passing options)

```bash
curl -s -X POST \
  http://localhost:8000/ \
  -H "Content-Type: application/json" \
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

### Python helper (use when bash is awkward)

```python
import requests
import sys

def kroki_render(
    source: str,
    diagram_type: str,
    output_format: str = "svg",
    server: str = "http://localhost:8000",
    options: dict | None = None,
) -> bytes:
    """Render diagram source via Kroki POST API."""
    if options:
        payload = {
            "diagram_source": source,
            "diagram_type": diagram_type,
            "output_format": output_format,
            "diagram_options": options,
        }
        resp = requests.post(
            f"{server}/",
            json=payload,
            timeout=30,
        )
    else:
        resp = requests.post(
            f"{server}/{diagram_type}/{output_format}",
            content=source.encode(),
            headers={"Content-Type": "text/plain"},
            timeout=30,
        )
    resp.raise_for_status()
    return resp.content


if __name__ == "__main__":
    src = sys.stdin.read()
    data = kroki_render(src, diagram_type="mermaid", output_format="svg")
    sys.stdout.buffer.write(data)
```

## Workflow

1. **Identify diagram type** from user request or existing source file.
2. **Choose output format**: SVG (default, scalable, viewable inline), PNG (raster,
   for embedding in docs), PDF (for PlantUML/print).
3. **Locate or generate source** — if the user hasn't provided source, write it now
   using the appropriate language. See `references/diagram-syntax.md` for quick-start
   examples in each language.
4. **Save source to a temp file** in `/home/claude/` before POSTing; makes debugging
   and iteration easier.
5. **POST to Kroki** using curl (preferred for simplicity) or the Python helper above.
6. **Save output** to `/mnt/user-data/outputs/` using a descriptive filename.
7. **Present the file** to the user via `present_files`.
8. **Iterate** if the user wants style/layout changes — apply diagram options (see
   `references/diagram-options.md`) or edit the source.

## Output File Naming

Use a descriptive stem, not `output.svg`:
- `sequence-auth-flow.svg`
- `c4-container-myapp.png`
- `erd-users.svg`

## Error Handling

| HTTP status | Meaning | Action |
|---|---|---|
| `400` | Invalid diagram source | Show the error body to the user; fix the syntax |
| `404` | Unknown diagram type | Check the type identifier spelling |
| `500` | Renderer error | Check server logs; simplify the diagram |
| Connection refused | Kroki not running | Tell the user; suggest `docker run` command |

If the server is unreachable, suggest starting Kroki locally:
```bash
docker run --rm -p 8000:8000 yuzutech/kroki
```

## Diagram Options

Options customise rendering (theme, layout engine, scale, etc.) and vary by diagram
type. Pass them via the `diagram_options` JSON field or as query parameters on GET.

For a full options reference, see `references/diagram-options.md`.

Most commonly used:
- **PlantUML** — `theme`: e.g. `cyborg`, `blueprint`, `sketchy`
- **GraphViz** — `layout`: `dot` (default), `neato`, `fdp`, `circo`, `twopi`
- **D2** — `theme`: `0`–`301`; `sketch`: `""` (hand-drawn); `layout`: `dagre`/`elk`
- **Mermaid** — any camelCase Mermaid config key, converted to kebab-case
- **Svgbob** — `scale`, `stroke-width`, `fill-color`, `font-size`

## Reference Files

- `references/diagram-syntax.md` — Quick-start source examples for every major type
- `references/diagram-options.md` — Full options tables per diagram type

Read a reference file when you need a syntax reminder or a full options list.
