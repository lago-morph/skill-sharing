# Iteration plan

> **This is a prototype**, not a product. We're solving a specific 4-person team's pain. Each iteration is independently shippable and disposable — if a better tool ships upstream mid-flight, we abandon and adopt. After every iteration: 30-min team retro → next iteration's scope.
>
> **Initial scope: Codex CLI only.** Claude Code and other tools are deferred — see [`consider-for-later.md`](./consider-for-later.md). rulesync supports them, so adding more is mostly a `--targets` config change in `src/substrate.ts` and a few extra paths in `hosts.ts`.
>
> See [`consider-for-later.md`](./consider-for-later.md) for parked features. **Anything in that document is out of scope** unless the pilot's lived experience justifies pulling it back in.

See [problem-statement.md](./problem-statement.md) for context and [decisions.md](./decisions.md) for the design choices framing this plan.

## Iteration 0 — Repo + scaffolding (½ day)

- TypeScript project skeleton: `src/`, `test/`, `examples/`, `package.json`, `tsconfig.json`.
- Add `rulesync` as a regular dependency (pinned `^8.15`). Wrap calls behind one `src/substrate.ts` so we can swap it out later. See [rulesync-evaluation.md](./rulesync-evaluation.md).
- Two example skills under `examples/` in vanilla agentskills.io SKILL.md format. No frontmatter extensions, no schema beyond what agentskills.io defines. See [skill-schema.md](./skill-schema.md).
- `npm run smoke` script: copies an example skill into a temp `.rulesync/skills/` and runs `rulesync generate --features skills --targets codexcli` so a teammate can confirm the substrate works end-to-end with one command.

**Deliverable:** working repo, two examples, confirmed rulesync round-trip into Codex layout. Team eyeballs it before we go further.

### Try it out

```bash
git clone <repo-url> && cd skill-sharing
npm install
npm run smoke           # copies an example into .rulesync/, runs rulesync
ls .codex/skills/       # the example skill should appear here
```

## Iteration 1 — `skillctl list` (1–2 days)

- `skillctl list` walks every known Codex skill location on the machine and prints a table: name, scope (user | project), path, last-modified.
- `skillctl show <name>` prints the resolved skill (frontmatter + body).
- `hosts.ts` registry has one entry for the prototype: Codex CLI (`./.codex/skills/`, `~/.codex/skills/`). Other tools added when their support lands; see [consider-for-later.md](./consider-for-later.md).
- No network. No writes. Pure inventory of what's on the user's machine.

**Deliverable:** `npm install -g .` (or `npm link`) then `skillctl list`. Team uses it on their own machines. Tells us whether path coverage is right and whether inventory is the most useful primitive — or whether they jump straight past it to sharing.

### Try it out

```bash
cd skill-sharing && npm install && npm link
mkdir -p ~/.codex/skills/demo-skill
cat > ~/.codex/skills/demo-skill/SKILL.md <<'EOF'
---
name: demo-skill
description: Demo skill for trying skillctl list.
---
Body.
EOF
skillctl list                  # demo-skill should appear, scope=user
skillctl show demo-skill       # frontmatter + body
```

## Iteration 2 — `skillctl ls` / `pull` / `push` against a private git marketplace (3–4 days)

- A "marketplace" is just a git repo with a `.claude-plugin/marketplace.json` and a `plugins/` tree. We use the existing schema unchanged (it's a metadata convention; Codex doesn't read it). **Single private repo for the pilot** — see [decisions.md](./decisions.md) row 5.
- `skillctl ls <marketplace>` clones/updates the marketplace and lists what's available: skill name, description, last-modified. The remote-side counterpart to `skillctl list`.
- `skillctl pull <skill>@<marketplace>` clones/updates the marketplace, copies the skill into a temp `.rulesync/skills/<name>/`, and calls rulesync to fan out to Codex layout (`~/.codex/skills/<name>/`).
- `skillctl push <skill> --to <marketplace>` copies the skill (and any sibling files referenced by frontmatter `paths`/`context`) into the marketplace repo as a one-skill plugin, updates `marketplace.json`, commits, pushes.
- No merging yet. If `pull` would overwrite a locally edited skill, abort with a clear message.
- **No visibility guard, no public/private split.** All marketplaces are treated as private. The visibility design is parked in [consider-for-later.md](./consider-for-later.md).

**Deliverable:** team stands up `team-skills` (private) and round-trips a real skill end-to-end. Tells us whether plugin format is the right unit of sharing or whether a leaner "bare skill" form is needed, and whether `skillctl ls` is the right discovery surface.

### Try it out

```bash
# One-time: stand up an empty private marketplace repo
gh repo create your-org/team-skills --private --clone
cd team-skills && mkdir -p .claude-plugin plugins
echo '{"name":"team-skills","plugins":[]}' > .claude-plugin/marketplace.json
git add . && git commit -m init && git push -u origin main && cd ..

# Push a skill to it
skillctl push demo-skill --to git@github.com:your-org/team-skills.git

# On a teammate's machine
skillctl ls   git@github.com:your-org/team-skills.git    # see what's there
skillctl pull demo-skill@team-skills                     # materializes via rulesync
ls ~/.codex/skills/demo-skill                            # appeared
```

## Iteration 3 — LLM-assisted merge driver (2–3 days)

- Register a custom git merge driver via `.gitattributes` for `**/SKILL.md`. `skillctl init-merge-driver` writes the `.gitattributes` and `.git/config` entries.
- On conflict, call Claude with `(base, ours, theirs)` and a prompt-cached system instruction: "merge these three versions of an AI skill, preserving both authors' intent; output the merged markdown only." Write the result with a `<!-- SKILLCTL: review required -->` marker so the user can't merge without looking.
- `skillctl merge <skill>` does the same on demand without going through git.
- **No section schema. No structural diff.** Just `(base, ours, theirs)` → LLM → reviewed candidate. If output quality is poor, that's the signal to revisit a structured approach (parked in [consider-for-later.md](./consider-for-later.md)).

**Deliverable:** real concurrent-edit story. Tells us whether the LLM merge output is good enough for the team to trust.

### Try it out

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd team-skills && skillctl init-merge-driver

# Simulate a conflict on demo-skill
git checkout -b alice
printf '\nAlice added this line.\n' >> plugins/demo-skill/SKILL.md
git commit -am alice

git checkout main && git checkout -b bob
printf '\nBob added a different line here.\n' >> plugins/demo-skill/SKILL.md
git commit -am bob

git merge alice                                          # driver runs Claude
cat plugins/demo-skill/SKILL.md                          # merged + review marker
```

## Stretch / deferred

Almost everything that used to live in "stretch" has moved to [consider-for-later.md](./consider-for-later.md). The prototype's scope is iter-0 through iter-3. Anything beyond that — including support for tools other than Codex CLI — needs an explicit re-scoping decision.

## What we explicitly cut from earlier drafts (and why)

- **AGENTS.md export iteration:** delegated to rulesync. No code from us.
- **Public/private marketplace split + visibility guard (was iter-2):** deferred — pilot uses only private repos. See [consider-for-later.md](./consider-for-later.md).
- **Overlay iteration:** deferred. See [consider-for-later.md](./consider-for-later.md).
- **Section schema:** dropped. We use agentskills.io SKILL.md unchanged. See [skill-schema.md](./skill-schema.md).
- **Claude Code support in v1:** deferred. Codex CLI only for the prototype. See [consider-for-later.md](./consider-for-later.md).

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
│   ├── consider-for-later.md
│   ├── rulesync-evaluation.md
│   ├── ai-rules-sync-evaluation.md
│   ├── research-brief.md
│   └── deep-research-report.md
├── src/
│   ├── cli.ts                   # commander entry point
│   ├── hosts.ts                 # path registry — Codex CLI only for the prototype
│   ├── inventory.ts             # iter 1: list/show
│   ├── marketplace.ts           # iter 2: ls/pull/push, marketplace.json IO
│   ├── substrate.ts             # rulesync wrapper (iter 0+)
│   ├── merge.ts                 # iter 3: LLM 3-way merge
│   └── llm.ts                   # @anthropic-ai/sdk wrapper, prompt cache enabled
├── test/
└── examples/
    ├── example-skill-a/
    └── example-skill-b/
```

## Verification plan

- **Iter 0:** team eyeballs the rulesync round-trip on the example skills. Confirm the substrate produces what the user expects in `.codex/skills/`.
- **Iter 1:** every team member runs `skillctl list` on their machine; we confirm coverage of Codex paths matches reality (any missing path is a bug).
- **Iter 2:** stand up `team-skills` (private) and round-trip a real skill end-to-end. `skillctl ls team-skills` shows it; `skillctl pull` materializes it via rulesync; `skillctl push` puts a new version back.
- **Iter 3:** seed a real conflict (two team members edit the same skill differently), let the merge driver run, hand the result to a third reviewer who wasn't involved in the edits — they should be able to adjudicate quickly.

## Open questions (re-confirm at each iteration boundary)

- **Is `skillctl list` actually wanted?** If the team skips straight to `pull`, Iter 1 is busywork.
- **Is `skillctl ls <marketplace>` worth a discrete command, or should `list --remote` cover it?** Decide in iter-2.
- **Unit pushed to marketplace:** single-skill plugin (lean) vs. named bundle (logical grouping). **Default: single-skill plugins.**
- **Stop conditions.** If Anthropic / OpenAI / GitHub / rulesync ships the equivalent of any iteration before we land it, we abandon and adopt. This is a feature, not a failure.
