---
name: write-commit-message
description: Craft a clear, conventional commit message from staged changes.
visibility: public
version: 0.1.0
when_to_use: |
  When the user asks you to commit staged changes and hasn't supplied a message,
  or when they ask you to improve an existing draft commit message.
user-invocable: true
allowed-tools:
  - Bash
---

## Purpose

Generate a commit message that follows the Conventional Commits spec and
accurately reflects what the staged diff actually changes — not just what the
ticket says.

## When to use

Reach for this skill whenever:

- The user runs `git commit` without `-m` and wants Claude to draft the message.
- The user pastes a vague message like "fix stuff" and wants it improved.
- You are about to create a commit yourself and need a message template.

## Procedure <!-- id: proc -->

1. Run `git diff --staged` to read the staged changes in full.
2. Identify the primary *type* from the Conventional Commits set:
   `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
3. Identify the *scope* (optional): the module, package, or component most
   affected.
4. Write a **subject line** in the imperative mood, ≤ 72 characters:
   `<type>(<scope>): <short summary>`
5. If the diff needs explanation, add a **body** (blank line after subject)
   describing *why* the change was made, not *what* — the diff already shows
   what.
6. If the commit closes an issue, append a `Closes #NNN` trailer.
7. Present the message to the user for approval before running `git commit -m`.

## Examples

```
feat(schema): add section ID extraction from HTML comments

Stable IDs let `skillctl merge` track sections across reorders without
falling back to fuzzy heading matching, which broke when authors renamed
a section.

Closes #42
```

```
fix(hosts): include ~/.claude/commands in Claude Code paths

The commands directory was omitted from the initial scan, causing
`skillctl list` to miss user-level slash commands.
```

## References

- [Conventional Commits specification](https://www.conventionalcommits.org/)
- [Git commit message best practices](https://cbea.ms/git-commit/)

## Anti-patterns

- Do not summarize the ticket title verbatim — describe what the code does.
- Do not use past tense ("Fixed bug") — use imperative ("Fix bug").
- Do not exceed 72 characters on the subject line; terminals wrap it.
- Do not include `git add` in the procedure — only commit what the user
  already staged.
