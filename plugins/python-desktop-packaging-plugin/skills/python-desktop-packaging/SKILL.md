---
name: python-desktop-packaging
description: >-
  Package Python desktop apps (PyWebView, PyInstaller, Briefcase, py2app) into
  distributable bundles across macOS, Linux and Windows, and verify the result
  actually works. Use this whenever the user is freezing a Python app into a
  .app/.exe/AppImage, writing or debugging a PyInstaller spec, setting up CI to
  build desktop artefacts, signing or notarising a bundle, producing SBOMs or
  build attestations for a built binary, or asking why something works from
  source but breaks once packaged — even if they only mention one platform, and
  even if they frame it as a CI question rather than a packaging one. The
  failure modes here are silent and platform-specific, so reach for this before
  writing the spec rather than after the bug report.
---

# Packaging Python desktop apps

Packaging fails quietly. The build succeeds, the tests pass, and the artefact is
broken in a way nobody notices until a user double-clicks it. Every practice
here exists to convert a silent failure into a loud one.

## The one rule

**Verify the artefact, not the source tree.** A green test suite proves the
source works under your dev interpreter. It says nothing about whether the
frozen bundle can find its assets, import its GUI backend, or write to disk.

Concretely: the packaged binary must be able to test *itself*, and CI must run
that self-test against the built artefact.

## The self-test contract

Give the app a headless mode that exercises its own guts and exits non-zero on
failure:

```
myapp --self-test --report report.json
```

It should emit JSON covering, at minimum:

| Field | The silent failure it catches |
|---|---|
| `frozen` | You verified the source tree by accident. This is the check that catches the others being meaningless. |
| `resource_root` | `__file__`-relative paths that work in dev and vanish under `sys._MEIPASS`. |
| `assets` | Data files not collected — a blank window. |
| `gui_backend` | No windowing backend bundled. See below; this one is vicious. |
| `dependency versions` | Package metadata stripped from the bundle. |
| `write_check` | The app writing next to its executable, which is read-only once installed. |

`--report PATH` is not a convenience. A Windows GUI-subsystem executable has **no
console attached**, so its stdout goes nowhere when launched from a terminal.
The file is the only output channel that works on all three platforms. Write to
stdout too, wrapped in `contextlib.suppress(OSError)`.

Then a verification script runs the binary, reads the report, and fails loudly.
Keep its platform assumptions honest — asserting a `.app` bundle exists only
makes sense on macOS.

## Cross-compilation: there isn't any

PyInstaller freezes the interpreter it runs under and wraps it in a bootloader
compiled for the host. There is no `--target`. You need one machine per
OS **and** per architecture.

The partial exceptions, in descending order of trustworthiness:

- **macOS `universal2`** works only if the interpreter *and* every native wheel
  are universal2. uv's python-build-standalone and Homebrew are single-arch;
  python.org installers are universal2. Building on each arch and `lipo`-ing is
  less clever and more reliable.
- **Windows under Wine** is documented as possible and explicitly unsupported.
- **Docker** gets you Linux-from-Linux. It does nothing for macOS or Windows.

## The traps, by layer

### Resource resolution
Keep `sys._MEIPASS` handling in exactly one module, and have it raise with
context (`frozen=`, `root=`) rather than returning a path that does not exist.
A missing asset should fail at the call site, not as a blank window later.

### GUI backends are chosen lazily
This is the worst failure mode in the set, because everything else goes green.
pywebview selects its backend at `webview.start()`, not at import. A Linux build
with no GTK or Qt bindings will import cleanly, pass every other check, and die
the instant a user launches it.

Probe it explicitly: try importing the platform backend modules in the
library's own order. Do **not** call the library's own `initialize()` — it
usually also runs app setup with side effects a headless check should not have.
Report which backend resolved, and fail the build when none does.

### Type checkers only know the platform they run on
`mypy` checks `sys.platform` as it finds it. An `os.uname()` call will sail
through a macOS dev loop and a macOS CI job, then fail on Windows. Run
`mypy --platform darwin`, `--platform linux` and `--platform win32` everywhere
you run it, and branch on `sys.platform` rather than `os.name` so the checker
can narrow properly.

### Writable locations
Write to the per-user data directory, never beside the executable. The test
that proves it: mount the built disk image read-only and run the app from there.
If it works, installed users will be fine.

See `references/pyinstaller-spec.md` for spec-level traps — metadata collection,
platform-blind data collection, and an annotated spec.

See `references/ci-workflows.md` for build/release pipeline findings — runner
selection and cost, artefact upload, SBOMs, and attestations.

## Signing, honestly

Ad-hoc signing (`codesign --sign -`) satisfies `codesign --verify --deep
--strict` and runs locally. It does **not** satisfy `spctl --assess`, and the
bundle will not open on anyone else's machine. Say so plainly rather than
letting a green `codesign --verify` imply distributability.

Real distribution needs a Developer ID certificate, the hardened runtime with an
entitlements plist (PyInstaller bundles typically need
`com.apple.security.cs.allow-unsigned-executable-memory`), then `notarytool
submit --wait` and `stapler staple`.

## Reporting results

Report what the build weighs and what it links against, not just that it
succeeded. Bundle sizes diverge sharply by platform — a GUI toolkit the OS
provides on one platform gets vendored on another — and a Linux bundle still
links against the build host's glibc and a graph of system libraries it does not
carry. That makes it non-portable across distros however green the build was,
which is the argument for Flatpak or AppImage rather than a bare tarball.

Build on the oldest OS you intend to support. Watch for hosted-runner image
migrations: they move the glibc floor under you without any change on your side.
