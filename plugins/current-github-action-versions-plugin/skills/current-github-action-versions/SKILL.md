---
name: current-github-action-versions
description: "A list of current versions of github actions. Use when creating or changing github workflows."
---

Make sure the actions versions are at least these. Older versions are producing warnings and deprecation notices.

Versions verified against upstream releases on 2026-09-10. Treat each entry as a **floor**, not a pin — never downgrade a workflow that is already on something newer.

## Core

```
actions/checkout@v7
actions/cache@v6                  # also actions/cache/restore@v6, actions/cache/save@v6
actions/setup-python@v7
actions/setup-node@v7
actions/setup-go@v7
actions/setup-java@v6
actions/upload-artifact@v7
actions/download-artifact@v8
actions/github-script@v9
actions/create-github-app-token@v3
```

## Docker / containers

```
docker/setup-qemu-action@v4
docker/setup-buildx-action@v4
docker/login-action@v4
docker/metadata-action@v6
docker/build-push-action@v7
```

## Release & publish

```
softprops/action-gh-release@v3
pypa/gh-action-pypi-publish@release/v1   # intentionally a branch ref, not a tag
astral-sh/setup-uv@v10
goreleaser/goreleaser-action@v7
stefanzweifel/git-auto-commit-action@v7
```

## Supply chain & security

```
actions/attest@v4
actions/attest-build-provenance@v4
actions/dependency-review-action@v5
github/codeql-action@v4                  # init / analyze / upload-sarif
sigstore/cosign-installer@v4
anchore/sbom-action@v0.24                # v0.x — no floating major tag, pin a minor
gitleaks/gitleaks-action@v3
aquasecurity/trivy-action@v0.36          # v0.x — no floating major tag, pin a minor
```

## GitHub Pages

```
actions/configure-pages@v6
actions/upload-pages-artifact@v5
actions/deploy-pages@v5
```

## PR & repo automation

```
peter-evans/create-pull-request@v8
peter-evans/create-or-update-comment@v5
peter-evans/find-comment@v4
marocchino/sticky-pull-request-comment@v3
amannn/action-semantic-pull-request@v6
dorny/paths-filter@v4
actions/labeler@v7
actions/stale@v11
```

## Language & tooling

```
codecov/codecov-action@v7
golangci/golangci-lint-action@v9
DavidAnson/markdownlint-cli2-action@v24
Swatinem/rust-cache@v2
dtolnay/rust-toolchain@v1                # or @stable / @<toolchain>
ruby/setup-ruby@v1
```

## Infra & deploy

```
hashicorp/setup-terraform@v4
terraform-linters/setup-tflint@v6
cloudflare/wrangler-action@v4
slackapi/slack-github-action@v4          # v1.x is long dead; the API changed at v2
```

## Risky jumps

Most major bumps are runtime upgrades and are safe. These are the ones that change behaviour — check them before bumping, especially on a repo you can't easily re-run.

- **Node 24 runtime (most `actions/*` and `docker/*` majors in this list).** Requires Actions Runner **v2.327.1+**. Irrelevant on GitHub-hosted runners; **update self-hosted runners first** or jobs fail to start. Applies to `setup-python@v6`, `upload-artifact@v6`, `labeler@v6`, `stale@v10`, `codecov-action@v6`, `paths-filter@v4`, `docker/*@v4`/`build-push-action@v7`, and others.
- **`actions/checkout@v7`** — now *blocks* checking out a fork PR head under `pull_request_target` and `workflow_run`. If a workflow deliberately checks out untrusted fork code there, v7 breaks it. That is the safe behaviour; rework the workflow rather than pinning back.
- **`astral-sh/setup-uv@v9`** — default cache pruning disabled. Caches get larger, which can raise Actions cache storage cost.
- **`astral-sh/setup-uv@v10`** — with the default `enable-cache: auto`, the cache is now **disabled entirely** for `pull_request_target`, `workflow_run` and `release` events (cache-poisoning defence). Jobs still pass but lose the cache speedup.
- **`actions/download-artifact@v8`** — hash mismatches now **error by default** (previously tolerated), and the action moved to ESM.
- **`actions/setup-node@v5`** — caches automatically when `package.json` has a `packageManager` field; set `package-manager-cache: false` to opt out. **`@v6`** narrows that auto-caching to npm only.
- **`actions/setup-python@v7`** — the `pip-install` input was removed.
- **`docker/build-push-action@v7`** — removed the deprecated `DOCKER_BUILD_NO_SUMMARY` and `DOCKER_BUILD_EXPORT_RETENTION_DAYS` env vars.
- **`slackapi/slack-github-action@v2`** — full rework of how payloads are sent (YAML payloads, explicit API method selection). **A v1 config will not carry over**; rewrite the step.
- **`DavidAnson/markdownlint-cli2-action`** — majors track markdownlint-cli2 itself, so a bump can introduce new rules that fail docs which previously linted clean.

## Notes

- **Prefer SHA pinning for third-party actions.** Use the full 40-char commit SHA with the version in a trailing comment, which is the convention already used across these repos:
  ```yaml
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
  ```
  Floating major tags (`@v7`) are acceptable for `actions/*` and `docker/*`. Anything else that touches secrets, publishes artifacts, or runs on `pull_request_target` should be SHA-pinned. Dependabot updates SHA pins and refreshes the comment if `.github/dependabot.yml` includes the `github-actions` ecosystem.
- **`@latest` and `@master` are not versions.** Replace them (e.g. `lowlighter/metrics@latest`) with a tag or SHA.
- **Don't guess a version that isn't in this list.** Check upstream instead:
  ```bash
  gh api repos/OWNER/REPO/releases/latest --jq .tag_name
  ```
- **v0.x actions have no stable major tag.** Pin at least the minor (`@v0.24`) or a SHA; `@v0` either doesn't exist or moves across breaking changes.
