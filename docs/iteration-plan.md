# Iteration plan

> **This is a prototype**, not a product. We're solving a specific 4-person team's pain. Each iteration is independently shippable and disposable — if a better tool ships upstream mid-flight, we abandon and adopt. After every iteration: 30-min team retro → next iteration's scope.

See [problem-statement.md](./problem-statement.md) for context and [decisions.md](./decisions.md) for the design choices framing this plan.

## Iteration 0 — Repo + scaffolding (½ day)

- TypeScript project skeleton: `src/`, `test/`, `examples/`, `package.json`, `tsconfig.json`.
- Decide between `rulesync` and `ai-rules-sync` as the cross-tool substrate by reading both READMEs. Pin the choice as a peer dependency.
- Two example skills under `examples/` in vanilla agentskills.io SKILL.md format with the `visibility:` frontmatter extension. No schema beyond what agentskills.io defines. See [skill-schema.md](./skill-schema.md).
- Smoke test: the chosen substrate can fan one of the example skills out to Claude Code + Codex layouts.

**Deliverable:** working repo, two examples, confirmed substrate. Team eyeballs it and confirms TypeScript / chosen substrate feel right before we go further.

## Iteration 1 — `skillctl list` (1–2 days)

- `skillctl list` walks every known skill location on the machine and prints a table: name, host (claude-code | codex | …), scope (user | project | plugin), path, visibility, last-modified.
- `skillctl show <name>` prints the resolved skill (frontmatter + body).
- Detection paths come from a small `hosts.ts` registry; one entry per supported host. Start with Claude Code (3 paths) and Codex (`AGENTS.md` discovery in cwd / parents / `~/.codex/`).
- No network. No writes. Pure inventory.

**Deliverable:** `npm install -g .` (or local link) then `skillctl list`. Team uses it on their own machines. Tells us whether path coverage is right and whether inventory is the most useful primitive — or whether they jump straight past it to sharing.

## Iteration 2 — `skillctl push` / `skillctl pull` against a git marketplace (3–4 days)

- A "marketplace" is just a git repo with a `.claude-plugin/marketplace.json` and a `plugins/` tree. We use the existing schema unchanged.
- `skillctl push <skill> --to <marketplace>`: copies the skill (and any sibling files referenced by frontmatter `paths`/`context`) into the marketplace repo as a one-skill plugin, updates `marketplace.json`, commits, pushes.
- `skillctl pull <skill>@<marketplace>`: clones/updates the marketplace, copies the skill into `~/.claude/skills/`, optionally invokes the substrate (rulesync/ai-rules-sync) to fan out to other tools.
- **Visibility guard:** before pushing, check the skill's `visibility:` against a `marketplace.visibility` declared in the marketplace's `marketplace.json`. Refuse `proprietary → public`.
- No merging yet. If `pull` would overwrite a locally-edited skill, abort with a clear message.

**Deliverable:** the team can stand up one private and one public marketplace repo and exchange skills. Tells us whether plugin format is the right unit of sharing or whether we need a leaner "bare skill" format.

## Iteration 3 — LLM-assisted merge driver (2–3 days)

- Register a custom git merge driver via `.gitattributes` for `**/SKILL.md`.
- On conflict, call Claude with `(base, ours, theirs)` and a prompt-cached system instruction: "merge these three versions of an AI skill, preserving both authors' intent; output the merged markdown only." Write the result with a `<!-- SKILLCTL: review required -->` marker so the user can't merge without looking.
- `skillctl merge <skill>` does the same on demand without going through git.
- **No section schema. No structural diff.** Just `(base, ours, theirs)` → LLM → reviewed candidate. If output quality is poor, that's the signal to revisit a structured approach.

**Deliverable:** real concurrent-edit story. Tells us whether the LLM merge output is good enough for the team to trust, or whether structure-aware merging is worth its tax.

## Stretch (post-pilot, only if validated)

- **Overlay / base+override composition** — only if "all-or-nothing adoption" turns out to be the most painful unresolved issue after Iter 1–3.
- **`skillctl new --from-transcript`** — generate a skill from a Claude Code session transcript.
- **`skillctl refactor <skill>`** — agent that improves progressive disclosure, splits oversized skills, externalizes examples.
- **First-party adapters** for tools that the substrate doesn't cover well.
- **Cross-marketplace lockfile** (`skillctl.lock`) pinning sources across multiple marketplaces.

## What we explicitly cut from earlier drafts (and why)

- **AGENTS.md export iteration:** delegated to rulesync / ai-rules-sync. No code from us.
- **Overlay iteration:** moved to stretch. Cannot justify the complexity until the pilot tells us it's the bottleneck.
- **Section schema (prior `skill-schema.md`):** dropped as a v1 deliverable. We use agentskills.io SKILL.md unchanged plus a `visibility:` frontmatter key. See [skill-schema.md](./skill-schema.md) for the resulting one-pager.

---

## Critical files / structure

```
skill-sharing/
├── package.json
├── tsconfig.json
├── README.md
├── docs/
│   ├── problem-statement.md
│   ├── decisions.md
│   ├── prior-art.md
│   ├── iteration-plan.md
│   ├── skill-schema.md
│   ├── research-brief.md
│   └── deep-research-report.md
├── src/
│   ├── cli.ts                   # commander entry point
│   ├── hosts.ts                 # path registries per host
│   ├── inventory.ts             # iter 1: list/show
│   ├── marketplace.ts           # iter 2: push/pull, marketplace.json IO
│   ├── visibility.ts            # iter 2: pre-push guard
│   ├── merge.ts                 # iter 3: LLM 3-way merge
│   └── llm.ts                   # @anthropic-ai/sdk wrapper, prompt cache enabled
├── test/
└── examples/
    ├── public-skill/
    └── proprietary-skill/
```

## Verification plan

- **Iter 0:** team eyeballs the substrate round-trip on the example skills. Yes/no on `rulesync` vs `ai-rules-sync` and on TypeScript.
- **Iter 1:** every team member runs `skillctl list` on their machine; we confirm coverage matches reality (any missing path is a bug).
- **Iter 2:** stand up `team-skills-public` and `team-skills-private` repos; round-trip a real skill end-to-end. Verify the visibility guard refuses a deliberate proprietary-to-public push.
- **Iter 3:** seed a real conflict (two team members edit the same skill differently), let the merge driver run, hand the result to a third reviewer who wasn't involved in the edits — they should be able to adjudicate quickly.

## Open questions (re-confirm at each iteration boundary)

- **`rulesync` vs. `ai-rules-sync` as substrate.** Decide in Iter 0. ai-rules-sync's multi-repo composition is the more interesting feature for our marketplace model; rulesync is broader.
- **Is `skillctl list` actually wanted?** If the team skips straight to `pull`, Iter 1 is busywork.
- **Unit pushed to marketplace:** single-skill plugin (lean) vs. named bundle (logical grouping). **Default: single-skill plugins.**
- **Stop conditions.** If Anthropic / OpenAI / GitHub / rulesync ships the equivalent of any iteration before we land it, we abandon and adopt. This is a feature, not a failure.
