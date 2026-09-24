---
name: op-cli
description: "Verified behaviour and traps of the 1Password CLI (`op`) when driven from code: silent no-op edits (exit 0, nothing applied), stdin that must be a real pipe, whole-item round-trips that blank fields, service-account quirks, and how to write secrets without putting them in argv. Use whenever code shells out to `op` (subprocess, asyncio, uvloop/uvicorn, scripts, CI), reads or writes 1Password items or fields programmatically, uses OP_SERVICE_ACCOUNT_TOKEN, or when an `op item edit`/`op item create` \"succeeds\" but nothing changes — even if 1Password isn't named and the symptom is just a secret that won't save."
---

# 1Password CLI (`op`) from code

Verified on 2026-09-24 against **op 2.34.1** with a **service account**, on Debian, by
direct experiment on scratch items. Several plausible-sounding explanations turned out to be wrong
along the way; they're recorded at the end so they don't get rediscovered. Re-verify on a new major
version of `op` — none of this is documented contract.

## The one that costs a day: stdin must be a FIFO

`op item edit` / `op item create` read a JSON item from stdin **only if stdin is a pipe (FIFO)**.
Given any other kind of stdin — notably a **socket** — `op` ignores it, applies an empty edit, and
**exits 0 with nothing on stderr**. The item's `updated_at`/`version` still bump, so it even looks
like something happened.

For `op item create`, the documented form for a piped template is
`op item create - --vault <vault>`, with `-` as the first positional argument. Pass it: 2.34.1
also picks up piped stdin without it (see *Inherited stdin gets eaten*), but relying on that is
relying on undocumented behaviour.

This bites whenever the parent isn't a shell:

| Parent | Child stdin with "PIPE" | `op` reads it? |
|---|---|---|
| shell `cat x \| op …` | FIFO | yes |
| `subprocess.run(input=…)` | FIFO | yes |
| stock `asyncio` `create_subprocess_exec(stdin=PIPE)` | FIFO | yes |
| **uvloop** (default under `uvicorn[standard]`) `stdin=PIPE` | **socketpair** | **no — silent no-op** |
| Node `child_process` `'pipe'` (libuv, like uvloop) | socketpair (inferred, not tested with `op`) | assume **no** |

So code that works in a script or test fails only inside the web server. Don't let the event loop
choose: make the pipe yourself.

```python
import asyncio, os

def _write_all_and_close(fd: int, data: bytes) -> None:
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
    except BrokenPipeError:
        pass  # op exited early; its rc/stderr say why
    finally:
        os.close(fd)

async def op_with_stdin(*args: str, data: bytes) -> tuple[int, bytes, bytes]:
    r, w = os.pipe()                      # a real FIFO, whatever the event loop
    try:
        proc = await asyncio.create_subprocess_exec(
            "op", *args, stdin=r,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    except BaseException:
        os.close(w); raise
    finally:
        os.close(r)
    writer = asyncio.ensure_future(asyncio.to_thread(_write_all_and_close, w, data))
    comm = asyncio.ensure_future(proc.communicate())
    try:
        # shield: a cancelled request must not cancel communicate() mid-drain
        await asyncio.shield(asyncio.gather(writer, comm))
    except BaseException:                 # incl. CancelledError from a dropped request
        if proc.returncode is None:
            proc.kill()                   # cancellation alone doesn't stop the child
        # let communicate() finish draining and reap the child; the writer gets EPIPE
        await asyncio.gather(writer, comm, return_exceptions=True)
        raise
    out, err = comm.result()
    return proc.returncode, out, err
```

To check what a child actually gets: `stat.S_ISFIFO(os.fstat(0).st_mode)` vs `S_ISSOCK` in a tiny
child process under the same loop.

## Never trust the exit code of a write — read back

Because of the above (and any future silent-failure mode), after every `op item edit`:
re-`get` the item and compare the fields you meant to change. On mismatch, raise, and include
`op`'s stderr in the message even though rc was 0 — it's empty in the FIFO case, and "op said:
nothing" is itself the diagnostic.

## Whole-item round-trips blank what you don't send

The piped-JSON edit is a *replace*: a field present in the item but sent **without a `value`** is
emptied. So when editing via stdin:

- start from a fresh `op item get … --format json` of the same item (not a cached copy),
- change only the values you mean to change, send everything else back untouched.

**Items with a passkey are out.** 1Password's docs say JSON templates don't support passkeys:
editing such an item from piped JSON or `--template` overwrites the passkey (not verified here). Check
for a passkey before any round-trip and, if there is one, fall back to assignment syntax — which
puts the value in argv, so for a secret field on such an item stop and tell the user rather than
pick the lesser evil silently. A field-by-field read-back won't notice a lost passkey unless it
checks for one.

Fields **added** to the JSON are created (id/label = your name, `"type": "CONCEALED"` for secrets).
Fields you update keep their existing `id`. No separate "create field" step is needed.

## Keep secrets out of argv

Assignment syntax (`op item edit item 'field[password]=VALUE'`) puts the value in the process list
and shell history. For anything secret, use the piped JSON (above) or `--template=<file>` with a
0600 file on tmpfs (`/dev/shm`), deleted immediately. Both were verified to apply edits; the FIFO
rule doesn't apply to `--template` because it reads a path.

## Reading

- `op item get <item> --vault <v> --format json` **includes CONCEALED values** on 2.34.1; pass
  `--reveal` anyway so a future version that conceals by default can't silently change what you
  send back on a round-trip.
- Human (non-JSON) output conceals unless `--reveal`.
- Match fields by `label` (what people type in the app) with `id` as a fallback; app-created
  custom fields get random ids like `gx2wx3ovcezbqgicff5fdd2fhq`.
- `op read op://vault/item/field` is fine for one value; for several fields of one item, one
  `item get` is one API call instead of N (service accounts are rate-limited — cache briefly).

## Service accounts

- Every item command needs `--vault` (or piped input that names one): *"…called by a service
  account. Please specify one either through the --vault flag or through piped input"*.
- A service account can't see Personal/Private vaults; scope it to one vault and make config refs
  vault-relative so code can't reach outside it.
- Writes (e.g. storing a refreshed OAuth token) need read **and write** on the vault.
- In a read-only container: set `OP_CONFIG_DIR` to a tmpfs path (e.g. `/tmp/op`) and
  `OP_CACHE=false`; `op` then prints *"Using configuration at non-standard location"* to stderr,
  which is harmless.

## Inherited stdin gets eaten

Any `op` command that accepts a piped template will try to parse whatever stdin it inherits. A
script run as `python - <<EOF` (or anything with non-terminal stdin) that shells out to
`op item create` fails with *"unable to process line 1: invalid JSON in piped input"*. Pass
`stdin=subprocess.DEVNULL` to every `op` call that isn't deliberately piping a template.

## Beliefs that were wrong (don't rediscover them)

Each of these looked like the explanation for "edit succeeded but nothing changed"; each was
disproved by experiment. The real cause every time was socket stdin.

- ~~"`op item get --format json` hides concealed values without `--reveal`"~~ — it includes them.
- ~~"Piped edits silently drop *new* fields; create them first by assignment"~~ — new fields are
  added fine from a FIFO.
- ~~"Race: `op` checks for piped input before the parent has written"~~ — spawn-then-write works
  when stdin is a FIFO.
- ~~"Something about app-created items / long token values"~~ — structural clones and realistic
  values all wrote fine.

Method that found it: reproduce the *exact* call path in the failing process's conditions. Every
probe passed until one ran the same function under `uvloop.run(...)`.
