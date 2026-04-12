from __future__ import annotations

from collections import defaultdict

from .models import Entry


SECTION_HEADERS = {
    "BODY",
    "EXTENDED BODY",
    "EXCERPT",
    "KEYWORDS",
}


def parse_mt_export(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for raw_entry in text.split("--------\n"):
        chunk = raw_entry.strip()
        if not chunk:
            continue
        entries.append(parse_entry(chunk))
    return entries


def parse_entry(chunk: str) -> Entry:
    metadata: dict[str, list[str]] = defaultdict(list)
    sections: dict[str, str] = {}
    current_section: str | None = None
    section_lines: list[str] = []

    for line in chunk.splitlines():
        if line == "-----":
            if current_section is not None:
                sections[current_section] = "\n".join(section_lines).strip()
                current_section = None
                section_lines = []
            continue

        if current_section is not None:
            section_lines.append(line)
            continue

        if line.endswith(":") and line[:-1] in SECTION_HEADERS:
            current_section = line[:-1]
            section_lines = []
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()].append(value.strip())

    if current_section is not None:
        sections[current_section] = "\n".join(section_lines).strip()

    return Entry(metadata=dict(metadata), sections=sections)
