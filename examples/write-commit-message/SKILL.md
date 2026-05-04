---
name: write-commit-message
description: Craft a clear, conventional commit message from staged changes.
---

## Purpose

Generate a commit message that follows the Conventional Commits spec and
accurately reflects what the staged diff actually changes.

## When to use

Reach for this skill whenever:

- The user runs `git commit` without `-m` and wants a drafted message.
- The user has a vague message like "fix stuff" and wants it improved.
- You are about to create a commit yourself and need a message template.

## Procedure

1. Run `git diff --staged` to read the staged changes in full.
2. Identify the primary type: `feat`, `fix`, `docs`, `style`, `refactor`,
   `perf`, `test`, `chore`.
3. Identify the scope (optional): the module or component most affected.
4. Write a subject line in the imperative mood, ≤ 72 characters:
   `<type>(<scope>): <short summary>`
5. If the diff needs explanation, add a body (blank line after subject)
   describing *why* the change was made, not what — the diff shows what.
6. If the commit closes an issue, append a `Closes #NNN` trailer.
7. Present the message to the user for approval before running `git commit -m`.

## Examples

```
feat(substrate): wrap rulesync behind src/substrate.ts

Isolates the rulesync dependency so swapping the substrate later only
touches one file.
```

```
fix(hosts): include ~/.codex/skills in Codex user scope

The user-scoped skills directory was missing from the path registry,
causing skillctl list to miss globally-installed skills.
```

## Anti-patterns

- Do not summarize the ticket title verbatim — describe what the code does.
- Do not use past tense ("Fixed bug") — use imperative ("Fix bug").
- Do not exceed 72 characters on the subject line.
