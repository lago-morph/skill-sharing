# Prior art and landscape

Snapshot from research conducted May 2026 across two passes (Claude Code documentation + general web sweep). This will go stale — re-run before any major scope decision.

## Claude Code primitives we'll build on

- **Skill paths.** `~/.claude/skills/<name>/SKILL.md` (user), `.claude/skills/<name>/SKILL.md` (project), `<plugin>/skills/<name>/SKILL.md` (bundled). Auto-discovered, watched. Spec: `code.claude.com/docs/en/skills.md`.
- **SKILL.md format.** YAML frontmatter (`name`, `description`, `when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `context`, `paths`, `arguments`, `effort`, `model`) + markdown body.
- **Plugin manifest** (`.claude-plugin/plugin.json`). Bundles skills, agents, hooks, MCP servers, LSP servers, monitors, themes, output styles, channels. Spec: `code.claude.com/docs/en/plugins-reference.md`.
- **Marketplace** (`.claude-plugin/marketplace.json`). A git repo listing plugins. Installed via `/plugin marketplace add` + `/plugin install`. Private git repos work as marketplaces. Spec: `code.claude.com/docs/en/plugin-marketplaces.md`.
- **MCP in plugins.** `.mcp.json` at plugin root or inline under `mcpServers` in plugin.json. Variable substitution: `${CLAUDE_PLUGIN_ROOT}` etc.

## Cross-tool standards

- **AGENTS.md** (`agents.md`, repo `agentsmd/agents.md`). Donated to the Agentic AI Foundation Dec 2025. Plain markdown, schema-free, nearest-file-wins. Native support across Codex, GitHub Copilot, Cursor, Windsurf, Amp, Devin, Jules, Gemini, Factory, Zed, RooCode, Continue.dev, Aider, OpenHands. **Treat as universal export target — Codex is just the closest consumer.**
- **Agent Skills specification** (`agentskills.io/specification`). Released by Anthropic Dec 2025. SKILL.md + frontmatter + `scripts/` / `references/` / `assets/`. Adopted by OpenAI/Codex and most major tools. **Our SKILL.md should conform to this**, not the Claude Code-specific superset.

## Direct competitors (closest existing tools)

> **Note:** after evaluation we adopted `rulesync` as substrate and rejected `ai-rules-sync`. See [decisions.md](./decisions.md) Decision 2, [rulesync-evaluation.md](./rulesync-evaluation.md), and [ai-rules-sync-evaluation.md](./ai-rules-sync-evaluation.md). We delegate cross-tool fan-out and AGENTS.md export to rulesync and only build the inventory + remote-listing + merge layer on top.

| Tool | Scope | Maturity | Role for us |
|---|---|---|---|
| [`rulesync`](https://github.com/dyoshikawa/rulesync) (Node) | Fan-out one source to many tools (rules, commands, MCP, ignore-files, subagents, skills) | Mature-ish | **Substrate (adopted).** Wrapped behind `src/substrate.ts`. |
| [`ai-rules-sync`](https://github.com/lbb00/ai-rules-sync) (Node) | Symlink-based multi-repo composition | Pre-1.0, idle since 2026-03 | **Evaluated and rejected.** No Node API, single maintainer, dormant. |
| [`skillshare`](https://github.com/runkids/skillshare) | Skill sharing | Newer / experimental | Unclear |
| `ai-nexus` | Agent ecosystem | Experimental | Unclear |
| [`anthropics/skills`](https://github.com/anthropics/skills), [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) | Official Anthropic catalogs | Stable | Passive content; not a sync tool |
| LangSmith Hub, PromptHub, Promptfoo | Prompt management | Mature (different domain) | Prompt-centric, not AGENTS.md / Skills aware |

Curation-only resources: `wshobson/agents` (148+ skills, 960k+ installs), `awesome-skills.com`, `claudemarketplaces.com`, `skillsmp.com`, `travisvn/awesome-claude-skills`, `ComposioHQ/awesome-claude-skills`.

## Semantic / LLM merge landscape

- **[Mergiraf](https://mergiraf.org/)** — mature tree-sitter merge, 33+ languages, code-focused.
- **[Weave](https://github.com/ataraxy-labs/weave)** — newer, claims markdown support.
- **[difftastic](https://github.com/Wilfred/difftastic)** — structural diff (markdown via tree-sitter, recent).
- **No mature standalone LLM merge driver exists** for prose. People stitch shell wrappers around Claude as a custom git driver. Real gap.

## Dotfile / overlay analogues

- **[chezmoi](https://www.chezmoi.io/)** — templating, encryption, per-host overlays.
- **[yadm](https://yadm.io/)**, **[dotbot](https://github.com/anishathalye/dotbot)**, **[Dotter](https://github.com/SuperCuber/dotter)**.
- **None are AI-config-aware.** Users today stash `CLAUDE.md` as a plain dotfile.

## Skill-from-transcript

- Anthropic's **skill-creator** lives inside Claude Code (not a standalone CLI).
- Anthropic Console **Prompt Generator** is web-only.
- **No standalone transcript→SKILL.md CLI exists.** Real gap.

## Where this tool earns its keep

Scoped down for the prototype. Overlays, transcript→skill, lockfiles, visibility guards, and provenance metadata are all parked in [consider-for-later.md](./consider-for-later.md).

1. **Inventory across hosts.** rulesync is an authoring tool; it doesn't survey what's on a machine. `skillctl list` is the smallest piece of net-new value.
2. **Remote inventory** (`skillctl ls <marketplace>`). Counterpart to `skillctl list`. Tells the team what's available without inspecting `marketplace.json` by hand.
3. **LLM 3-way merge driver wired to git via `.gitattributes`.** Existing approaches are DIY shell wrappers; making this a turnkey thing for SKILL.md files is a real gap-fill — and we do it without a section schema, just `(base, ours, theirs)` → LLM → reviewed candidate.
4. **(Deferred)** Overlay model, transcript → SKILL.md, visibility guard, lockfile, etc. — see [consider-for-later.md](./consider-for-later.md).

## TypeScript libraries we'll use

| Library | Purpose |
|---|---|
| [`@anthropic-ai/sdk`](https://github.com/anthropics/anthropic-sdk-typescript) | LLM merge driver (prompt caching on) |
| [`gray-matter`](https://github.com/jonschlinkert/gray-matter) | Frontmatter parse/serialize |
| [`simple-git`](https://github.com/steveukx/git-js) | Git ops |
| [`commander`](https://github.com/tj/commander.js) | CLI |
| [`rulesync`](https://github.com/dyoshikawa/rulesync) | Multi-tool fan-out, AGENTS.md export (wrapped behind `src/substrate.ts`) |
