# Skill schema

> **Status:** intentionally minimal. We do **not** define a custom schema. Skills follow [agentskills.io](https://agentskills.io/specification) unchanged, plus one frontmatter extension. This file used to specify a section schema with optional stable IDs; that approach was dropped per the deep-research review (see [deep-research-report.md](./deep-research-report.md)) — there's no clear evidence the structure pays off for prose, and forcing it taxes authors.

## File layout

A skill is a directory exactly as agentskills.io defines it:

```
<skill-name>/
├── SKILL.md
├── scripts/         # optional, per agentskills.io
├── references/      # optional, per agentskills.io
└── assets/          # optional, per agentskills.io
```

## Frontmatter extension

We add **one** key on top of agentskills.io frontmatter:

```yaml
---
name: snake-case-name
description: One-sentence description of what the skill does.
visibility: public          # public | proprietary  ← skillctl extension
# ...all other agentskills.io / Claude Code keys pass through unchanged
---
```

Unknown frontmatter keys are preserved on round-trip.

## Body

Whatever the author wants to write. We do **not** require named sections, stable IDs, or a particular structure. If a merge conflict arises, the LLM merge driver (Iteration 3) handles it — that's the whole point of choosing LLM merge over a structured approach.

## Visibility semantics

- `visibility: public` — may be pushed to any marketplace.
- `visibility: proprietary` — **may not** be pushed to a marketplace whose `marketplace.visibility` is `public`. The pre-push guard refuses; an optional GitHub Action on the public marketplace can refuse server-side as defense in depth.

## What this is NOT

- **Not a section schema.** Authors write whatever markdown structure suits the skill.
- **Not a serialization format.** Skills remain markdown that humans write directly.
- **Not enforced.** If the agentskills.io frontmatter is malformed, that's an upstream concern; we don't validate beyond the visibility key.
