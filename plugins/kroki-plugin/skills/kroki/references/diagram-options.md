# Diagram Options Reference

Options are passed via JSON `diagram_options`, query parameters, or
`Kroki-Diagram-Options-{Key}: value` HTTP headers. JSON body takes precedence
over headers, which take precedence over query parameters.

---

## BlockDiag family
Applies to: `blockdiag`, `seqdiag`, `actdiag`, `nwdiag`, `packetdiag`, `rackdiag`

| Option | Values | Notes |
|---|---|---|
| `antialias` | flag (empty string `""`) | Anti-alias filter on output image |
| `no-transparency` | flag | Disable transparent background (PNG only) |
| `size` | `{W}x{H}` e.g. `320x240` | Output image size |
| `no-doctype` | flag | Omit doctype tag (SVG only) |

---

## D2

| Option | Values | Notes |
|---|---|---|
| `theme` | `0`–`301` (see list below) | Visual theme |
| `layout` | `dagre` (default), `elk` | Layout engine |
| `sketch` | flag (empty `""`) | Hand-drawn aesthetic |

D2 theme IDs:
- `0` default, `1` neutral-gray, `3` flagship-terrastruct, `4` cool-classics,
  `5` mixed-berry-blue, `6` grape-soda, `7` aubergine, `8` colorblind-clear,
  `100` vanilla-nitro-cola, `101` orange-creamsicle, `102` shirley-temple,
  `103` earth-tones, `104` everglade-green, `105` buttered-toast,
  `200` dark-mauve, `300` terminal, `301` terminal-grayscale

---

## Ditaa

| Option | Values | Notes |
|---|---|---|
| `no-antialias` | any | Turn off anti-aliasing |
| `no-separation` | any | Don't separate common shape edges |
| `round-corners` | any | Render all corners as round |
| `scale` | double (default `1.0`) | Size multiplier |
| `no-shadows` | any | Disable drop-shadow effect |
| `tabs` | integer | Tab width in spaces (default 8) |

---

## GraphViz

| Option | Values | Notes |
|---|---|---|
| `layout` | `dot` (default), `neato`, `fdp`, `sfdp`, `twopi`, `circo` | Layout engine |
| `scale` | double (default `72.0`) | Input scale for pos attribute |
| `graph-attribute-{name}` | any | Set a graph attribute (`-G` flag) |
| `node-attribute-{name}` | any | Set a default node attribute (`-N` flag) |
| `edge-attribute-{name}` | any | Set a default edge attribute (`-E` flag) |

---

## Mermaid

Mermaid config keys use camelCase internally; Kroki requires kebab-case, and
dot-separated sub-keys use underscore prefix instead of dot.

Examples:
- `htmlLabels` → `html-labels`
- `er.titleTopMargin` → `er_title-top-margin`

Options are case-insensitive in Kroki.

Unavailable for security reasons: `maxTextSize`, `securityLevel`, `secure`, `startOnLoad`.

Full config reference: https://github.com/mermaid-js/mermaid/blob/master/packages/mermaid/src/config.type.ts

Commonly useful:
| Mermaid key | Kroki option | Example value |
|---|---|---|
| `theme` | `theme` | `dark`, `forest`, `neutral`, `base` |
| `fontSize` | `font-size` | `16` |
| `flowchart.curve` | `flowchart_curve` | `basis`, `linear`, `step` |

---

## PlantUML

| Option | Values | Notes |
|---|---|---|
| `theme` | string (see list below) | Prepends `!theme` directive |
| `no-metadata` | flag | Omit source in SVG/PNG metadata |

PlantUML themes: `amiga`, `black-knight`, `bluegray`, `blueprint`, `cerulean`,
`cerulean-outline`, `crt-amber`, `crt-green`, `cyborg`, `cyborg-outline`, `hacker`,
`hacker-hold`, `lightgray`, `materia`, `materia-outline`, `metal`, `mimeograph`,
`minty`, `plain`, `resume-light`, `sandstone`, `silver`, `sketchy`, `sketchy-outline`,
`spacelab`, `superhero`, `superhero-outline`, `united`

---

## Structurizr

| Option | Values | Notes |
|---|---|---|
| `view-key` | string | Key of the view to render (if workspace has multiple views) |
| `output` | `diagram`, `legend` | Select output type for the view |

---

## Svgbob

| Option | Default | Notes |
|---|---|---|
| `background` | `white` | Backdrop fill colour |
| `font-family` | `arial` | Text font |
| `font-size` | `14` | Text font size (integer) |
| `fill-color` | `black` | Solid shape fill colour |
| `scale` | `1` | Scale factor for the entire SVG |
| `stroke-width` | `2` | Line stroke width |

---

## Symbolator

| Option | Default | Notes |
|---|---|---|
| `component` | (last) | Select which component to render |
| `transparent` | flag | Transparent background instead of white |
| `title` | `""` | Insert title into diagram |
| `scale` | `1.0` | Scale factor |
| `no-type` | flag | Omit port type info |
| `library-name` | `""` | Add library name (requires `title`) |
