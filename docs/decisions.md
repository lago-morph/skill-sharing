# Design decisions

> **Intent:** this is an **internal prototype**, not a commercial product. Audience is one 4-person pilot team, with possible rollout to ~30 people if it proves useful. The project is open source for transparency, but the goal is to **relieve a known team's immediate pain**. We expect to throw it away cheerfully if upstream tools (rulesync, first-party skills, etc.) absorb the use case mid-flight.

Decisions locked in after the first brainstorming pass and the deep-research review. Each is reversible — but reversing one will reshape the iteration plan, so do it deliberately.

| # | Decision | Rationale | Alternatives considered |
|---|---|---|---|
| 1 | **Audience: one 4-person pilot team, then maybe 30 people. Internal prototype, not a product.** | We're solving a known team's pain. No need to design for unknown users. Stop building if upstream absorbs the use case. | Open-source community (would force RBAC, hosted index, broader compat); ship as a product (would force funded discovery, marketing). |
| 2 | **Build on `rulesync` / `ai-rules-sync` as substrate** for cross-tool fan-out and AGENTS.md export. | They already solve the multi-tool sync problem across Claude Code, Codex, Copilot, Cursor, Gemini, etc. Reinventing this is busywork that could be subsumed by upstream at any time. | Roll our own multi-tool exporter (more code, no leverage); skip cross-tool entirely (forces team to standardize on one assistant). |
| 3 | **Cross-tool from day one: Claude Code + Codex.** | Half the team uses each. Cheap because we delegate the tool-specific paths to rulesync. | Claude-Code-only first, host-neutral later. |
| 4 | **Merge model: LLM 3-way merge with human review. No section schema, no structured AST.** | Section schemas tax authors with structure they wouldn't otherwise write. The deep-research report found no clear evidence the structure pays off for prose. An LLM call on conflict is "dumb but cheap" and stays out of the author's way. | Section-aware schema (premature; defer until pilot proves the need); structured AST (kills authoring ergonomics); ship without merge (leaves Pain 2 unsolved). |
| 5 | **Visibility: two marketplaces + pre-push guard.** Frontmatter `visibility: public \| proprietary`. | Cheap, deterministic, matches how the team already separates public/private repos. ~50 LOC. | Single marketplace with encryption (key management overhead); defer entirely (forces awkward workarounds). |
| 6 | **Implementation language: TypeScript.** | Aligns with rulesync (Node), the Claude Code ecosystem, and the Anthropic TS SDK. One runtime per teammate's machine instead of two. | Python (the prior call; switched once we settled on rulesync as substrate). |
| 7 | **Pace: small iterations, each useful on its own. Throwaway-ready.** | Vision will change as the team uses it. If a better solution ships mid-flight, we should be able to abandon any iteration without sunk-cost panic. | Full vision in v1 (slower, harder to abandon). |

## Out of scope for v1 (and probably forever, unless pilot demands it)

- **Section schema, stable section IDs, structure-aware merge.** Deferred per the deep-research recommendation; LLM merge handles conflicts when they arise.
- **Provenance / registry / catalog metadata** (ownership, freshness, compatibility scoring). Useful at scale; overkill for a pilot.
- **Overlay / base+override composition.** Deferred until the pilot reports that "all-or-nothing adoption" is actually the most painful unresolved problem.
- **RBAC, sub-teams, fine-grained access controls.** Public/proprietary is enough granularity.
- **Registry server or hosted UI.** Git is the substrate.
- **First-party Cursor / VS Code / IDE adapters.** AGENTS.md export via rulesync covers these passively.
- **Automatic skill generation** (`--from-transcript`, `refactor`). Stretch only if the pilot identifies real demand.

## Things we are explicitly building on (not reinventing)

- **`rulesync` / `ai-rules-sync`** — multi-tool fan-out and AGENTS.md export.
- **Claude Code plugin/marketplace format** (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) — on-disk and on-git bundle.
- **Agent Skills specification** (`agentskills.io/specification`) — SKILL.md format conformance, used unmodified.
- **AGENTS.md** — universal export target, handled by rulesync.
- **TypeScript libs:** `@anthropic-ai/sdk`, `gray-matter` (frontmatter), `simple-git`, `commander` (CLI).

See [prior-art.md](./prior-art.md) for the landscape these choices are positioned against.
