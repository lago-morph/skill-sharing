# Design decisions

> **Intent:** this is an **internal prototype**, not a commercial product. Audience is one 4-person pilot team, with possible rollout to ~30 people if it proves useful. The project is open source for transparency, but the goal is to **relieve a known team's immediate pain**. We expect to throw it away cheerfully if upstream tools (rulesync, first-party skills, etc.) absorb the use case mid-flight.

Decisions locked in after the first brainstorming pass, the deep-research review, and the rulesync / ai-rules-sync evaluations. Each is reversible — but reversing one will reshape the iteration plan, so do it deliberately.

| # | Decision | Rationale | Alternatives considered |
|---|---|---|---|
| 1 | **Audience: one 4-person pilot team, then maybe 30 people. Internal prototype, not a product.** | We're solving a known team's pain. No need to design for unknown users. Stop building if upstream absorbs the use case. | Open-source community (would force RBAC, hosted index, broader compat); ship as a product (would force funded discovery, marketing). |
| 2 | **Build on `rulesync` as substrate** for cross-tool fan-out and AGENTS.md export — wrapped behind a single `src/substrate.ts` for swap-out. | Real TypeScript programmatic API, ~25 supported hosts, dual ESM/CJS, types shipped. ai-rules-sync was evaluated and rejected (CLI-only, no Node API, idle since 2026-03). See [rulesync-evaluation.md](./rulesync-evaluation.md) and [ai-rules-sync-evaluation.md](./ai-rules-sync-evaluation.md). | Reinvent fan-out (busywork); ai-rules-sync (lacks API, dormant); skip cross-tool entirely (forces team to pick one assistant). |
| 3 | **Cross-tool from day one: Claude Code + Codex.** | Half the team uses each. Cheap because rulesync handles tool-specific paths. | Claude-Code-only first, host-neutral later. |
| 4 | **Merge model: LLM 3-way merge with human review. No section schema, no structured AST.** | Section schemas tax authors with structure they wouldn't otherwise write. The deep-research report found no clear evidence the structure pays off for prose. An LLM call on conflict is "dumb but cheap" and stays out of the author's way. | Section-aware schema (premature; deferred — see [consider-for-later.md](./consider-for-later.md)); structured AST (kills authoring ergonomics); ship without merge (leaves Pain 2 unsolved). |
| 5 | **Pilot uses private repositories only. No public/private split, no visibility frontmatter, no pre-push guard.** | Without a public surface there is nothing to leak. The visibility model and dual-marketplace design are deferred — see [consider-for-later.md](./consider-for-later.md). | Two marketplaces + visibility guard from day one (bloats iter-2; solves a non-problem for the pilot). |
| 6 | **Implementation language: TypeScript.** | Aligns with rulesync (Node), the Claude Code ecosystem, and the Anthropic TS SDK. One runtime per teammate's machine instead of two. | Python (the prior call; switched once we settled on rulesync as substrate). |
| 7 | **Pace: small iterations, each useful on its own. Throwaway-ready.** | Vision will change as the team uses it. If a better solution ships mid-flight, we should be able to abandon any iteration without sunk-cost panic. | Full vision in v1 (slower, harder to abandon). |

## Out of scope for the prototype

See [consider-for-later.md](./consider-for-later.md) for the parked features and the trigger conditions that would justify revisiting them. Highlights that don't get built unless the pilot demands it:

- Public/private marketplace split, `visibility:` frontmatter, pre-push guards.
- Section schema, stable IDs, structure-aware merge.
- Provenance / registry / catalog metadata.
- Overlay / base+override composition.
- RBAC, sub-teams, fine-grained access controls.
- Registry server or hosted UI.
- Skill generation tools (`--from-transcript`, `refactor`).
- VS Code / IDE surfaces.

## Things we are explicitly building on (not reinventing)

- **`rulesync`** — multi-tool fan-out and AGENTS.md export, wrapped behind one source file for isolation.
- **Claude Code plugin/marketplace format** (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) — on-disk and on-git bundle.
- **Agent Skills specification** (`agentskills.io/specification`) — SKILL.md format conformance, used unmodified.
- **AGENTS.md** — universal export target, handled by rulesync.
- **TypeScript libs:** `@anthropic-ai/sdk`, `gray-matter` (frontmatter), `simple-git`, `commander` (CLI).

See [prior-art.md](./prior-art.md) for the landscape these choices are positioned against.
