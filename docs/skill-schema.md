# Skill schema (DRAFT — Iteration 0 deliverable)

> **Status:** proposed. Final form will be settled in Iteration 0 after team review. Documented here so the iteration plan is grounded in something concrete.

## Goals

1. **Be a strict conformant subset of [agentskills.io](https://agentskills.io/specification)** so skills install on any tool that reads the spec — not just Claude Code.
2. **Carry enough structure that section-aware merges work** (Iteration 3) without forcing skill authors to learn a new format.
3. **Carry enough metadata that `skillctl` can route, gate, and bundle** (visibility, dependencies).

## File layout

A skill is a directory:

```
<skill-name>/
├── SKILL.md              # frontmatter + body (this spec)
├── scripts/              # optional, per agentskills.io
├── references/           # optional, per agentskills.io
└── assets/               # optional, per agentskills.io
```

## Frontmatter

```yaml
---
# Required (per agentskills.io)
name: snake-case-name
description: One-sentence description of what the skill does.

# Required by us (skillctl extension)
visibility: public          # public | proprietary

# Recommended
when_to_use: |
  Free-form prose describing the trigger conditions.
version: 0.1.0              # semver; bumped on every push

# Optional (passed through to Claude Code)
allowed-tools: [Read, Edit, Bash]
disable-model-invocation: false
user-invocable: true

# Optional (skillctl extension)
depends_on:                 # other skills or plugins this one needs
  - mcp: github
  - skill: code-review-base
origin:                     # populated by `skillctl pull`, do not hand-edit
  marketplace: team-skills-private
  pulled_at: 2026-05-03T17:50:00Z
  base_sha: abc123
---
```

Unknown frontmatter keys are preserved on round-trip. Claude Code's existing optional keys (`context`, `paths`, `arguments`, `effort`, `model`) pass through unchanged.

## Body — section schema

The body is markdown with **named H2 sections**. The parser recognizes the following section names; anything else is preserved verbatim under a `## Other` bucket for merge purposes.

| Section | Required | Purpose |
|---|---|---|
| `## Purpose` | yes | One-paragraph statement of what the skill does and why it exists. |
| `## When to use` | yes | Triggers and signals — when an agent should reach for this skill. |
| `## Procedure` | no | Step-by-step instructions. The most edit-prone section. |
| `## Examples` | no | Worked examples. Encouraged to live in `references/` for long ones. |
| `## References` | no | Pointers to docs, RFCs, related skills. |
| `## Anti-patterns` | no | What not to do; common mistakes. |

### Why this set

- Matches how skill authors already structure prose, so it's not a tax.
- Each section is independently mergeable. Two people editing `## Procedure` and `## Examples` get a clean merge with no LLM call.
- `## Anti-patterns` is explicitly carved out because it's a frequent bolt-on and we don't want it shoved into `## Procedure`.

## Section IDs (optional, for robust merge)

Sections may carry a stable HTML-comment ID:

```markdown
## Procedure <!-- id: proc -->

1. ...
```

When IDs are present, `skillctl merge` tracks sections by ID across reorders. When absent, it falls back to matching by heading text.

## Visibility semantics

- `visibility: public` — may be pushed to any marketplace.
- `visibility: proprietary` — **may not** be pushed to a marketplace whose `marketplace.visibility` is `public`. The pre-push guard refuses, the GitHub Action on the public marketplace also refuses (defense in depth).

## What this is NOT

- Not a new spec — `name`/`description`/`scripts/` etc. follow agentskills.io.
- Not a serialization format — skills remain markdown that humans write directly.
- Not enforced at parse time for unknown sections — we preserve them so we can roll the schema forward without breaking existing skills.
