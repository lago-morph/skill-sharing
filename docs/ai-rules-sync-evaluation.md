# ai-rules-sync evaluation

> **Verdict up front.** Use it selectively, do not depend on it as substrate. Its multi-repository composition is a real fit for the "private + public marketplace" model, but it is symlink-based, CLI-only (no documented Node API), young (started 2025-12-25, 27 stars, single maintainer), and idle for ~7 weeks as of evaluation. Treat it as a peer tool we recommend to teammates, not a library we wire into `skillctl`.

Evaluated against v0.8.1 (npm published 2026-03-11, last commit 2026-03-16, evaluated 2026-05-03). Sources: the GitHub repo at [github.com/lbb00/ai-rules-sync](https://github.com/lbb00/ai-rules-sync), npm registry metadata at [registry.npmjs.org/ai-rules-sync](https://registry.npmjs.org/ai-rules-sync), and the project docs at [lbb00.github.io/ai-rules-sync](https://lbb00.github.io/ai-rules-sync/) (mirrored in the repo under `docs/`).

## 1. What it actually does

AIS (the `ais` binary) manages **per-tool rule/skill/agent files in your project as symbolic links into Git-cloned "rules repositories"**. The flow is:

1. `ais use <repo-url>` — clones the repo into `~/.config/ai-rules-sync/repos/<name>` and registers it.
2. `ais cursor add react` (or `ais claude skills add code-review`, etc.) — creates a symlink from the project's expected location (e.g. `.claude/skills/code-review`) into the cloned rules repo, and records the dependency in `ai-rules-sync.json`.
3. `ais install` — re-creates all symlinks listed in `ai-rules-sync.json` on a new machine. Cloning teammates do this on onboarding.

It is **not** a build/transform/render tool. It does not parse markdown, does not touch frontmatter, does not modify file contents. The dependency is `linkany` (`^0.0.4`) which does the actual symlink creation. See `src/sync-engine.ts` lines 106-118 in the cloned repo, and the `dotany` abstraction layer at `src/dotany/`.

**Inputs accepted:** any file the target tool supports — `.md`, `.mdc`, `.toml`, `.ts`, `.js`, `.rules`, `.instructions.md`, `.prompt.md`, `.agent.md`. They are passed through unchanged.

**Outputs produced:** symlinks, plus the `ai-rules-sync.json` / `ai-rules-sync.local.json` / `~/.config/ai-rules-sync/user.json` config files. Plus auto-managed `.gitignore` entries (so tracked symlinks don't pollute the project's git history) and `.git/info/exclude` entries for `--local` private rules.

**Tools/hosts supported (v0.8.1):** Cursor, GitHub Copilot, Claude Code, Trae, OpenCode, Codex, Gemini CLI, Warp, Windsurf, Cline, plus a universal `agents-md` adapter. Each tool exposes one or more subtypes (`rules`, `commands`, `skills`, `agents`, `prompts`, `instructions`, `md`, `tools`). Full table in `docs/reference/supported-tools.md`. Notably Claude Code skills land at `.claude/skills/` (project) or `~/.claude/skills/` (user via `--user`) — exactly our target layout.

**Invocation:** `ais <tool> [subtype] <action> <name> [-t repo] [-l] [-d targetDir] [--user] [--dry-run] [--force]`. There is also a top-level `ais add` that auto-detects tool when unambiguous. Full CLI in `docs/reference/cli.md`.

## 2. Multi-repository composition (the headline feature)

This is the part that maps best to our use case, and it is genuinely there.

**Mechanism.** Each entry in `ai-rules-sync.json` records the URL of the repo it came from. You can pull from N repos in the same project; conflict "resolution" is **per-entry, not per-file** — you give each entry a unique local name (or alias via `{ "url": "...", "rule": "<repo-name>" }`).

Example consumer config from `docs/reference/configuration.md`:

```json
{
  "version": 1,
  "claude": {
    "skills": {
      "code-review":      "https://github.com/team/private-rules.git",
      "react-patterns":   "https://github.com/community/public-rules.git",
      "react-patterns-v2": {
        "url":  "https://github.com/community/public-rules.git",
        "rule": "react-patterns"
      }
    }
  }
}
```

**Three configs merge with priority** (highest first): `ai-rules-sync.local.json` > `ai-rules-sync.json` > `~/.config/ai-rules-sync/user.json`. So a user's personal repo, a team's shared repo, and a private overlay all stack at install time.

**What it does NOT do.** There is no automatic conflict resolution between two repos that publish a skill of the same name. The user must alias one of them. There is no merge, no overlay (the value of an entry is just a URL pointing to a single source file or directory). And there is no sense of "private repo wins over public repo" beyond the name-collision-rejection behavior; the `*` wildcard tool key is for fallback, not for precedence.

For our "private team repo + public community repo" model this is good enough — we'd model both as registered repos and our marketplace UX would handle naming. But it is not a true overlay system.

## 3. Pain-by-pain mapping

| Pain | AIS coverage | Notes |
|---|---|---|
| **1. No inventory across hosts** | Partial | `ais ls` lists registered rules repos, `ais status` lists symlinks in the **current project**. There is no `ais list-everywhere` that surveys `~/.claude/skills/`, `.claude/skills/`, plugin-bundled, Cursor/Codex paths globally. Provenance lookup only works for things AIS itself created. |
| **2. Prose merge conflicts** | None | AIS has no merge story at all. Files are symlinks to a single source of truth — the only way two people "edit the same skill" is to push to the same rules repo, where ordinary git line-diff conflicts apply. AIS does not address them. |
| **3. All-or-nothing adoption** | None | An entry is the unit. You take a whole skill or you don't. No partial pull, no section-level cherry-picking. (Our deep-research report said this was a stretch problem anyway.) |
| **4. Skills don't travel alone** | None | The `ai-rules-sync.json` schema records `tool → subtype → entries → repo URL`. There is no slot for "this skill needs MCP server X" or "this skill expects slash-command Y." Bundling has to live one layer up — either in our plugin manifest, or in skill frontmatter we add ourselves. |
| **5. Public vs proprietary mix** | Partial | The `--local` flag writes to `ai-rules-sync.local.json` and auto-adds the symlink to `.git/info/exclude`. That's a per-machine-private model — fine for "I added this rule for myself," wrong for "this internal skill must never leave our private remote." There is no `visibility:` frontmatter concept and no pre-push guard. |

Net: **AIS reduces the "skills don't travel" friction modestly (because it standardizes the layout across tools) but does not directly resolve any of our five pains.**

## 4. Schema and frontmatter handling

**It does not parse or modify file contents.** Symlinks are created with `fs.ensureSymlink` (`src/sync-engine.ts` line 118); the source file is the target file. So:

- Arbitrary frontmatter round-trips byte-for-byte. Adding `visibility: public | proprietary` to a SKILL.md is safe.
- AIS does not impose its own metadata on the markdown. All AIS metadata lives in `ai-rules-sync.json` (file-level) and a `KNOWLEDGE_BASE.md` header pattern is used in **its own repo** for internal tracking only — not enforced on consumers.
- The markdown body is never touched.

The `gemini-agents` adapter reads frontmatter to support Gemini's agent format (see `src/adapters/gemini-agents.ts`), but that is a per-adapter concern and only for files AIS imports/creates, not files it relays.

This is good news for us. Our `visibility:` key is safe.

## 5. Discovery / inventory

The relevant commands:

- `ais ls` — lists registered rules repositories (`~/.config/ai-rules-sync/repos/*`).
- `ais status [--user] [--json]` — current project's symlinks and config files.
- `ais search <query>` — searches **inside the registered rules repositories** for matching entry names. Not a filesystem-wide search.
- `ais check` — git fetch on each registered repo and reports drift.

There is **no equivalent of `skillctl list` that walks `~/.claude/skills/`, `.claude/skills/`, plugin-bundled paths, Codex skill paths, etc., regardless of whether AIS installed them.** That continues to be net-new value for our tool.

## 6. Programmatic API

**Effectively none.** Inspection of `package.json`:

```json
{
  "type": "module",
  "bin": { "ais": "./dist/index.js" },
  "files": ["dist"]
}
```

There is no `main`, no `exports`, no `types` field. The package publishes a CLI binary, full stop. The TypeScript source has plenty of `export` declarations (`linkEntry`, `unlinkEntry`, `importEntry` in `src/sync-engine.ts`; the adapter registry in `src/adapters/`), but they are not part of a documented public API. The recent commit message "docs: improve structure, onboarding, and API reference (#40)" refers to the **CLI** reference docs, not a programmatic API.

If we wanted to call AIS from `skillctl`, our options are:

1. Shell out to `ais` (works, painful, brittle to flag changes).
2. Import internal modules — `import { linkEntry } from 'ai-rules-sync/dist/sync-engine.js'` — and accept that any minor version can break us (the `0.7.0` changelog mentions `refactor!: remove legacy compatibility code paths`, so they break things).
3. Vendor the parts we want (Unlicense — explicitly permitted).

Sketch of the shell-out approach:

```ts
import { execa } from 'execa';

async function aisInstall(projectPath: string) {
  await execa('ais', ['install', '--json'], { cwd: projectPath });
}

async function aisAddSkill(name: string, repoUrl: string) {
  await execa('ais', ['claude', 'skills', 'add', name, '-t', repoUrl]);
}
```

Realistic, but every command we wrap is a future maintenance liability.

## 7. Maturity signals

| Signal | Value |
|---|---|
| First commit | 2025-12-25 |
| First npm publish | 2026-01-12 (v0.3.0) |
| Latest release | v0.8.1, 2026-03-11 |
| Last commit on `main` | 2026-03-16 |
| Total commits | 82 |
| Stars / forks | 27 / 1 (per WebFetch summary; small) |
| Maintainers | Single — `lbb00` |
| Weekly downloads | Unknown (npm-stat blocked WebFetch; check manually) |
| License | Unlicense (public domain) |
| Breaking changes | v0.7.0 explicitly removed legacy compat paths; v0.8.0 reshaped `sourceDir`; pre-1.0 cadence |

**Reading.** Active for ~3 months, then quiet for ~7 weeks. Pre-1.0, single maintainer, breaking-change history on minor bumps. Not abandoned, but not load-bearing. Comparable in age to our own project. The competitor `rulesync` (different research thread) is older and broader, which is presumably why prior-art.md treats it as the substrate candidate of choice.

## 8. Smallest concrete integration

If we adopt AIS as a **recommended companion tool** rather than substrate:

```bash
# Teammate setup (one-time)
npm install -g ai-rules-sync
ais use git@github.com:our-team/skills-private.git
ais use https://github.com/anthropics/skills.git
ais install

# skillctl just inventories what's there, regardless of who installed it
skillctl list                         # walks ~/.claude/skills/, .claude/skills/, plugin paths
skillctl list --provenance            # uses ais status --json + filesystem walk to label sources
skillctl check-visibility --pre-push  # our own guard, independent of ais
```

If we adopt it as **substrate**, the smallest wrapper is:

```ts
// In skillctl, for the "pull a community skill" path
await execa('ais', ['claude', 'skills', 'add', skillName, '-t', repoUrl]);
// Then read frontmatter from the resulting symlink target ourselves
```

We would still own the inventory, merge driver, and visibility guard.

## 9. Risks of depending on it

- **Single maintainer, pre-1.0, breaking minors.** A minor bump can rearrange the config schema or rename CLI flags we shell out to.
- **Symlink-only sync model.** No copy mode. On Windows without developer mode, symlinks require admin rights. Our 4-person team is mac/linux today, but a future Windows teammate would hit this.
- **No public Node API.** We have no contract; importing internals is at our own risk.
- **Idle for 7 weeks.** Could be normal for an indie project, could be the start of abandonment. Hard to tell at this size.
- **No issue-responsiveness data.** GitHub API and `gh` CLI were unavailable in this environment so we could not measure mean-time-to-respond. Worth a manual check before any deeper bet.
- **Ecosystem overlap.** `rulesync` is older, has more stars, and already does cross-tool fan-out. If the rulesync evaluation comes back favorable, AIS is the dispensable one.

## 10. Recommendation

**Do not adopt as substrate. Use it selectively, and only as a recommended companion tool for teammates who want a shared rules repo across non-Claude tools.**

Reasoning:

- Our hardest unsolved pains (inventory, prose-merge, visibility guard) are not ones AIS addresses.
- The pain it does address — "skills live in many places per tool, copy-paste is brittle" — is real, but the tools we care most about (Claude Code's plugin/marketplace format) already have a first-party install story (`/plugin marketplace add`, `/plugin install`). AIS would just be a parallel install path with a different mental model (symlinks vs. plugins).
- Multi-repository composition is the intriguing bit, but the value to us is conceptual — it confirms that "register N repos and pull entries from each" is a reasonable model. We can absorb the design lesson without taking the dependency.
- Maturity (pre-1.0, single maintainer, ~7 weeks idle) doesn't justify making it load-bearing for our prototype. We are explicitly throwaway-ready (decisions.md decision 7), but throwaway-readiness applies to **our own code**, not to the cost of unwinding a transitive dependency mid-flight.
- vs. **rulesync** (the sibling agent's research): from public sources, rulesync is older, has more stars, and operates by **rendering** a single source-of-truth into per-tool output files rather than by symlinking. That render model is friendlier to our LLM-merge story (we own the canonical file), and friendlier to Windows. AIS's symlink model is interesting but more tightly coupled to its own worldview. We should bias toward rulesync if it covers Claude Code skills — pending the sibling agent's findings.

**Net action.** Update `prior-art.md` to demote AIS from "substrate candidate" to "useful companion tool, not load-bearing." Keep the `visibility:` plan, the inventory plan, and the LLM merge driver plan exactly as in `decisions.md`; none of them depend on AIS. Re-evaluate in 6 months — if AIS reaches 1.0, gains a documented Node API, or absorbs an inventory feature, this conclusion may flip.
