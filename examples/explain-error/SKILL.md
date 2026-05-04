---
name: explain-error
description: Diagnose a runtime error and suggest a fix without guessing.
---

## Purpose

Turn a raw error message + stack trace into a clear explanation of what
went wrong, why it went wrong, and what the most likely fix is — without
making changes until the diagnosis is confirmed.

## When to use

Use this skill when:

- The user pastes an error message and asks "what does this mean?"
- A test is failing and the output isn't self-explanatory.
- A build or type-check step is producing errors across multiple files.

## Procedure

1. Read the full error message and stack trace before saying anything.
2. Identify the **root cause** — the first failure in the call stack, not
   a downstream symptom.
3. Explain in plain language what the error means and why it happened.
4. Propose the most likely fix as a hypothesis: "I think the issue is X;
   here is how I would fix it."
5. Wait for the user to confirm before applying any changes.
6. If the error could have multiple causes, list them in order of
   likelihood and ask which matches the user's situation.

## Anti-patterns

- Do not immediately edit files to "try something" — diagnose first.
- Do not suggest adding `try/catch` to silence an error without
  understanding what caused it.
- Do not guess at missing context; ask for the relevant file or log.
