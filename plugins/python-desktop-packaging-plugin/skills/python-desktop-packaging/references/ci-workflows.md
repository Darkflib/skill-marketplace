# Building and releasing desktop artefacts in CI

## Where to run what

Self-hosted runners for ordinary builds; hosted runners for releases. The
reasoning is not only the macOS minutes multiplier:

- A **self-hosted runner cannot produce trustworthy provenance.** The point of
  SLSA build level 2+ is an ephemeral builder the author does not control. So
  the split stops being a budget decision and becomes a security property.
- Hosted runners are a **poor place to test a GUI app.** A headless self-test
  runs anywhere, but opening a real window wants a logged-in session. Your own
  hardware is the better test bed, not merely the cheaper one.

Keep one workflow definition across both — `runs-on` selected by an input —
rather than two drifting systems. Give the CI workflow an input to switch
between self-hosted and hosted runners: while runners are being set up, the
question *"is it my workflow or my runner?"* comes up repeatedly.

Start new workflows as `workflow_dispatch` only. Add push triggers once a green
run on each machine is boring.

## Self-hosted workspaces persist

Clear `dist/` and `build/` at the start of every job. Otherwise a build that
fails to produce a new artefact leaves the old one in place, and verification
passes against last week's binary. `--clean` handles the tool's own cache, not
your output directory.

## A skipped matrix leg still allocates a runner

Gating steps inside a matrix with `if:` does not prevent the runner starting.
One observed release run allocated a macOS runner to skip three steps — billed
at ten times the Linux rate. Filter the matrix itself in a small planning job:

```yaml
  plan:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.pick.outputs.matrix }}
    steps:
      - id: pick
        run: |
          selected="$(echo "$all" | jq -c --arg t "$PLATFORM" '[.[] | select(.target == $t)]')"
          echo "matrix={\"include\":$selected}" >> "$GITHUB_OUTPUT"
  build:
    needs: plan
    strategy:
      matrix: ${{ fromJSON(needs.plan.outputs.matrix) }}
```

Job-level `if:` is evaluated before allocation, so separate jobs with `if:` are
already efficient. It is specifically matrix legs gated at step level that waste
runners.

## Uploading a macOS bundle

`upload-artifact` zips its input, which drops the symlinks and executable bits a
`.app` needs. Tar it first, or what comes back down will not run:

```yaml
- run: tar -czf myapp-macos-${{ runner.arch }}.tar.gz -C dist MyApp.app
```

Linux directory builds want the same treatment for the executable bit. Windows
has neither problem, so the default zip is fine there.

## Two SBOMs, because neither alone is true

**Dependency view** — authoritative for what went in. Build it from a throwaway
environment synced without the dev group, so it lists what is actually frozen
into the bundle rather than pytest and the build tool as well:

```bash
UV_PROJECT_ENVIRONMENT=.venv-sbom uv sync --frozen --no-dev
uvx --from cyclonedx-bom cyclonedx-py environment .venv-sbom \
  --pyproject pyproject.toml --of JSON -o sbom-runtime.cdx.json
```

Doing the sync per-platform matters: the macOS run then lists pyobjc where the
Windows run lists pythonnet, whereas a lockfile-wide export smears all
platforms together into a union that describes no real artefact.

**Artefact view** — catches what the dependency graph never mentions: the
interpreter, the bootloader, vendored native libraries. Scan `dist/` with Syft.

Neither substitutes for the other. The artefact scan cannot see Python packages
whose metadata the freezer stripped; the dependency graph cannot see the native
libraries the freezer added.

## Attestations

`actions/attest-build-provenance` and `actions/attest` (which supersedes the
deprecated `actions/attest-sbom` and takes `sbom-path` directly) need
`id-token: write` and `attestations: write`, and no separate signing
infrastructure. `gh attestation verify` is the consumer side — but it defaults
to the provenance predicate, so finding an SBOM attestation needs
`--predicate-type https://cyclonedx.org/bom` or `https://spdx.dev/Document`.

A verified provenance attestation records `runnerEnvironment: github-hosted`.
That field is the whole argument for keeping releases off self-hosted runners,
in machine-readable form.

**They do not work on user-owned private repositories:**

```
Failed to persist attestation: Feature not available for user-owned private
repositories. To enable this feature, please make this repository public.
```

Note *user-owned*. An org-owned private repository with GitHub Advanced
Security is the route that keeps source closed. The alternatives are making the
repository public, or shipping without attestation.

Give the release workflow an input to disable attestation so the rest of the
pipeline stays runnable while that question is open — but default it **on**. A
release that quietly stops attesting is worse than one that fails loudly.

Frozen output is not bit-reproducible, so the attestation is the only link
between source and binary. Build and attest in the same job, with the artefact
never leaving the runner in between.

## Pinning

SHA-pin third-party actions that touch secrets or publish artefacts, with the
version in a trailing comment, and enable Dependabot's `github-actions`
ecosystem to keep them current. Floating major tags are acceptable for
first-party `actions/*`.

Self-hosted runners must be new enough for the Node runtime the actions target.
An outdated runner does not fail a step — the job never starts.
