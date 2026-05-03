# Problem statement

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

## Intended outcome

A Python CLI plus a small set of conventions that:

- Inventories skills across all known hosts on a machine.
- Pushes/pulls skills to/from a git-backed marketplace (public or private).
- Merges concurrent edits using a section-aware schema and an LLM-assisted three-way merge for same-section conflicts.
- Bundles each skill with its MCP/tool dependencies via the existing Claude Code plugin format, with adapters that emit AGENTS.md fragments for non-Claude hosts.
- Refuses to leak `proprietary` skills to public remotes.

V1 is intentionally small. We ship in increments a 4-person team can actually use and react to.
