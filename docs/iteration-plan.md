# Iteration plan

Each iteration is independently shippable and produces something the team can try. After every iteration: 30-min team retro → next iteration's scope.

See [problem-statement.md](./problem-statement.md) for context and [decisions.md](./decisions.md) for the design choices framing this plan.

## Iteration 0 — Repo + skill conventions (½ day)

- Lay down repo skeleton: `skillctl/` (Python package), `tests/`, `docs/`, `examples/`.
- Define the **section schema** for skills (frontmatter + named H2 sections: `## Purpose`, `## When to use`, `## Procedure`, `## Examples`, `## References`, `## Anti-patterns`). Every section optional except `Purpose` and `When to use`. See [skill-schema.md](./skill-schema.md).
- Add `visibility: public | proprietary` to the frontmatter (extension on top of Claude Code's frontmatter — Claude Code ignores unknown keys).
- Two example skills committed under `examples/` in the canonical schema.

**Deliverable:** repo + a one-page `skill-schema.md`. Team reviews schema, pushes back, we revise.

## Iteration 1 — `skillctl list` (1–2 days)

- `skillctl list` walks every known location on the machine and prints a table: name, host (claude-code | codex | …), scope (user | project | plugin), path, visibility, last-modified.
- `skillctl show <name>` prints the resolved skill (frontmatter + body).
- Detection paths come from a small `hosts.py` registry; one entry per supported host. Start with Claude Code (3 paths) and Codex (`AGENTS.md` discovery in cwd / parents / `~/.codex/`).
- No network. No writes. Pure inventory.

**Deliverable:** `pip install -e .` then `skillctl list`. Team uses it on their own machines. Tells us whether path coverage is right and whether the table is the right surface.

## Iteration 2 — `skillctl push` / `skillctl pull` against a git marketplace (3–4 days)

- A "marketplace" is just a git repo with a `.claude-plugin/marketplace.json` and a `plugins/` tree. We use the existing schema unchanged.
- `skillctl push <skill> --to <marketplace>`: copies the skill (and any sibling files referenced by frontmatter `paths`/`context`) into the marketplace repo as a one-skill plugin, updates `marketplace.json`, commits, pushes.
- `skillctl pull <skill>@<marketplace>`: clones/updates the marketplace, copies the skill into `~/.claude/skills/` (or installs as a plugin via `/plugin` instructions if the user prefers).
- **Visibility guard:** before pushing, check the skill's `visibility:` against a `marketplace.visibility` declared in the marketplace's `marketplace.json`. Refuse `proprietary → public`.
- No merging yet. If `pull` would overwrite a locally-edited skill, abort with a clear message.

**Deliverable:** the team can stand up one private and one public marketplace repo and exchange skills. Tells us whether plugin format is the right unit of sharing or whether we need a leaner "bare skill" format.

## Iteration 3 — Section-aware diff + LLM 3-way merge (3–5 days)

- `skillctl diff <skill> [--against <marketplace>]`: structural diff that shows which sections changed, not raw line diff.
- `skillctl merge <skill>`: when local and remote both changed the same skill from a common base, do a section-by-section merge:
  - Sections changed on only one side → take that side.
  - Sections changed on both sides → invoke Claude (`anthropic` SDK, prompt-cached) with `(base, ours, theirs)` and produce a merge candidate; write to `<skill>.merged.md` for the user to review.
- Optional: register as a custom git merge driver via `.gitattributes` so `git merge` calls into us automatically when merging marketplace pulls.
- Add `skillctl pull --merge` to chain pull + merge.

**Deliverable:** real concurrent-edit story. Tells us whether the section schema holds up and whether LLM-merge output quality is acceptable, or whether we need to tighten the schema (e.g. stable section IDs).

## Iteration 4 — AGENTS.md export (2–3 days)

- `skillctl export <skill> --as agents-md`: render a skill into an AGENTS.md fragment (drop Claude-specific frontmatter, flatten sections to plain prose).
- `skillctl install <skill> --host codex` (and `--host cursor`, `--host aider`, etc.): write the AGENTS.md output into the right location for that host.
- Round-trip: `skillctl pull` for an AGENTS.md-consuming host installs the skill as AGENTS.md content; for a Claude Code user installs as SKILL.md.
- Document the lossy fields (e.g. `allowed-tools` doesn't survive the trip to AGENTS.md).
- **One adapter, many hosts** — because AGENTS.md is the broadly-supported standard, not just Codex.

**Deliverable:** non-Claude-Code users on the team can consume the same shared skills. Tells us how lossy the AGENTS.md bridge is in practice.

## Iteration 5 — Base + overlay composition (3–5 days)

- Each user can keep `~/.claude/skill-overlays/<skill>.overlay.md` with section-level overrides: `replace`, `append`, `disable`.
- On `pull`, base and overlay are kept separate; on activation (or via a `skillctl materialize` step) they're combined into the on-disk SKILL.md that Claude Code actually reads.
- `skillctl pull` updates the base; the overlay survives.

**Deliverable:** people can adopt a shared skill while keeping personal tweaks. Tells us whether overlay is the right model or whether forks-with-rebase would be simpler.

## Stretch (post-feedback)

- `skillctl new --from-transcript`: generate a skill from a Claude Code session transcript.
- `skillctl refactor <skill>`: agent that improves progressive disclosure, splits oversized skills, externalizes examples.
- VS Code extension surface for `list` / `pull` / `diff`.
- First-party Cursor / Continue host adapters (beyond what AGENTS.md export covers).
- Cross-marketplace lockfile (`skillctl.lock`) pinning sources across Claude Code plugins, Cursor plugins, Continue Hub, raw GitHub Skills repos.

---

## Critical files / structure

```
skill-sharing/
├── pyproject.toml
├── README.md
├── docs/
│   ├── problem-statement.md
│   ├── decisions.md
│   ├── prior-art.md
│   ├── iteration-plan.md
│   ├── skill-schema.md
│   └── research-brief.md
├── skillctl/
│   ├── __init__.py
│   ├── cli.py                   # Typer entry point
│   ├── hosts.py                 # path registries per host
│   ├── inventory.py             # iter 1: list/show
│   ├── marketplace.py           # iter 2: push/pull, marketplace.json IO
│   ├── visibility.py            # iter 2: pre-push guard
│   ├── schema.py                # iter 0/3: frontmatter + section parsing
│   ├── merge.py                 # iter 3: section diff + LLM 3-way merge
│   ├── codex.py                 # iter 4: AGENTS.md adapter
│   ├── overlay.py               # iter 5: base + overlay
│   └── llm.py                   # thin wrapper over anthropic SDK, prompt cache enabled
├── tests/
└── examples/
    ├── public-skill/
    └── proprietary-skill/
```

## Verification plan

Each iteration ends with two complementary checks:

1. **pytest** — automated unit/integration tests that run in CI.
2. **Sandbox smoke test** — Claude exercises the CLI end-to-end in the dev
   environment, creates real fixture files, and confirms the golden path and
   key edge cases behave correctly. Results are recorded below as each
   iteration is completed.

### Iter 0 — Schema parser

*pytest:* schema parser round-trips, section-ID extraction, edge cases.

*Sandbox smoke test:*
- Parse both `examples/` skills via the Python API; print name, visibility,
  section headings.
- Verify `skillctl --help`, `skillctl list` (stub), and `skillctl show` (stub)
  exit cleanly.
- Confirm `dump_skill(parse_skill(text)) == parse_skill(dump_skill(…))` holds
  on both example files (idempotent round-trip).

### Iter 1 — `skillctl list` / `skillctl show`

*pytest:* inventory walker finds skills at mocked paths; missing dirs are
skipped cleanly; `show` renders correct output.

*Sandbox smoke test:*
- Plant a skill file at `~/.claude/skills/test-skill/SKILL.md` and one at
  `.claude/skills/project-skill/SKILL.md` in a temp project dir.
- Run `skillctl list`; verify both rows appear with correct host, scope, and
  visibility columns.
- Run `skillctl show test-skill`; verify full frontmatter + body is printed.
- Remove the planted files; confirm `skillctl list` shows an empty table
  rather than crashing.

### Iter 2 — `skillctl push` / `skillctl pull`

*pytest:* marketplace.json IO, visibility guard logic, overwrite-abort
message, happy-path copy.

*Sandbox smoke test:*
- `git init` a temp dir as a public marketplace (set `marketplace.visibility:
  public` in `marketplace.json`).
- Push `examples/public-skill` to it; confirm the plugin tree and updated
  `marketplace.json` are committed in the marketplace repo.
- Pull it back to a fresh location; confirm the skill file appears.
- Attempt to push `examples/proprietary-skill` to the public marketplace;
  confirm the guard refuses with a clear error.
- Attempt a second pull to the same location (overwrite scenario); confirm
  the abort message fires.

### Iter 3 — Section-aware diff + LLM 3-way merge

*pytest:* section diff identifies correct changed sections; same-side-only
changes are auto-resolved; both-sides conflicts route to `llm.merge` (mocked
in tests).

*Sandbox smoke test:*
- Create a base skill and two diverged variants (edit `## Procedure` in one,
  `## Examples` in the other; edit `## Purpose` in both).
- Run `skillctl diff`; confirm output shows only the changed sections.
- Run `skillctl merge`; confirm `## Procedure` and `## Examples` are
  auto-resolved and only `## Purpose` is handed to Claude for a merge
  candidate.
- Inspect the `.merged.md` output for coherence.

### Iter 4 — AGENTS.md export

*pytest:* Claude-specific frontmatter keys stripped; sections flattened to
prose; output is valid markdown.

*Sandbox smoke test:*
- Export both example skills with `skillctl export --as agents-md`.
- Confirm `allowed-tools`, `visibility`, `depends_on`, `origin` are absent
  from the output.
- Confirm section headings are rendered as prose paragraphs (no H2s with
  schema names).
- Copy the output into a temp `AGENTS.md` in a fresh dir; confirm a
  `skillctl list` run with the Codex host adapter picks it up.

### Iter 5 — Base + overlay composition

*pytest:* overlay `replace`/`append`/`disable` directives applied correctly;
base update preserves overlay; materialize output matches expectation.

*Sandbox smoke test:*
- Pull a base skill; write an overlay that replaces `## Procedure` and
  appends to `## When to use`.
- Run `skillctl materialize`; confirm the output contains the replaced
  procedure and the appended when-to-use, with all other sections from base.
- Simulate a base update (edit base file); re-materialize; confirm overlay
  still applies and the updated base sections flow through.

## Open questions (recommendations, to be re-confirmed at each iteration boundary)

- **Unit pushed to marketplace:** single-skill plugin (lean, every skill is a plugin) vs. named bundle (logical grouping). **Recommend single-skill plugins in v1.**
- **Common base for 3-way merge:** store the last-pulled version of every shared skill under `~/.cache/skillctl/base/<marketplace>/<skill>.md` so a base always exists.
- **Server-side visibility check:** add a small GitHub Action on the public marketplace that fails the build if any `visibility: proprietary` slips through. Defense in depth alongside the client-side pre-push guard.
- **Conformance target for SKILL.md:** write skills to the cross-tool **agentskills.io spec** (not Claude Code's superset) so they portably install on Codex/others without extra translation. Claude Code-specific frontmatter keys live in an optional namespace.
