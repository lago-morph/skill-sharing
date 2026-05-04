# AGENTS.md

> **AI assistants joining this project: read this file first.** It tells you how to orient, where the work lives, what is in and out of scope, and how to identify "the next thing to do."
>
> Reading order: this file → [`README.md`](./README.md) → [`docs/iteration-plan.md`](./docs/iteration-plan.md) → [`docs/decisions.md`](./docs/decisions.md). Everything else is reference material — read on demand when a task needs it.

## What this project is

`skillctl` is a TypeScript CLI prototype for sharing AI agent skills inside a small team. It is **not a product**. It is an internal pilot for a 4-person team (potentially ~30 later), open-sourced for transparency only. The intent is to relieve specific pain points fast and to **abandon the project cheerfully** if upstream tools (rulesync, first-party skills, etc.) absorb the use case.

The repo is currently in the **design phase**: docs only, no code.

## Finding "the next thing"

1. Open [`docs/iteration-plan.md`](./docs/iteration-plan.md). Iterations are numbered and sequential.
2. The "next thing" is the **first iteration whose deliverable is not yet present in the repo**. Check by inspecting the repo, not by guessing.
3. Each iteration ends with a **"Try it out"** block. The iteration is done when those commands work end-to-end on a fresh checkout.

If the user says *"implement the next thing on the list"* without further qualification, identify the iteration via step 2, state your interpretation in one sentence, and proceed.

## Hard rules — do not violate without explicit user permission

1. **Codex CLI is the only target.** Do not add Claude Code, Cursor, Copilot, Gemini, or any other tool to `hosts.ts` or to `--targets` for rulesync. Other-tool support is parked — see [`docs/consider-for-later.md`](./docs/consider-for-later.md).
2. **Do not pull anything from [`docs/consider-for-later.md`](./docs/consider-for-later.md) into scope.** That file explicitly tells you the trigger conditions for revisiting each item; if a request seems to ask for one of them, surface that and ask before acting.
3. **No section schema, no stable section IDs, no structure-aware merge.** Skills are vanilla agentskills.io SKILL.md. The merge driver is a dumb LLM call on `(base, ours, theirs)`. See [`docs/decisions.md`](./docs/decisions.md) row 4.
4. **No `visibility:` frontmatter, no public/private split, no pre-push guard.** The pilot uses private repos only. See [`docs/decisions.md`](./docs/decisions.md) row 5.
5. **rulesync is the substrate, wrapped behind exactly one file (`src/substrate.ts`).** Do not import or call `rulesync` from anywhere else. ai-rules-sync is rejected — do not add it as a dependency.
6. **TypeScript only.** No Python, no shell wrappers as primary code. CLI built with `commander`; LLM calls via `@anthropic-ai/sdk` with prompt caching on.
7. **Do not create new docs without asking first.** The `docs/` set is intentional.
8. **Do not modify [`docs/research-brief.md`](./docs/research-brief.md) or [`docs/deep-research-report.md`](./docs/deep-research-report.md).** They are historical artifacts.

When you find yourself wanting to do something that conflicts with these rules, that is a signal to **stop and ask**, not to push through.

## Workflow

- **Branches.** Use a descriptive feature branch per iteration: `iter-0-scaffolding`, `iter-1-list`, `iter-2-marketplace`, `iter-3-merge`. If a session arrived on a different branch (e.g. via a system prompt), ask before switching.
- **Commits.** Clear subject + body explaining *why*. One logical change per commit; multiple commits per iteration are fine. Never amend a published commit.
- **Confirm before risky actions.** Force-push, branch delete, dropping files, touching `main`, modifying CI — ask first.
- **Run the iteration's "Try it out" block before claiming done.** That is the verification gate.
- **When unsure, ask in one sentence.** "Iter 1 — pick up `~/.codex/skills/` only, or also `./.codex/skills/`?" beats guessing.

## Definition of done for an iteration

1. The bullet-point spec in [`docs/iteration-plan.md`](./docs/iteration-plan.md) is satisfied.
2. The "Try it out" block runs cleanly on a fresh checkout.
3. Tests cover the new behavior (test infra is set up in iter 0; subsequent iterations extend it).
4. `tsc --noEmit` passes.
5. Commits are pushed.
6. The user agrees it is done. Don't self-mark — confirm.
