"""Minimal YAML frontmatter reader for SKILL.md and plugin manifests.

No third-party dependency: PyYAML is not always available and the subset used
by skill frontmatter is small. Supports the shapes that appear in practice:

    name: slide-creator
    description: >
      Folded block scalar.
    description: |
      Literal block scalar.
    description: "quoted scalar"
    metadata:
      version: 0.1.0

Unknown nested structures are returned as a nested dict of raw strings.
"""

from __future__ import annotations

import re

_SCALARS = (">", "|", ">-", "|-", ">+", "|+")


def parse(text: str) -> dict:
    """Parse the YAML frontmatter of a document. Returns {} when absent."""
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    return _parse_block(lines[1:end])


def _parse_block(lines: list[str]) -> dict:
    result: dict = {}
    index = 0
    while index < len(lines):
        raw = lines[index]
        index += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):
            continue  # continuation of a value already consumed
        match = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in _SCALARS:
            folded = value[0] == ">"
            block, index = _read_block(lines, index)
            result[key] = _join(block, folded)
        elif value == "":
            nested, index = _read_nested(lines, index)
            result[key] = nested
        else:
            result[key] = _unquote(value)
    return result


def _read_block(lines: list[str], index: int) -> tuple[list[str], int]:
    block: list[str] = []
    while index < len(lines):
        line = lines[index]
        if line.strip() and line[:1] not in (" ", "\t"):
            break
        block.append(line.strip())
        index += 1
    return block, index


def _read_nested(lines: list[str], index: int) -> tuple[dict, int]:
    nested: dict = {}
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line[:1] not in (" ", "\t"):
            break
        match = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*)$", line)
        if match:
            nested[match.group(1)] = _unquote(match.group(2).strip())
        index += 1
    return nested, index


def _join(block: list[str], folded: bool) -> str:
    parts = [line for line in block if line]
    if not parts:
        return ""
    if folded:
        return " ".join(parts)
    return "\n".join(parts)


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def read(path) -> dict:
    """Parse the frontmatter of a file. Returns {} on any failure."""
    try:
        with open(path, encoding="utf-8") as handle:
            return parse(handle.read())
    except OSError:
        return {}
