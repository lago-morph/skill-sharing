# Deep-research brief: AI skill sharing for small teams

> **How to use this file:** paste the entire contents into a deep-research agent (ChatGPT Deep Research, Gemini Deep Research, Perplexity, Claude with web search, etc.). The brief is self-contained — the researcher does not need access to the rest of this repository.

---

## Your role

You are a research analyst. Your job is to pressure-test a design for a tool that helps small teams share AI agent "skills" across multiple coding-assistant platforms. I'll give you the problem framing, the decisions we've already locked in, our current understanding of the landscape, and our planned implementation approach. I want you to:

1. Find and summarize what other people have written about these problems (blog posts, papers, conference talks, Hacker News / Reddit discussions, post-mortems, RFC threads).
2. Survey what already exists in the marketplace — both direct competitors and adjacent tools that could substitute or be built on.
3. Identify what in our plan is **genuinely novel** vs. what already exists and we may be unaware of.
4. Suggest revisions to scope, sequence, or technical approach. Flag where we may be solving the wrong problem, where the problem is harder than we think, and where we are over- or under-scoped.

Be skeptical. Cite sources. If the evidence is thin, say so rather than embellishing.

---

## What we're building (one paragraph)

A Python CLI (`skillctl`) plus a small set of conventions that lets a 4-person team inventory, share, merge, and selectively customize natural-language "skills" used by AI coding assistants (Claude Code, Codex, Cursor, Aider, etc.). Sharing happens via git-backed marketplaces (one public, one proprietary). Merges of concurrent prose edits use a section-aware schema with an LLM-assisted three-way merge for same-section conflicts. Skills are bundled with their MCP/tool dependencies via the existing Claude Code plugin format and exported to non-Claude hosts via AGENTS.md.

---

## The problem (five concrete pains)

1. **No inventory.** Skills live in many places: per-user (`~/.claude/skills/`), per-project (`.claude/skills/`), bundled inside installed plugins, and in tool-specific locations for Codex / Cursor / etc. There is no single command that says "here is everything I have, and where it came from."
2. **Prose doesn't merge with line-diff.** Skills are markdown. Two people editing the same skill — even non-conflicting edits — routinely produce git conflicts that are unresolvable line-by-line because one of them reorganized sections.
3. **All-or-nothing adoption.** A teammate's update to a shared skill may help one user and hurt another. Today the only options are "accept the whole new version" or "fork." There is no clean way to take part of a change.
4. **Skills don't travel alone.** Many skills depend on MCP servers, tools, or slash commands. Sharing the SKILL.md without those dependencies produces a broken skill on the recipient's machine.
5. **Public vs. proprietary mix.** Some skills are fine to share publicly; others encode internal practice and must not leak. Today nothing prevents an accidental push to a public remote.

We are explicitly **not** trying to solve in v1: RBAC / sub-teams / fine-grained access; a registry server or hosted UI; first-party Cursor/IDE adapters; automatic skill generation from chat transcripts (those last two are stretch goals).

---

## Decisions we've already made

| # | Decision | Rationale |
|---|---|---|
| 1 | **Audience: individuals / small groups** in v1. Git remotes alone, no registry server. | Fastest path to a usable tool for a 4-person team. |
| 2 | **Cross-tool from day one: Claude Code + Codex.** | Half the team uses each. AGENTS.md makes the second host cheap. |
| 3 | **Merge: section schema + LLM 3-way merge** for same-section conflicts. | Section schema makes most merges conflict-free; LLM merge handles the rest with a human review gate. |
| 4 | **Visibility: two marketplaces + pre-push guard.** Frontmatter `visibility: public \| proprietary`. | Cheap, deterministic, defers RBAC. |
| 5 | **Implementation language: Python.** | Fits LLM tooling and the team's skillset. |
| 6 | **Pace: small iterations**, each independently shippable, with a 30-min retro between iterations. | Vision will change as the team uses it. |

---

## Our current understanding of the landscape (please challenge)

This is what our initial research turned up. Where it's wrong, outdated, or shallow, correct it.

### Things we plan to build on (not reinvent)

- **Claude Code plugin/marketplace format** (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) as the on-disk and on-git bundle. Spec: `code.claude.com/docs/en/plugins-reference.md`, `code.claude.com/docs/en/plugin-marketplaces.md`.
- **Agent Skills specification** (`agentskills.io/specification`) — released by Anthropic Dec 2025, adopted by OpenAI/Codex and most major tools. Defines SKILL.md + frontmatter + `scripts/` / `references/` / `assets/`.
- **AGENTS.md** (`agents.md`, repo `agentsmd/agents.md`) — donated to the Agentic AI Foundation Dec 2025. Native support across Codex, GitHub Copilot, Cursor, Windsurf, Amp, Devin, Jules, Gemini, Factory, Zed, RooCode, Continue.dev, Aider, OpenHands.
- **Python libs:** `python-frontmatter`, `marko` (CommonMark AST), `merge3` (three-way merge primitive), `GitPython`, `anthropic` SDK, `typer`.

### Direct competitors we know about

| Tool | Scope | Maturity | Gap we believe exists |
|---|---|---|---|
| `dyoshikawa/rulesync` (Node) | Fan-out one source to many tools | Mature-ish | No overlays, no prose merge, no proprietary/public split |
| `lbb00/ai-rules-sync` (Node) | Similar to rulesync | Mature-ish | Same |
| `runkids/skillshare` | Skill sharing | Newer | Unclear scope |
| `anthropics/skills`, `anthropics/claude-plugins-official` | Official Anthropic catalogs | Stable | Passive content; not a sync tool |
| LangSmith Hub, PromptHub, Promptfoo | Prompt management | Mature | Prompt-centric, not AGENTS.md/Skills aware |
| Curation lists: `wshobson/agents`, `awesome-skills.com`, `claudemarketplaces.com`, `skillsmp.com`, `travisvn/awesome-claude-skills` | Discovery | Active | Not sharing/sync tools |

### Semantic / LLM merge landscape

- **Mergiraf** (`mergiraf.org`) — mature tree-sitter merge, 33+ languages, code-focused.
- **Weave** (`github.com/ataraxy-labs/weave`) — newer, claims markdown support.
- **difftastic** — structural diff, markdown via tree-sitter (recent).
- We believe **no mature standalone LLM merge driver exists** for prose — only DIY shell wrappers registering Claude as a custom git driver.

### Dotfile / overlay analogues

- **chezmoi**, **yadm**, **dotbot**, **Dotter** — none AI-config-aware.

### Skill-from-transcript

- Anthropic's **skill-creator** lives inside Claude Code (not a standalone CLI). Console **Prompt Generator** is web-only. We believe **no standalone transcript→SKILL.md CLI exists.**

### Where we believe the tool earns its keep

1. **Overlay model** on top of AGENTS.md + SKILL.md (chezmoi-style base + per-host/per-tool/per-team layers).
2. **Section-aware + LLM 3-way merge for prose.**
3. **Standalone transcript → SKILL.md** (stretch).
4. **Cross-marketplace install with a lockfile** (stretch).

---

## Our planned approach (six iterations)

| Iter | Scope | Deliverable |
|---|---|---|
| 0 | Repo skeleton, section schema spec, two example skills, frontmatter `visibility:` | One-page schema doc team can review |
| 1 | `skillctl list` / `show` — pure inventory across Claude Code + Codex paths | `pip install -e .`; team runs on their machines |
| 2 | `skillctl push` / `pull` against a git marketplace; pre-push visibility guard | Public + private marketplace repos round-tripping a real skill |
| 3 | Section-aware diff + LLM 3-way merge driver | Real concurrent-edit story with an LLM-merged candidate the user reviews |
| 4 | AGENTS.md export covering Codex, Cursor, Aider, Continue, Copilot via one adapter | Non-Claude users on the team can consume shared skills |
| 5 | Base + overlay composition (`replace` / `append` / `disable` per section) | Users adopt shared skills while keeping personal tweaks |
| Stretch | `--from-transcript`, `refactor` agent, VS Code surface, lockfile | TBD after feedback |

The full schema and iteration plan are spelled out in adjacent files in our repo, but the table above is enough for you to evaluate scope and sequencing.

---

## Specific research questions

Please address each. Cite sources. Indicate confidence.

### A. Prior art we may have missed

A1. Are there other tools — including unreleased / WIP / academic — that solve the **same combination** of problems (cross-tool sync + prose merge + visibility split + dependency bundling)? Look beyond GitHub: company engineering blogs, VC-funded stealth tools, internal tools that were open-sourced quietly.

A2. Have any organizations (Anthropic, OpenAI, GitHub, Cursor, Continue, Sourcegraph, Replit, Vercel, JetBrains, Google) signaled they are building first-party tooling in this space? Roadmaps, RFCs, dev forum posts, conference talks, job postings.

A3. Are there mature LLM-as-merge-driver implementations we've missed? Specifically search for: `git merge driver llm`, `semantic merge prose`, `markdown three-way merge`, custom drivers wired to Claude / GPT-4 / Gemini.

A4. Is there an established convention for **section-stable IDs in markdown** (the `<!-- id: foo -->` pattern) that we should match rather than invent?

### B. Writing about these problems

B1. What have practitioners written about the prose-merge problem for AI prompts, rules, or instructions? Specifically: are there post-mortems or retrospectives from teams who hit this and what did they do?

B2. What's been written about **organizational patterns** for sharing AI skills/rules/prompts across a team? (Onboarding docs, SRE-style runbooks, internal playbooks.) Are there established patterns we should adopt rather than invent?

B3. Are there academic or industry papers on **collaborative editing of prompts / instructions** at the team or organization scale?

B4. What does the AGENTS.md community discussion look like? Where is the spec going? Are there active proposals for extending it? (Look at the agentsmd/agents.md repo issues, the Agentic AI Foundation, related W3C or IETF activity.)

### C. Where our framing or approach might be wrong

C1. **Is the section schema premature standardization?** Skills today are free-form markdown; forcing a section structure may create friction. What's the strongest argument against this approach? Are there alternative merge strategies (e.g., paragraph-level semantic chunking, embedding-based diff) that don't require a schema?

C2. **Is overlay the right composition model**, or would a fork-with-rebase / patch-stack model serve a 4-person team better? What do dotfile communities actually use in practice?

C3. **Is "cross-tool from day one" worth the extra scope?** Would shipping Claude-Code-only and adding Codex in iteration 4 actually be safer? What does the experience of `rulesync` and `ai-rules-sync` suggest — do users really run multiple tools, or do most pick one?

C4. **Is git the right substrate**, or would a content-addressed approach (IPFS-style, or just per-skill hashes) handle the "selective adoption" problem more naturally?

C5. **Are MCP servers really the dependency unit we should bundle**, or is the more common dependency a slash command, an agent, or a tool definition? What's the actual distribution in real-world skills?

### D. Scope and sequencing

D1. Given a 4-person team and a 6-iteration plan: which iteration is most likely to under-deliver value, and which is most likely to be the breakthrough that justifies the whole tool?

D2. Should any stretch goal be **promoted into v1** because skipping it makes the rest of the tool less useful? Specifically `--from-transcript` — does the lack of a generation flow undermine the sharing flow?

D3. What's the best sequence for the first three iterations if we wanted to **prove or disprove the riskiest assumption fastest**? (Our current sequence prioritizes incremental utility; the alternative would prioritize de-risking the merge model.)

D4. What's a realistic adoption story for a 4-person team? At what point would they likely abandon this in favor of "just commit AGENTS.md to git and deal with the merge pain"?

### E. Existence checks (please confirm or refute)

For each, say "exists / partially exists / does not exist that I can find" and cite:

- A standalone CLI that converts a Claude Code or Codex chat transcript into a SKILL.md or equivalent.
- An LLM-backed three-way merge driver registered via `.gitattributes` for markdown files.
- A tool that materializes a "base + overlay" composition for AGENTS.md or SKILL.md files.
- A cross-marketplace install resolver / lockfile spanning Claude plugins + Cursor + Continue + raw GitHub.
- An organization that has publicly described running an internal "skill marketplace" in production (not a curation list).

### F. Genuinely novel?

Of the four claims under "Where we believe the tool earns its keep" above, mark each as: **novel / partially novel / already done well by [X]**. For anything not novel, point us at the prior work so we can either build on it or reconsider scope.

### G. Concrete suggestions

Give us:

- Up to 5 **specific** changes to the iteration plan (move X earlier, drop Y, replace Z with W). For each, the evidence behind the suggestion.
- Up to 3 **risks** we don't seem to have noticed.
- Up to 3 **opportunities** we haven't articulated (e.g., a partnership, a missing primitive that would unlock a step, an adjacent user we should design for).

---

## Output format

Structure your reply as:

1. **Executive summary** (≤ 200 words). Top 3 things we should change, top 3 things we got right, biggest blind spot.
2. **Findings by question** (A1, A2, …). Bullet-form. Cite sources inline. Indicate confidence (high / medium / low).
3. **Suggested revised iteration plan** (table form, same shape as ours).
4. **Reading list** (10–20 sources, grouped by theme, with one-line annotations).

Length: aim for 3,000–5,000 words. Prefer fewer, deeper findings over broad surface coverage. If a question can't be answered from public sources, say so plainly and move on.
