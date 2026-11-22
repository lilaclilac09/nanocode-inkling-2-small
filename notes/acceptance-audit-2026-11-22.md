# Acceptance audit — 2026-11-22

Existing work checked against [ACCEPTANCE.md](../ACCEPTANCE.md); only rules there determine failures.

| # | Item | Fails rule | Source rule | Fix |
|---|------|-----------|-------------|-----|
| 1 | README / delivery status | Works/caveats table and historical demo do not supply product status + next human action | §5, `ship-visible-mvp.mdc` | Fixed in this PR: `Status: LOCAL ONLY`, operator-validation next action, historical-run qualification rather than a new hosted-service claim. |

Not fixable after merge: none established in the returned PR history. README's `src-ref/` entry referred to a directory absent from tracked files; removed as a factual correction, not an independently invented acceptance failure.

## Existing work and evidence

- Latest origin/main fetched before branching; base SHA `5ad862735a63063c6cb222fcd140c911002d05a0`.
- All returned PRs: [#1, Add Aileen's acceptance standard and PR evidence check](https://github.com/lilaclilac09/nanocode-inkling-2-small/pull/1), MERGED. Current checker accepts its body; merge SHA present and ancestor check against origin/main exits 0.
- README documents nanocode Claude harness, Tinker model rewrite via `tinker-proxy.py`, Mac direct-key setup, `nc exec`, external TUI and demo transcript. `demo/hello.txt` exists; no tracked `src-ref/`. AGENTS/CLAUDE/Cursor rule point to ACCEPTANCE.md.
- No repo web UI, automated product tests, build or lint configuration. TUI is supplied by external nanocode, not this repository. Only acceptance workflow; four recent successful acceptance runs do not reproduce remote inference.
- Deployments API: `[]`; Pages: `gh: Not Found (HTTP 404)`. A local CLI recipe does not imply hosted production, and no external production service is established here.

## Acceptance coverage and verification scope

- §1: workflow order, prior inspection/root cause/minimal diff, no unrequested redesign/deletion, confirmation on visual/multi-system changes, dependency justification: historical conversations unavailable; not assessable. This PR changes documentation only.
- §2: no inspection/diff-only completion; disclose skipped checks; test changed flow; no old-QA substitution; artifacts: README's dated demo remains historical evidence with untested limitations, not a current claim. No paid remote inference, operator credentials, native-Mac or external TUI validation performed by this PR.
- §3: no bug-fix PR returned; historical repro/hypothesis/root-cause/minimal-fix/safety chronology not established or alleged missing.
- §4: no repo web UI or UI change. Future TUI acceptance needs relevant screenshots and interaction evidence; no fake mobile webpage created.
- §5: item 1 fixed; #1 MERGED and reachable. No draft endpoint established; historical duplication/approval chronology unavailable.
- §6: instruction pointers and README commands reviewed. No imported OKC job-ID rule or invented numeric-citation criterion.
- §7: native Mac/nanocode/Tinker access are operator prerequisites. Impact: degraded current verification; next human action: validate sample in supported personal environment; not doing: requesting new secrets or running paid inference to turn a docs PR into a production claim.
- §8: #1 passes; proposed PR body must pass `python scripts/check_acceptance.py <body-file>`.

No product test command exists. Python syntax can be checked without executing the proxy. Documented manual flow starts `python3 tinker-proxy.py 18789` in the intended credential environment, configures nanocode and runs the README sample; not replayed here. Actual documentation/syntax/closer outcomes are recorded in the PR evidence. No raw API JSON committed.
