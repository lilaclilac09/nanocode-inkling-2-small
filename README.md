# nanocode + Inkling 2 Small

Status: LOCAL ONLY — this repository provides a local proxy and setup recipe, not a hosted agent service; next human action: validate the documented sample in your own supported nanocode/Tinker environment before relying on the integration.

Acceptance evidence: [2026-11-22 audit](notes/acceptance-audit-2026-11-22.md). The dated run below is historical evidence, not a fresh verification of the current upstream services.

Run [nanocode](https://github.com/nanocodexyz/nanocode) (`nc`), the Rust agent engine
that runs Codex and Claude harnesses, with
[Thinking Machines Inkling 2 Small](https://thinkingmachines.ai/news/inkling-2-small/)
as the model — via the [Tinker](https://tinker.thinkingmachines.dev) Anthropic-compatible API.

Verified working 2026-11-13: `nc exec` reads a file, edits it with Bash, and
reports back — all driven by Inkling 2 Small through Tinker.

## What it is

- **nanocode** (`nc`): a terminal agent engine. You give it a prompt; it reads
  files, runs commands, and edits code. Its strengths are Code Mode (the model
  writes a small program to call tools, so only the result comes back into
  context — cheap on tokens) and durability (every call is logged, so a dead
  process resumes).
- **Inkling 2 Small**: Thinking Machines' 594B MoE (17B active), text + image
  input, no audio. Served here through Tinker's Anthropic-compatible endpoint.
- **The glue**: nanocode's Claude harness talks the Anthropic Messages API.
  Point it at Tinker with two env vars and it just works — except nanocode
  only accepts its builtin model ids on the CLI, so a tiny local proxy
  (`tinker-proxy.py`) rewrites the model id to Inkling on the way through.

## Setup (Mac)

```sh
# 1. Install nanocode — use a release from 2026-11-13 or later.
#    The rolling "nanocode-cli" release (2026-10-27) does NOT read
#    NANOCODE_ANTHROPIC_BASE_URL. This per-commit build does:
curl -fsSL https://github.com/nanocodexyz/nanocode/releases/download/nanocode-cli-3f97ab0/nanocode-aarch64-apple-darwin.gz \
  -o /tmp/nanocode.gz
gunzip -c /tmp/nanocode.gz > ~/.nanocode/bin/nanocode
chmod +x ~/.nanocode/bin/nanocode
ln -sf nanocode ~/.nanocode/bin/nc
export PATH="$HOME/.nanocode/bin:$PATH"

# 2. Point nanocode at Tinker (Inkling via Anthropic API).
#    Base URL must include /v1 — nanocode only appends /messages.
export NANOCODE_ANTHROPIC_BASE_URL="https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api/v1"
export NANOCODE_ANTHROPIC_API_KEY="<your tml- key>"

# 3. Run it. Use a builtin Claude id on the CLI (nanocode validates the
#    name); the proxy below rewrites it to Inkling. --thinking none is
#    recommended — Inkling is not Claude and its thinking levels differ.
nc --harness claude --model claude-haiku-4-5 --thinking none
```

One-shot (no TUI), for scripts:

```sh
nc exec --harness claude --model claude-haiku-4-5 --thinking none \
  "Read hello.txt and append a line at the end."
```

## The proxy (only needed on a machine without a raw key)

On this VM the Tinker key lives in a credential store that only swaps the
real key into the `x-api-key` header. nanocode sends its key as a Bearer
token, which is never swapped — so a local proxy sits in between:

- `tinker-proxy.py` listens on `127.0.0.1:18789`, takes nanocode's request,
  drops its Bearer token, re-issues it to Tinker with the credential in
  `x-api-key`, and rewrites the `model` field to
  `thinkingmachines/Inkling-2-Small`. Responses (including SSE streams) pass
  through unchanged.

```sh
python3 tinker-proxy.py 18789
export NANOCODE_ANTHROPIC_BASE_URL="http://127.0.0.1:18789/v1"
export NANOCODE_ANTHROPIC_API_KEY="dummy"   # ignored by the proxy
nc exec --harness claude --model claude-haiku-4-5 --thinking none "…"
```

On your own Mac, where you hold the real `tml-` key, skip the proxy and set
`NANOCODE_ANTHROPIC_BASE_URL` to Tinker directly (step 2 above).

## What works / what does not

| | |
|---|---|
| Works | `nc exec` small tasks: read, edit, run commands, report back. Tool calls round-trip through Inkling. |
| Works | Interactive `nc` TUI session with the Claude harness. |
| Caveat | `--context-window` is a session arg in 0.7.0, not an `exec` flag — omit it; the default window applies. |
| Caveat | nanocode validates `--model` against its builtin list. Any builtin Claude id works as the CLI name; the proxy rewrites it to Inkling. Do not pass `thinkingmachines/Inkling-2-Small` directly — the CLI rejects it. |
| Caveat | The Codex harness cannot use Tinker: it needs the OpenAI Responses protocol, which Tinker's OpenAI route does not support for tools. Use the Claude harness only. |
| Not tested | Long multi-turn sessions, subagents, Code Mode with many tool calls, prompt caching headers. Inkling is not a coding model — do not expect it to out-code Muse. |

## Demo

`demo/hello.txt` is the sample workspace used for the first verified run:

```
$ nc exec --harness claude --model claude-haiku-4-5 --thinking none \
    "Read hello.txt and append the line 'Hello from Inkling via nanocode' at the end of the file."

Done. The file now contains:
Hello, world.
This is a demo file.
Hello from Inkling via nanocode
```

## Cost

Inkling 2 Small on Tinker (serverless, Anthropic route): $0.30 / 1M input
tokens, $0.03 / 1M cached input, $1.00 / 1M output. A small task like the demo
above costs a fraction of a cent.

## Files

- `tinker-proxy.py` — localhost proxy: Bearer → `x-api-key` swap + model rewrite.
- `demo/` — sample workspace for the first run.
