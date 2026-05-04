"""Path registry: one entry per supported host (Claude Code, Codex, …)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class HostEntry:
    name: str      # e.g. "claude-code"
    scope: str     # "user" | "project" | "plugin"
    path: Path


def claude_code_paths(cwd: Path | None = None) -> list[HostEntry]:
    """Return the three canonical Claude Code skill locations."""
    home = Path.home()
    entries = [
        HostEntry("claude-code", "user", home / ".claude" / "skills"),
        HostEntry("claude-code", "user", home / ".claude" / "commands"),
    ]
    project_root = cwd or Path.cwd()
    entries.append(HostEntry("claude-code", "project", project_root / ".claude" / "skills"))
    return entries


def codex_paths(cwd: Path | None = None) -> list[HostEntry]:
    """Walk cwd and parents for AGENTS.md; also check ~/.codex/."""
    home = Path.home()
    start = cwd or Path.cwd()
    entries: list[HostEntry] = []

    for parent in [start, *start.parents]:
        candidate = parent / "AGENTS.md"
        if candidate.exists():
            entries.append(HostEntry("codex", "project", candidate))

    codex_home = home / ".codex"
    if (codex_home / "AGENTS.md").exists():
        entries.append(HostEntry("codex", "user", codex_home / "AGENTS.md"))

    return entries


def all_host_entries(cwd: Path | None = None) -> list[HostEntry]:
    return claude_code_paths(cwd) + codex_paths(cwd)
