# Consider for later

> **AI sessions and human readers, please read this carefully before doing anything else with this file.**
>
> **Nothing in this document is in scope for the current iteration plan.** The ideas here are deliberately deferred. They are recorded so we don't lose them, not so we can build them.
>
> Do **not** treat any feature in this file as a requirement, a near-term roadmap item, or guidance for current implementation. If you are an AI assistant helping with this project, **read [`iteration-plan.md`](./iteration-plan.md) and [`decisions.md`](./decisions.md) for what is actually in scope.** If a user request seems to ask for something here, surface that this is parked work and ask before pulling it in.
>
> The trigger for moving any of this back into scope is **the pilot team explicitly identifying it as the most painful unresolved problem**, not "we have time" or "it would be nice."

This document holds enterprise-type features and ambitions that the deep-research review and the prototype framing both told us to push out. The 4-person pilot doesn't need them. A 30-person rollout might. A commercial product certainly would. Pull from this list when (and only when) the pilot's lived experience justifies it.

---

## Public / private marketplace split, visibility frontmatter, pre-push guard

The original design had two marketplaces — one public, one private — and a `visibility:` frontmatter key with a pre-push guard. Parked.

- **Frontmatter extension:** `visibility: public | proprietary` on each skill. `proprietary` is the conservative default.
- **Marketplace declaration:** each marketplace's `marketplace.json` declares `marketplace.visibility: public | proprietary`.
- **Pre-push guard:** `skillctl push` refuses to write a `proprietary` skill into a `public` marketplace.
- **Server-side guard (defense in depth):** a GitHub Action on the public marketplace fails the build if any committed `SKILL.md` carries `visibility: proprietary`.

**Why deferred for the pilot:** the pilot uses **only private repositories**. Without a public surface, there is nothing to leak to. The dual-repo model and visibility guard solve a problem we don't yet have. Adding them upfront forces decisions about defaults, semantics, and exception flows before we know the pilot's actual workflow.

**Trigger for re-scoping:** pilot wants to share a skill with someone outside the team, or wants to publish a subset of the team's skills as open source.

**rulesync interaction:** when this is revived, verify that an unknown `visibility:` key survives `rulesync generate --features skills` for both `claudecode` and `codexcli`. rulesync uses `gray-matter` at parse time but rebuilds frontmatter from a known-key model on emit, so unknown keys may be stripped. If they are, the canonical skill source has to live outside `.rulesync/skills/` (or visibility is reapplied after generation). See [rulesync-evaluation.md](./rulesync-evaluation.md) §3.

## Provenance, registry, and catalog metadata

Tracked metadata that would matter at scale and is overkill for a pilot:

- Ownership / maintainer per skill.
- Last-reviewed timestamp; staleness signals.
- Compatibility (which Claude Code / Codex / rulesync versions this skill was tested with).
- Trust / provenance chain (who created it, who modified it, signed commits).
- Adoption / usage metrics (how many teammates have it pulled).

The deep-research report identified this as the strongest defendable layer for a *commercial* product. We are not building a commercial product.

**Trigger for re-scoping:** pilot reports they can't tell which shared skill is canonical or current.

## Overlay / base+override composition

chezmoi-style per-user customization on top of a shared skill: `~/.claude/skill-overlays/<skill>.overlay.md` with section-level `replace` / `append` / `disable`. Resolves at materialization time. Solves [pain 3 — all-or-nothing adoption](./problem-statement.md).

**Why deferred:** premature until the pilot reports that "all-or-nothing adoption" is actually the most painful unresolved issue. Forks-with-rebase may be enough at 4 people.

**Trigger for re-scoping:** ≥2 pilot members fork a shared skill and ask "how do I keep my edit while pulling updates."

## Section schema and structure-aware merge

Stable named-H2 sections (`## Purpose`, `## When to use`, `## Procedure`, …) with optional HTML-comment IDs (`<!-- id: proc -->`), enabling section-by-section three-way merge. The deep-research report found no clear evidence the structure pays off for prose, so we ship the dumb LLM merge driver instead.

**Trigger for re-scoping:** the LLM merge driver from iter-3 produces results the team won't trust, *and* the team agrees a structure tax is worth paying.

## RBAC, sub-teams, fine-grained access controls

`public | proprietary` is enough granularity for ≤30 people. Anything finer is enterprise IAM.

**Trigger for re-scoping:** none within the prototype's scope. If we ever need this, the answer is "use a real product, not this one."

## Registry server / hosted UI

A server that catalogs marketplaces, provides search, hosts a UI, runs server-side validation, etc. Git is the substrate; we're not running infrastructure.

**Trigger for re-scoping:** none within the prototype's scope.

## First-party adapters beyond what rulesync covers

If a tool the team uses isn't supported by rulesync, we'd write our own adapter. As of `rulesync@8.x` it covers ~25 tools including the ones we care about.

**Trigger for re-scoping:** team adopts a tool with no rulesync support.

## Cross-marketplace lockfile

`skillctl.lock` pinning sources across multiple marketplaces — Cargo/npm-style resolution. Only matters when the team is mixing many sources.

**Trigger for re-scoping:** pilot uses ≥3 marketplaces simultaneously.

## Skill generation tools

- `skillctl new --from-transcript` — generate a SKILL.md from a Claude Code session transcript.
- `skillctl refactor <skill>` — agent that improves progressive disclosure, splits oversized skills, externalizes examples.

The deep-research report flagged "no standalone transcript→SKILL.md CLI exists" as a real gap. Anthropic's `skill-creator` lives inside Claude Code itself, which arguably makes it Anthropic's problem.

**Trigger for re-scoping:** pilot reports authoring is the bottleneck, not sharing or merging.

## VS Code / IDE surfaces

Native VS Code extension or JetBrains plugin for `list` / `pull` / `diff`.

**Trigger for re-scoping:** pilot members consistently complain that the CLI breaks their flow.
