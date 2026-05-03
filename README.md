# skill-sharing

A design effort for `skillctl` — a TypeScript CLI that helps a small team inventory, share, and merge AI agent skills across multiple coding-assistant platforms (Claude Code, Codex, Cursor, Aider, …).

> **This is an internal prototype**, not a commercial product. Built for a 4-person pilot team (potentially rolling out to ~30 people if useful), open-sourced for transparency. We will throw it away cheerfully if upstream tools (`rulesync`, first-party skills, etc.) absorb the use case mid-flight.

This repo is currently in the **design phase**. No code yet.

## Documents

### Planning

- [`docs/problem-statement.md`](docs/problem-statement.md) — the five concrete pains we're solving.
- [`docs/decisions.md`](docs/decisions.md) — locked-in design decisions with rationale.
- [`docs/iteration-plan.md`](docs/iteration-plan.md) — four iterations sized for a 4-person team, each independently shippable; throwaway-ready.
- [`docs/skill-schema.md`](docs/skill-schema.md) — minimal SKILL.md format: agentskills.io unchanged plus one `visibility:` frontmatter key.
- [`docs/prior-art.md`](docs/prior-art.md) — landscape: what exists, what we build on, where this earns its keep.

### Substrate evaluations

- [`docs/rulesync-evaluation.md`](docs/rulesync-evaluation.md) — `rulesync` capabilities and fit as a peer-dependency substrate.
- [`docs/ai-rules-sync-evaluation.md`](docs/ai-rules-sync-evaluation.md) — `ai-rules-sync` capabilities and fit as a peer-dependency substrate.

### Research

- [`docs/research-brief.md`](docs/research-brief.md) — self-contained brief that was fed to a deep-research agent.
- [`docs/deep-research-report.md`](docs/deep-research-report.md) — the resulting external review; informed the prototype refocus.
