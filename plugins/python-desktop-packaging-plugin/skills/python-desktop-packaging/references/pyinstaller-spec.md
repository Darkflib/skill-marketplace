# PyInstaller spec traps

## Package metadata is not collected

`importlib.metadata.version("foo")` returns nothing inside a bundle unless the
spec asks for the dist-info explicitly:

```python
from PyInstaller.utils.hooks import copy_metadata
datas += copy_metadata("pywebview")
```

Two consequences beyond a missing version string:

- Any runtime code doing capability detection via metadata silently degrades.
- **SBOM scanners pointed at the artefact see almost no Python packages.** A
  Syft scan of a real bundle returned 14 packages, of which exactly one was a
  Python distribution — the one with `copy_metadata`. Everything else it found
  was native: the interpreter, libzstd, systemd, gcc runtime.

If you want a scanner to see the dependency graph, either collect metadata for
everything or generate the dependency SBOM from the lockfile instead. The
lockfile route is better anyway; see `ci-workflows.md`.

## `collect_data_files` is platform-blind

It collects everything the package ships, for every platform. A macOS `.app`
built with `collect_data_files("webview")` contained seven Windows DLLs:

```
webview/lib/WebBrowserInterop.x64.dll
webview/lib/Microsoft.Web.WebView2.WinForms.dll
webview/lib/runtimes/win-arm64/native/WebView2Loader.dll
...
```

Dead weight, and worse, SBOM noise: a scan of the Linux artefact reported
Microsoft Edge WebView2 as a component, which would send anyone doing
vulnerability triage on a false trail.

Filter by platform:

```python
datas += [
    (src, dst)
    for src, dst in collect_data_files("webview")
    if not _foreign_platform_lib(src)
]
```

Check what a collection actually pulled in — `find` the bundle for `.dll`,
`.so`, `.dylib` that have no business on the target — rather than trusting the
helper.

## Read the version without importing the package

The build environment is not the app environment. Parse it out:

```python
VERSION = re.search(
    r'__version__ = "([^"]+)"', (PKG_DIR / "__init__.py").read_text(encoding="utf-8")
).group(1)
```

## Guard the platform-specific parts

`BUNDLE` only exists meaningfully on macOS. Everything after `COLLECT` should be
conditional so the same spec produces a sane directory build elsewhere:

```python
if sys.platform == "darwin":
    app = BUNDLE(coll, name=f"{APP_NAME}.app", bundle_identifier=..., info_plist={...})
```

`LSMinimumSystemVersion` in the plist is a claim you are making, not something
derived from the build. Check what you actually produced:

```bash
find MyApp.app -type f \( -name '*.so' -o -name '*.dylib' \) -print0 \
  | xargs -0 -n1 vtool -show-build | grep minos | sort | uniq -c
```

Set the plist value from that, deliberately.

## Console vs windowed

`console=False` produces a GUI-subsystem executable on Windows with no console
attached. That is correct for the shipped app, and it is why the self-test needs
a report file rather than stdout. Do not solve this by shipping a second console
executable unless the app genuinely has a CLI.
