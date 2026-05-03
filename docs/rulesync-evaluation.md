# rulesync evaluation

> **Question:** can [`rulesync`](https://github.com/dyoshikawa/rulesync) be the substrate for `skillctl`, or do we need to keep it at arm's length?
>
> **Headline recommendation:** **Adopt as substrate, but only for what it already does well — fan-out, fetch, and AGENTS.md export.** Keep our skill bundle, visibility frontmatter, inventory, and merge driver outside `rulesync` so the day it pivots or removes our use case we can swap it without unwinding our schema.

Sources cited inline. Researched against rulesync `8.15.0` (published 2026-05-01).

## 1. What rulesync actually does

rulesync is a Node.js CLI that treats a `.rulesync/` directory as the single source of truth and **fans configuration out** to ~25 AI tools' native paths. It is fundamentally an *authoring* tool, not a *discovery* tool.

- **Input:** a `.rulesync/` directory with `rules/*.md`, `skills/<name>/SKILL.md`, `commands/`, `subagents/`, `mcp.json`, `hooks.json`, `.aiignore`, plus a top-level `rulesync.jsonc`. Frontmatter is YAML; body is markdown. ([file-formats.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/reference/file-formats.md), [configuration.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/guide/configuration.md))
- **Output:** tool-native files — `CLAUDE.md`, `.claude/skills/<name>/SKILL.md`, `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, `AGENTS.md`, `.codex/skills/`, etc. Project and global (`~/.claude/`, `~/.codex/`) scopes both supported.
- **Supported hosts:** Claude Code, Codex CLI, Cursor, GitHub Copilot (+ Copilot CLI), Gemini CLI, Cline, OpenCode, Roo Code, Kilo Code, Kiro, Windsurf, Zed, Warp, JetBrains Junie, AugmentCode, Google Antigravity, Factory Droid, Goose, Replit, Qwen Code, Rovodev, AgentsSkills, deepagents-cli, Pi, Takt, plus a generic `agentsmd` target. Claude Code and Codex CLI both have ✅ across `rules`, `skills`, `commands`, `subagents`, `mcp`, `hooks`, `permissions` in both scopes.
- **Features:** `rules`, `ignore`, `mcp`, `commands`, `subagents`, `skills`, `hooks`, `permissions`. Opt-in via `--features`.
- **CLI:** `rulesync init`, `generate`, `import`, `convert`, `fetch`, `install`, `gitignore`, `update`. ([cli-commands.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/reference/cli-commands.md))

`import` is per-tool one-shot ("read CLAUDE.md → write `.rulesync/rules/`"); `convert` is a stateless A→B conversion that doesn't touch `.rulesync/`; `fetch` pulls a foreign repo's `skills/`/`rules/`/etc. into `.rulesync/` with ref pinning.

## 2. Pain-by-pain mapping

| # | Pain | rulesync helps? | Notes |
|---|------|------|-------|
| 1 | No inventory — find every skill on the machine | **No.** | rulesync is one-direction: source → tool dirs. There's no `rulesync list`, no `rulesync where`. `import` is host-by-host and overwrites `.rulesync/`, so it's not a discovery primitive. |
| 2 | Prose doesn't merge with line-diff | **No.** | rulesync emits files; merge conflicts on either source or generated files are still git's problem. The FAQ even warns about generated-file diff noise and proposes `linguist-generated` as a workaround. ([faq.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/faq.md)) |
| 3 | All-or-nothing adoption — can't take part of a teammate's update | **No.** | No overlay/composition. The closest thing is **declarative sources** (§5), but that's whole-skill granularity with "first source wins" precedence. ([declarative-sources.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/guide/declarative-sources.md)) |
| 4 | Skills don't travel alone — they need MCP, tools, slash commands | **Partial.** | rulesync co-manages `mcp.json`, `commands/`, `subagents/`, `hooks.json`, and `permissions` alongside skills, all generated from one `.rulesync/` tree. So a teammate who adopts our `.rulesync/` gets the MCP servers and slash commands together — but only if everything is authored in `.rulesync/` shape. It does **not** declare per-skill dependencies; the bundle is implicit. |
| 5 | Public vs. proprietary mix | **No.** | No visibility concept. There's a `delete: true` + last-wins target precedence, but nothing that prevents publishing a `.rulesync/skills/secret/` on push. We have to layer this ourselves. |

Net: rulesync attacks pain 4 properly, brushes pain 3, and ignores 1, 2, and 5. That matches what we already assumed when we picked it as substrate.

## 3. Schema and frontmatter handling

This decides whether we can park `visibility:` in frontmatter without rulesync clobbering it.

Reserved skill frontmatter keys per [file-formats.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/reference/file-formats.md): `name`, `description`, `targets`, plus tool-namespaced blocks (`claudecode:`, `codexcli:`, `takt:`) that are opaque to other tools and dropped on emit to non-matching ones.

The docs do **not** promise pass-through for unknown top-level keys. rulesync uses `gray-matter` (preserves unknowns at parse time), but its emit step clearly rebuilds frontmatter from a known-key model — `claudecode.scheduled-task: true` rewrites the output path, which can't happen with generic pass-through. **Don't assume `visibility:` survives generation; test it in iter-0.**

Concrete iter-0 test: put `visibility: proprietary` in `.rulesync/skills/foo/SKILL.md`, run `rulesync generate --targets claudecode --features skills`, and `grep visibility .claude/skills/foo/SKILL.md`. If it's gone, visibility has to live outside the rulesync source tree (or be reapplied after generation).

rulesync does **not** modify the markdown body for skills (it does for some `rules` outputs, where multiple non-root rules concatenate into AGENTS.md-style files). Skills pass through as directory bundles.

## 4. Discovery / inventory

**Not a feature.** No equivalent of `skillctl list`. `rulesync import --targets X --features skills` is a one-direction host-by-host migration that overwrites `.rulesync/`, not a discovery primitive. `rulesync gitignore` knows every output path internally, but that table isn't on the public API. Our `skillctl list` is genuinely net-new; maintain our own `hosts.ts` registry as planned in [iteration-plan.md](./iteration-plan.md).

## 5. Multi-source / multi-repo composition

rulesync ships **declarative sources** ([declarative-sources.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/guide/declarative-sources.md)), which is closer to what we want than I expected:

```jsonc
// rulesync.jsonc
"sources": [
  { "source": "team-internal/skills" },                          // private
  { "source": "anthropics/skills", "skills": ["skill-creator"] }, // public, cherry-picked
  { "source": "https://dev.azure.com/org/p/_git/r", "transport": "git", "ref": "main" }
]
```

`rulesync install` resolves each ref to a SHA (writes `rulesync.lock`), fetches into `.rulesync/skills/.curated/<name>/`, and applies precedence: **local skills win over remote; first source wins over later sources.** A `--mode gh` writes directly to per-agent paths (`.claude/skills/`, `.cursor/skills/`, etc.) — overlapping with `skillctl pull`.

Close to our public/proprietary marketplace pair, **but**: no cross-source visibility check (a `team-internal/skills` skill can land somewhere you'd then commit to a public remote); skill granularity only (still pain 3); and the explicit marketplace ask in [#329](https://github.com/dyoshikawa/rulesync/issues/329) is labeled "considering" and unimplemented as of 8.15.0. Worth subscribing to.

## 6. Programmatic API

Yes — three exported async functions: `generate`, `importFromTool`, `convertFromTool` ([src/index.ts](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/src/index.ts), [programmatic-api.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/api/programmatic-api.md)). Dual ESM/CJS, types shipped, Node ≥ 22 (mirror in `skillctl`'s engines field). The `GenerateOptions` we'll use most: `inputRoot`, `outputRoots`, `targets`, `features`, `dryRun`, `check`, `silent`, `delete`.

```typescript
import { generate } from "rulesync";
await generate({
  inputRoot: tmpRulesyncDir, outputRoots: [process.cwd()],
  targets: ["claudecode", "codexcli"], features: ["skills"], silent: true,
});
```

Caveats: `baseDirs` is deprecated in favor of `outputRoots`; the per-target/per-feature config form changed in v8.0.0 (breaking). At least one major-version break in the past few months.

## 7. Maturity signals

- **Version / cadence:** 8.15.0, published 2026-05-01. Previous nine versions published between 2026-04-22 and 2026-05-01 — every 1–2 days currently, weekly historically. ([npm registry](https://registry.npmjs.org/rulesync))
- **Weekly downloads:** ~161k per a Socket-aggregated search snippet (treat as order-of-magnitude — npm's downloads API isn't on the allowlist here).
- **Stars / forks:** 1.1k / 108. **27 open issues**: CR-LF/path mismatches across OSes, a smol-toml CVE bump, Copilot frontmatter parsing bugs, the marketplace ask (#329). Triaged with `considering`/`enhancement` labels.
- **Maintainer:** single (`dyoshikawa`). **Biggest maturity risk** — bus factor of one for ~25-tool fan-out.
- **Direction:** more tools, more features (recent: permissions across Cursor/Kilo/AugmentCode/Cline/Qwencode; Gemini CLI command syntax; Copilot CLI). No public roadmap. `fetch` carries a "may change in future releases" warning.
- **Breaking-change history:** v8.0.0 broke `targets` array + `features` object; `baseDirs` deprecated. Schema still consolidating.

## 8. Integration sketch

`skillctl pull <skill>@<marketplace>` clones the marketplace, copies the skill into a temp `.rulesync/skills/<name>/`, then calls rulesync:

```typescript
// src/commands/pull.ts (sketch)
import { generate } from "rulesync";

const repo     = await cloneOrUpdate(marketplace);                     // ours
assertVisibilityCompatible(repo, skillDir);                            // ours
const tmp      = await mkdtemp("/tmp/skillctl-");
await cp(skillDir, path.join(tmp, ".rulesync/skills", skill), { recursive: true });
await generate({
  inputRoot: tmp, outputRoots: [process.cwd()],
  targets: ["claudecode", "codexcli"], features: ["skills"], silent: true,
});
```

Or, shelling out: `rulesync generate --targets claudecode,codexcli --features skills`.

We **don't** call rulesync on `push` — we write into the marketplace repo's plugin tree directly. rulesync only enters when materializing on a target machine. `skillctl list` and the merge driver use no rulesync code.

## 9. Risks of depending on rulesync

In rough order of likelihood:

1. **Frontmatter schema drift.** Closed set of keys + precedent of breaking config changes (v8.0.0). If `visibility:` collides with a future first-class key or rulesync starts rejecting unknown frontmatter, we relocate the key. **Mitigation:** test pass-through in iter-0; if it fails, keep canonical skills outside `.rulesync/skills/` and use rulesync only as a fan-out renderer.
2. **Single-maintainer bus factor.** One dev, very high cadence. A 6-month silence wouldn't be unusual. **Mitigation:** pin minor; assume we may need to fork.
3. **rulesync absorbs our use case.** Issue #329 + declarative sources are within shouting distance of `skillctl pull`. If they ship `--mode marketplace` with visibility checks, retire `skillctl` cheerfully — the *good* failure mode per [decisions.md](./decisions.md) row 7.
4. **rulesync pivots toward rules-only.** Historical core was rules; skills came later. If skills lag Claude Code's format changes, fan-out degrades silently. **Mitigation:** wrap `generate()` in one `src/substrate.ts` so we can swap to hand-rolled skill fan-out.
5. **Node 22 constraint.** rulesync requires Node 22+. Acceptable for an internal pilot; would matter at wider scope.
6. **Generated-file ambiguity.** rulesync's FAQ recommends `linguist-generated` for generated files. With our plan (canonical in marketplace repo, materialized via rulesync), `~/.claude/skills/foo/SKILL.md` is *generated* — must be explicit in our docs that users don't edit it in place.

## 10. Recommendation

**Adopt rulesync as the substrate for fan-out only. Don't put it in the critical path of authoring, inventory, or merging.**

- Credible match for pain 4 (skills + MCP + commands together) and partially for cross-tool. Re-implementing fan-out for ~25 tools is the busywork we promised not to do ([decisions.md](./decisions.md) row 2).
- TypeScript API is real and stable enough to call from `skillctl pull`. We get the multi-tool matrix for free.
- Its blind spots — inventory, merging, visibility — are exactly the gaps our prototype fills. No overlap makes our work redundant *today*.
- Bus-factor + breaking-change history argue for *isolation, not entanglement*: wrap rulesync in one file, treat its frontmatter schema as foreign, keep our canonical skill format independent of `.rulesync/`.
- #329 plus declarative sources are close enough that we should treat absorption as a likely-and-welcome outcome within ~6–12 months. The iteration plan is already throwaway-ready.

Iter-0 action items:

1. Pin `rulesync@^8.15` as a regular dependency. Don't promise forward compat past v9.
2. **Test that `visibility:` survives `rulesync generate --features skills` for both `claudecode` and `codexcli`.** This single test decides whether visibility lives inside or outside the rulesync source tree.
3. Subscribe to #329 and the rulesync release feed; revisit if either marketplaces or visibility ships upstream.

---

Primary sources (all linked inline above): [README](https://github.com/dyoshikawa/rulesync), [programmatic-api.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/api/programmatic-api.md), [configuration.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/guide/configuration.md), [file-formats.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/reference/file-formats.md), [cli-commands.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/reference/cli-commands.md), [declarative-sources.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/guide/declarative-sources.md), [separate-input-root.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/guide/separate-input-root.md), [faq.md](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/docs/faq.md), [src/index.ts](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/src/index.ts), [package.json](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/package.json), [npm registry](https://registry.npmjs.org/rulesync), [issue #329](https://github.com/dyoshikawa/rulesync/issues/329).
