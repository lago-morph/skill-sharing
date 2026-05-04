"""Tests for skillctl.schema — frontmatter + section parser."""

import textwrap

import pytest

from skillctl.schema import (
    Section,
    Skill,
    dump_skill,
    parse_skill,
)

MINIMAL_SKILL = textwrap.dedent("""\
    ---
    name: example-skill
    description: Does something useful.
    visibility: public
    version: 0.1.0
    ---

    ## Purpose

    A minimal skill used for testing.

    ## When to use

    Use this skill in tests.
    """)

FULL_SKILL = textwrap.dedent("""\
    ---
    name: full-skill
    description: A skill with all optional sections.
    visibility: proprietary
    version: 0.2.0
    allowed-tools:
      - Read
      - Edit
    ---

    ## Purpose

    Demonstrates every section type.

    ## When to use

    Whenever you need a complete example.

    ## Procedure <!-- id: proc -->

    1. Step one.
    2. Step two.

    ## Examples

    See `references/` for worked examples.

    ## References

    - agentskills.io specification

    ## Anti-patterns

    Do not skip step one.
    """)


class TestParseSkill:
    def test_parses_frontmatter(self):
        skill = parse_skill(MINIMAL_SKILL)
        assert skill.name == "example-skill"
        assert skill.visibility == "public"
        assert skill.frontmatter["version"] == "0.1.0"

    def test_required_sections_present(self):
        skill = parse_skill(MINIMAL_SKILL)
        headings = [s.heading for s in skill.sections]
        assert "Purpose" in headings
        assert "When to use" in headings

    def test_section_body_content(self):
        skill = parse_skill(MINIMAL_SKILL)
        purpose = skill.section("Purpose")
        assert purpose is not None
        assert "minimal skill" in purpose.body

    def test_section_count_minimal(self):
        skill = parse_skill(MINIMAL_SKILL)
        assert len(skill.sections) == 2

    def test_all_optional_sections_parsed(self):
        skill = parse_skill(FULL_SKILL)
        headings = {s.heading for s in skill.sections}
        assert headings == {
            "Purpose",
            "When to use",
            "Procedure",
            "Examples",
            "References",
            "Anti-patterns",
        }

    def test_section_id_extracted(self):
        skill = parse_skill(FULL_SKILL)
        proc = skill.section("Procedure")
        assert proc is not None
        assert proc.id == "proc"

    def test_section_id_not_in_heading(self):
        skill = parse_skill(FULL_SKILL)
        proc = skill.section("Procedure")
        assert "<!--" not in proc.heading

    def test_visibility_proprietary(self):
        skill = parse_skill(FULL_SKILL)
        assert skill.visibility == "proprietary"

    def test_no_frontmatter(self):
        text = "## Purpose\n\nSome purpose.\n"
        skill = parse_skill(text)
        assert skill.frontmatter == {}
        assert skill.name == ""
        assert skill.visibility == "public"
        assert len(skill.sections) == 1
        assert skill.sections[0].heading == "Purpose"

    def test_empty_frontmatter_block(self):
        text = "---\n---\n\n## Purpose\n\nHello.\n"
        skill = parse_skill(text)
        assert skill.frontmatter == {}

    def test_section_is_known(self):
        skill = parse_skill(MINIMAL_SKILL)
        assert all(s.is_known for s in skill.sections)

    def test_unknown_section_preserved(self):
        text = MINIMAL_SKILL + "\n## Custom Section\n\nCustom content.\n"
        skill = parse_skill(text)
        headings = [s.heading for s in skill.sections]
        assert "Custom Section" in headings
        custom = skill.section("Custom Section")
        assert not custom.is_known

    def test_sections_without_id_have_none(self):
        skill = parse_skill(MINIMAL_SKILL)
        for s in skill.sections:
            assert s.id is None


class TestDumpSkill:
    def test_roundtrip_minimal(self):
        skill = parse_skill(MINIMAL_SKILL)
        dumped = dump_skill(skill)
        reparsed = parse_skill(dumped)
        assert reparsed.name == skill.name
        assert reparsed.visibility == skill.visibility
        assert {s.heading for s in reparsed.sections} == {s.heading for s in skill.sections}

    def test_roundtrip_preserves_section_id(self):
        skill = parse_skill(FULL_SKILL)
        dumped = dump_skill(skill)
        reparsed = parse_skill(dumped)
        proc = reparsed.section("Procedure")
        assert proc is not None
        assert proc.id == "proc"

    def test_dump_contains_frontmatter_delimiter(self):
        skill = parse_skill(MINIMAL_SKILL)
        dumped = dump_skill(skill)
        assert dumped.startswith("---\n")
        assert "---\n" in dumped[4:]

    def test_dump_contains_h2_headings(self):
        skill = parse_skill(MINIMAL_SKILL)
        dumped = dump_skill(skill)
        assert "## Purpose" in dumped
        assert "## When to use" in dumped
