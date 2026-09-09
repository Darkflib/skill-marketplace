# Current GitHub Action Versions - Usage Guide

A reference list of current minimum versions for common GitHub Actions. Use it when creating or editing workflows so you don't pin outdated actions that produce deprecation warnings or fail CI.

## Use Cases

- **Authoring workflows**: pick current action versions for a new `.github/workflows/*.yml`
- **Maintenance**: bump existing workflows off deprecated versions
- **Review**: check whether a workflow's pinned versions are still current

## Quick Usage

Once installed, ask Claude things like:

- "Add a GitHub Actions workflow to build and publish this"
- "Update the action versions in my workflow"
- "Are these actions out of date?"

The skill triggers automatically when Claude creates or changes GitHub workflow files.

## What it covers

Minimum versions for the most common actions, grouped by area: core `actions/*` (`checkout`, `setup-python`/`node`/`go`/`java`, `cache`, `upload-artifact` / `download-artifact`, `github-script`, `create-github-app-token`), the `docker/*` build actions, release & publish (`softprops/action-gh-release`, `pypa/gh-action-pypi-publish`, `astral-sh/setup-uv`, `goreleaser`), supply chain & security (`actions/attest*`, `github/codeql-action`, `sigstore/cosign-installer`, `anchore/sbom-action`, `gitleaks`, `trivy`), GitHub Pages, PR & repo automation (`peter-evans/*`, `dorny/paths-filter`, `labeler`, `stale`), language tooling, and infra/deploy (`setup-terraform`, `tflint`, `wrangler-action`, `slack-github-action`). It also covers SHA-pinning conventions and how to check a version that isn't listed.

These are **floors** — newer versions are fine; older ones are what produce the warnings. See `skills/current-github-action-versions/SKILL.md` for the full list, which is the source of truth and the file to update as actions release new majors.

## Maintenance

When an action ships a new major version that deprecates the current one, update the corresponding line in `SKILL.md`. No code to change — it's a single reference document.
