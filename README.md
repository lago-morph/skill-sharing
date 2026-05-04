# skill-sharing

A design effort for `skillctl` — a TypeScript CLI that helps a small team inventory, share, and merge AI agent skills. The prototype targets **Codex CLI only**; broader tool support (Claude Code, Cursor, Copilot, …) is deferred and largely a config change once the Codex flow is proven, since rulesync handles fan-out.

> **This is an internal prototype**, not a commercial product. Built for a 4-person pilot team (potentially rolling out to ~30 people if useful), open-sourced for transparency. We will throw it away cheerfully if upstream tools (`rulesync`, first-party skills, etc.) absorb the use case mid-flight.

This repo is currently in the **design phase**. No code yet.

> **AI assistants:** start at [`AGENTS.md`](AGENTS.md). It tells you how to find "the next thing" and what's in/out of scope.

## Documents

### Planning (in scope)

- [`docs/problem-statement.md`](docs/problem-statement.md) — the five concrete pains we're solving (pain 5 deferred for the pilot).
- [`docs/decisions.md`](docs/decisions.md) — locked-in design decisions with rationale.
- [`docs/iteration-plan.md`](docs/iteration-plan.md) — four iterations sized for a 4-person team, each independently shippable; throwaway-ready.
- [`docs/skill-schema.md`](docs/skill-schema.md) — minimal SKILL.md format: agentskills.io unchanged, no extensions for the prototype.
- [`docs/prior-art.md`](docs/prior-art.md) — landscape: what exists, what we build on, where this earns its keep.

### Deferred (out of scope unless pilot demands)

- [`docs/consider-for-later.md`](docs/consider-for-later.md) — features and ambitions parked until the pilot justifies them. **Read the warning at the top before pulling anything from this list back into scope.**

### Substrate evaluations

- [`docs/rulesync-evaluation.md`](docs/rulesync-evaluation.md) — `rulesync` capabilities and fit. **Adopted as substrate.**
- [`docs/ai-rules-sync-evaluation.md`](docs/ai-rules-sync-evaluation.md) — `ai-rules-sync` capabilities and fit. **Evaluated and rejected.**

### Research

- [`docs/research-brief.md`](docs/research-brief.md) — self-contained brief that was fed to a deep-research agent.
- [`docs/deep-research-report.md`](docs/deep-research-report.md) — the resulting external review; informed the prototype refocus.
