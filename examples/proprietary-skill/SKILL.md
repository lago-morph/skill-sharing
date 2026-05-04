---
name: internal-code-review
description: Apply our team's internal code-review checklist to a pull request.
visibility: proprietary
version: 0.1.0
when_to_use: |
  When the user asks for a code review on a PR that targets our internal
  monorepo. Not suitable for open-source or third-party repositories.
user-invocable: true
allowed-tools:
  - Bash
  - Read
depends_on:
  - mcp: github
---

## Purpose

Run through our team's internal review checklist — covering security,
observability, and data-layer conventions that are specific to this codebase —
and produce a structured review comment ready to post on the PR.

## When to use

Use this skill when:

- A teammate asks "can you review PR #NNN?"
- You are preparing a self-review before requesting teammates.
- The diff touches our internal services (auth, billing, data pipeline).

Do **not** use for open-source contributions where our proprietary conventions
don't apply.

## Procedure <!-- id: proc -->

1. Fetch the PR diff: `gh pr diff <number>`.
2. Work through each checklist item below; note findings per item.
3. Group findings by severity: **blocker**, **suggestion**, **nit**.
4. Draft a single review comment in our standard template (see Examples).
5. Present the draft to the user; do not post until they approve.

### Checklist

- [ ] **Auth**: every new endpoint calls `require_auth()` or is explicitly
      marked `@public`.
- [ ] **Input validation**: external inputs validated at the boundary, not
      deep in the call stack.
- [ ] **Logging**: new code paths emit a structured log entry at entry and
      exit for flows > 50 ms.
- [ ] **Metrics**: new code paths increment a Prometheus counter with the
      standard label set (`service`, `env`, `version`).
- [ ] **Database**: no N+1 queries; any new query has a covering index or
      a documented reason it doesn't need one.
- [ ] **Error handling**: errors are wrapped with `fmt.Errorf("…: %w", err)`;
      no bare `panic` outside of `main`.
- [ ] **Tests**: new logic has unit tests; happy path + at least one error
      path covered.
- [ ] **Migration safety**: schema migrations are backward-compatible with
      the previous deploy (no destructive column drops in the same PR).

## Examples

```markdown
## Review — PR #123

**Blockers**
- `UserService.create` calls the DB directly without `require_auth()`. Add
  the guard or mark it `@internal_only`.

**Suggestions**
- The new `/report` endpoint has no Prometheus counter. Add one before ship.

**Nits**
- Line 47: variable name `tmp` doesn't convey intent; `pendingRecords` would
  be clearer.
```

## References

- Internal wiki: `go/code-review-guide` (requires VPN)
- `docs/observability.md` in this repo
- `docs/database-conventions.md` in this repo

## Anti-patterns

- Do not post the review without user approval — this is a draft aid.
- Do not apply open-source conventions (e.g. Apache license headers) — those
  don't apply here.
- Do not mark migration PRs as approved if the migration drops a column used
  by the current production binary.
