# Design decisions

Decisions locked in after the first brainstorming pass. Each is reversible — but reversing one will reshape the iteration plan, so do it deliberately.

| # | Decision | Rationale | Alternatives considered |
|---|---|---|---|
| 1 | **Audience: individuals / small groups** in v1. | Git remotes alone are sufficient; no registry server, no auth beyond git. Fastest path to a usable tool for a 4-person team. | Teams/orgs (would imply registry service + review workflow); open-source community (would imply hosted index, ratings). |
| 2 | **Cross-tool from day one: Claude Code + Codex.** | Half the team uses each; locking in to one would invalidate the design quickly. AGENTS.md is a real cross-tool standard that makes the second host cheap. | Claude Code first, adapters later; truly host-neutral (Cursor/IDEs from day one). |
| 3 | **Merge model: section schema + LLM 3-way merge** for same-section conflicts. | Section schema makes most prose merges conflict-free without LLM cost; LLM merge handles the residual same-section cases with a human review gate. Builds directly on git. | Section schema only (worse UX for prose conflicts); structured AST (best mergeability but breaks markdown ergonomics and existing skills). |
| 4 | **Visibility: two marketplaces + pre-push guard.** Frontmatter `visibility: public | proprietary`. | Cheap, deterministic, and matches how teams already separate public/private repos. Defers RBAC entirely. | Single marketplace with encrypted proprietary entries (adds key management); defer proprietary to v2 (forces awkward workarounds in v1). |
| 5 | **Implementation language: Python.** | Strong fit for LLM tooling, markdown/YAML processing, and the team's existing skillset. Pip distribution is acceptable for a 4-person internal tool. | TypeScript/Node (aligns with Claude Code itself); Go (single static binary). |
| 6 | **Pace: small iterations, each useful on its own.** | The vision will change as the team uses it. Each iteration is shippable; we hold a 30-min retro between iterations to scope the next. | Full vision in v1 (larger surface, slower feedback). |

## Out of scope for v1

- **RBAC, sub-teams, fine-grained access controls.** Public/proprietary is enough granularity for a 4-person team.
- **A registry server or hosted UI.** Git is the substrate.
- **Cursor / VS Code / IDE-specific adapters.** AGENTS.md export covers most of these passively in iteration 4; first-party adapters are stretch.
- **Automatic skill generation in v1.** `--from-transcript` and `refactor` are stretch goals after iteration 5.

## Things we are explicitly building on (not reinventing)

- **Claude Code plugin/marketplace format** (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) as the on-disk and on-git bundle.
- **Agent Skills specification** (`agentskills.io/specification`) as the cross-tool SKILL.md conformance target.
- **AGENTS.md** (`agents.md`) as the universal export format for non-Claude hosts.
- **Existing Python libs**: `python-frontmatter`, `marko`, `merge3`, `GitPython`, `anthropic` SDK, `typer`.

See [prior-art.md](./prior-art.md) for the landscape these choices are positioned against.
