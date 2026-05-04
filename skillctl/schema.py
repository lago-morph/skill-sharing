"""Frontmatter + section parsing for SKILL.md files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

KNOWN_SECTIONS = frozenset(
    {"Purpose", "When to use", "Procedure", "Examples", "References", "Anti-patterns"}
)
_SECTION_ID_RE = re.compile(r"<!--\s*id:\s*(\S+)\s*-->")
_H2_RE = re.compile(r"^## (.+)", re.MULTILINE)


@dataclass
class Section:
    heading: str
    body: str
    id: Optional[str] = None

    @property
    def is_known(self) -> bool:
        return self.heading in KNOWN_SECTIONS


@dataclass
class Skill:
    frontmatter: dict
    sections: list[Section]
    raw_body: str

    @property
    def name(self) -> str:
        return self.frontmatter.get("name", "")

    @property
    def visibility(self) -> str:
        return self.frontmatter.get("visibility", "public")

    def section(self, heading: str) -> Optional[Section]:
        for s in self.sections:
            if s.heading == heading:
                return s
        return None


def parse_skill(text: str) -> Skill:
    """Parse SKILL.md text into a Skill object."""
    fm: dict = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2].lstrip("\n")

    sections = _parse_sections(body)
    return Skill(frontmatter=fm, sections=sections, raw_body=body)


def parse_skill_file(path: Path) -> Skill:
    return parse_skill(path.read_text(encoding="utf-8"))


def _parse_sections(body: str) -> list[Section]:
    """Split body text into a list of Sections by H2 headings."""
    lines = body.splitlines(keepends=True)
    sections: list[Section] = []
    current_heading: Optional[str] = None
    current_id: Optional[str] = None
    current_lines: list[str] = []
    in_fence = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        m = _H2_RE.match(line)
        if m and not in_fence:
            if current_heading is not None:
                sections.append(
                    Section(
                        heading=current_heading,
                        id=current_id,
                        body="".join(current_lines).strip(),
                    )
                )
            heading_text = m.group(1)
            id_match = _SECTION_ID_RE.search(heading_text)
            if id_match:
                current_id = id_match.group(1)
                heading_text = _SECTION_ID_RE.sub("", heading_text).strip()
            else:
                current_id = None
            current_heading = heading_text
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections.append(
            Section(
                heading=current_heading,
                id=current_id,
                body="".join(current_lines).strip(),
            )
        )

    return sections


def dump_skill(skill: Skill) -> str:
    """Serialize a Skill back to SKILL.md text."""
    parts: list[str] = ["---\n", yaml.dump(skill.frontmatter, default_flow_style=False), "---\n"]
    for section in skill.sections:
        heading = section.heading
        if section.id:
            heading = f"{heading} <!-- id: {section.id} -->"
        parts.append(f"\n## {heading}\n\n")
        if section.body:
            parts.append(section.body + "\n")
    return "".join(parts)
