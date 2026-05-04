# Problem statement

> **Scope note:** this is an **internal prototype** for a specific 4-person team (potentially rolling out to ~30 people if useful). The goal is to relieve real pain we're hitting today, not to ship a commercial product. We will throw the project away cheerfully if upstream tools absorb the use case.

A small team (≈4 people) wants to share AI **skills** — natural-language instructions that guide coding agents — across the tools each person uses (Claude Code and Codex, in CLI / desktop / web / IDE forms). Today this is painful for five reasons.

## 1. No inventory

Skills live in many places: per-user (`~/.claude/skills/`), per-project (`.claude/skills/`), bundled inside installed plugins, and in tool-specific locations for Codex / Cursor / etc. There is no single command that says "here is everything I have, and where it came from." Without that, you can't reliably share or merge.

## 2. Prose doesn't merge with line-diff

Skills are markdown. Two people editing the same skill — even non-conflicting edits — routinely produce git conflicts that are unresolvable line-by-line because one of them reorganized sections.

## 3. All-or-nothing adoption

A teammate's update to a shared skill may help one user and hurt another. Today the only options are "accept the whole new version" or "fork." There is no clean way to take part of a change.

## 4. Skills don't travel alone

Many skills depend on MCP servers, tools, or slash commands. Sharing the SKILL.md without those dependencies produces a broken skill on the recipient's machine.

## 5. Public vs. proprietary mix

Some skills are fine to share publicly; others encode internal practice and must not leak. Today nothing prevents an accidental push to a public remote.

> **Deferred for the pilot.** The pilot uses only private repositories, so this pain is sidestepped rather than solved. The visibility model and pre-push guard are parked in [`consider-for-later.md`](./consider-for-later.md), to be revived if the team starts publishing to a public surface.

## Intended outcome

A TypeScript CLI plus a small set of conventions, building on `rulesync` for cross-tool fan-out, that:

- Inventories Codex skills on a machine (`skillctl list`).
- Lists what's available in a private git-backed marketplace (`skillctl ls <marketplace>`).
- Pulls/pushes skills to/from that marketplace.
- Merges concurrent edits by handing `(base, ours, theirs)` to an LLM and asking the user to review the result. No section schema, no structured AST.
- Bundles each skill with its MCP/tool dependencies via the existing Claude Code plugin format (used as a metadata convention; Codex doesn't read it); AGENTS.md and other-tool fan-out are delegated to rulesync.

V1 is intentionally small. **The prototype targets Codex CLI only**; Claude Code and other tools are deferred — see [`consider-for-later.md`](./consider-for-later.md). We ship in increments a 4-person team can actually use and react to. Anything that doesn't address pains 1–4 above is out of scope; pain 5 is also deferred.
