---
name: codex-review
description: Get an independent code review from the Codex CLI (a different model family, which surfaces different bugs than another Claude session), then verify and triage its findings. Use when the user asks for a Codex review, a second opinion, "get codex to look at this", or a review before committing, merging or opening a PR. Not for questions about code, and not a substitute for running the tests.
---

# Codex review

Run `codex exec review` non-interactively on a change, read what it finds, check each finding
against the code yourself, and give the user a triaged list. Codex runs read-only: it never edits
files, and neither do you until the user picks what to fix.

Verified on 2026-11-16 against **codex-cli 0.168.0** on macOS. Flags change between Codex
releases: if a command below is rejected, check `codex exec review --help` before working around it.

## Before running

1. `command -v codex`. If it is missing, stop and tell the user. Do not review it yourself under
   this skill (see "If it cannot run").
2. The repository must be a git repo. Run `git status --short` and `git log --oneline -1`.
3. Pick the scope:
   - **Uncommitted changes** (default when the tree is dirty): `git diff HEAD` plus untracked files.
   - **This branch** (default when the tree is clean and you are not on the default branch): the
     commits since the merge base with the base branch (`main`/`master`, or whatever the user names).
   - **One commit**: a SHA the user names.
   - **Specific files or a PR**: only when the user asks.
   If none of these applies (clean tree on the default branch), ask what to review.

## Write the brief

Codex cannot see this conversation. Write the brief to a file in the scratchpad directory (not in
the repo) and pass it on stdin. That avoids every shell-quoting problem with backticks, `$` and
quotes in the text.

The brief contains:

- **Scope**, stated plainly, e.g. "Review the uncommitted changes in this repository (`git diff HEAD`
  plus untracked files from `git status`)" or "Review the commits on this branch since
  `git merge-base HEAD main`".
- **Intent**: what the change is supposed to do, in the user's terms (from the task, issue or commit
  messages). Bugs are deviations from intent, so this is the most useful line in the brief.
- **Focus**, only if the user gave one (concurrency, security, migrations...).
- "Report findings only; do not edit any file."

Do **not** include your own opinion of the change, what you already checked, or that you think it is
correct. An anchored reviewer tends to agree, and an independent read is the point of using Codex.

`--uncommitted`, `--base` and `--commit` cannot be combined with custom instructions (codex rejects
it). Use them only for a bare review with no intent line. The brief form above is usually better.

## Run it

```bash
cd <repo> && codex exec review -c sandbox_mode='"read-only"' \
  -o <scratchpad>/codex-review-out.md - < <scratchpad>/codex-review-brief.md \
  > <scratchpad>/codex-review-log.txt 2>&1; echo "exit=$?"
```

- Add `-m <model>` only if the user names a model.
- A review takes from twenty seconds to several minutes. Run it with the Bash tool's
  `run_in_background` and wait for the completion notice. Do not poll and do not kill it for being slow.
- One review at a time. If it must be stopped, use SIGINT or SIGTERM, never SIGKILL, so codex can
  clean up its child processes.
- Codex needs network access and its own login. If your shell is sandboxed and the command fails on
  network or permissions, ask to run this one command outside the sandbox.

## If it cannot run

If codex is missing, not logged in, has no network, or the approval is denied: **stop and tell the
user why**, with the tail of the log. Never quietly do the review yourself and present it as Codex's.
The user wants a different model's eyes. You may *offer* a Claude review instead, clearly labelled
as such.

## Read the result

- Exit code non-zero, or an empty or missing output file, means the review **failed**. Report the
  error from the log, and do not say "no issues found".
- Exit 0 with no `[P0]`–`[P3]` items means Codex found nothing. Say so, and say that this is not proof
  (see below).
- Findings look like `- [P1] <title> — <absolute path>:<lines>` followed by an explanation. Convert
  paths to repo-relative links.

## Verify and triage

For every finding, check it against the code before reporting it. Read the lines, and run a cheap
reproduction (a one-liner or a quick test) where one exists. Label each one:

- **Confirmed**: you reproduced it or the code plainly does what Codex says.
- **Plausible**: you could not confirm or refute it cheaply. Say what would settle it.
- **Not a bug**: say why, briefly. Keep it in the list; do not drop disagreements silently.

If you or another Claude session reviewed the same change, mark which findings are **Codex-only**.
Those are the reason to run this.

Report, most severe first: the scope reviewed, the run time, and the triaged findings, each with its
priority, location, one-line claim and your label.

## Then

- Do not fix anything until the user says which findings to fix, unless they already asked you to
  fix what Codex finds. Then fix only the Confirmed ones and list what you skipped.
- After fixes, offer one re-review of the new diff. Stop after two rounds; repeated rounds mostly
  converge on approval rather than finding more.
- Reviewer approval is not verification. Same-model LLM reviewers have been measured approving most
  failing patches. Run the project's tests and point to them, not to the review, as evidence.
- Do not commit, push or comment on a PR unless asked.
