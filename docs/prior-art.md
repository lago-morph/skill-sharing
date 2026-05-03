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

| Tool | Scope | Maturity | Gap vs. our design |
|---|---|---|---|
| [`rulesync`](https://github.com/dyoshikawa/rulesync) (Node) | Fan-out one source to many tools | Mature-ish | No overlays, no prose merge, no proprietary/public split |
| [`ai-rules-sync`](https://github.com/lbb00/ai-rules-sync) (Node) | Similar to rulesync, privacy-first | Mature-ish | Same gaps |
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

1. **Overlay model on top of AGENTS.md + SKILL.md.** chezmoi-style base + per-host/per-tool/per-team layers. None of the rulesync-class tools do this.
2. **Section-aware + LLM 3-way merge for prose.** Mergiraf and Weave target code; nobody targets skill prose specifically.
3. **Standalone transcript → SKILL.md.** Fills a real gap (stretch goal).
4. **Cross-marketplace install with a lockfile.** Pin sources across Claude Code plugins, Cursor plugins, Continue Hub, raw GitHub Skills repos. Cargo/npm-style resolution is open territory (stretch).

## Python libraries we'll use

| Library | Purpose |
|---|---|
| [`python-frontmatter`](https://pypi.org/project/python-frontmatter/) | Frontmatter parse/serialize |
| [`marko`](https://github.com/frostming/marko) | CommonMark-correct AST; section splitting |
| [`merge3`](https://github.com/breezy-team/merge3) | Three-way merge primitive (line-level fallback) |
| [`GitPython`](https://github.com/gitpython-developers/GitPython) | Git ops via subprocess wrapper |
| [`anthropic`](https://github.com/anthropics/anthropic-sdk-python) | LLM merge driver and generators (prompt caching on) |
| [`typer`](https://typer.tiangolo.com/) | CLI |
| [`claude-agent-sdk-python`](https://github.com/anthropics/claude-agent-sdk-python) | Optional, if iter-3 LLM merge or stretch transcript→skill needs richer agent loops |
