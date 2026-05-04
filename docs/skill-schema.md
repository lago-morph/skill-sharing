# Skill schema

> **Status:** intentionally minimal. We do **not** define a custom schema. Skills follow [agentskills.io](https://agentskills.io/specification) unchanged. The earlier draft of this file specified a section schema with optional stable IDs and a `visibility:` frontmatter extension — both are deferred. See [`consider-for-later.md`](./consider-for-later.md) and [`deep-research-report.md`](./deep-research-report.md).

## File layout

A skill is a directory exactly as agentskills.io defines it:

```
<skill-name>/
├── SKILL.md
├── scripts/         # optional, per agentskills.io
├── references/      # optional, per agentskills.io
└── assets/          # optional, per agentskills.io
```

## Frontmatter

Whatever agentskills.io defines, plus whatever Claude Code accepts. We add **no required keys** of our own for the prototype. Unknown frontmatter keys should be preserved on round-trip — verify this once when wiring up rulesync (it uses `gray-matter` at parse but rebuilds frontmatter from a known-key model on emit, so behavior for unknowns is worth confirming). See [rulesync-evaluation.md](./rulesync-evaluation.md) §3.

## Body

Whatever the author wants to write. We do **not** require named sections, stable IDs, or a particular structure. If a merge conflict arises, the LLM merge driver (Iteration 3) handles it.

## What this is NOT

- **Not a section schema.**
- **Not a serialization format.** Skills remain markdown that humans write directly.
- **Not enforced.** No validation beyond what agentskills.io / Claude Code already do.
