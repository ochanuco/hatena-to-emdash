from __future__ import annotations

import re
import unicodedata
from datetime import datetime

from .models import ConvertedPost, Entry


def convert_entry(entry: Entry) -> ConvertedPost:
    title = first_meta(entry, "TITLE", "untitled")
    date_text = first_meta(entry, "DATE", "1970-01-01 00:00:00")
    parsed_date = parse_mt_date(date_text)
    slug = slugify(title) or parsed_date.strftime("%Y%m%d-%H%M%S")
    post_dir = parsed_date.strftime("posts/%Y/%m")
    asset_dir = parsed_date.strftime(f"assets/%Y/%m/{slug}")
    output_path = f"{post_dir}/{slug}.md"
    body = build_body(entry)
    markdown = build_markdown(entry, title, parsed_date, slug, asset_dir, body)
    return ConvertedPost(
        slug=slug,
        output_path=output_path,
        asset_dir=asset_dir,
        markdown=markdown,
    )


def build_body(entry: Entry) -> str:
    parts = [entry.sections.get("BODY", "").strip()]
    extended = entry.sections.get("EXTENDED BODY", "").strip()
    excerpt = entry.sections.get("EXCERPT", "").strip()
    if excerpt:
        parts.append("\n<!-- excerpt -->\n")
        parts.append(excerpt)
    if extended:
        parts.append("\n<!-- more -->\n")
        parts.append(extended)
    return "\n\n".join(part for part in parts if part).strip()


def build_markdown(
    entry: Entry,
    title: str,
    parsed_date: datetime,
    slug: str,
    asset_dir: str,
    body: str,
) -> str:
    categories = meta_list(entry, "CATEGORY")
    tags = split_tags(first_meta(entry, "TAGS", ""))
    status = normalize_status(first_meta(entry, "STATUS", "Publish"))
    frontmatter_lines = [
        "---",
        f'title: "{escape_yaml(title)}"',
        f"date: {parsed_date.isoformat()}",
        f'slug: "{slug}"',
        f'status: "{status}"',
        f"categories: {format_yaml_list(categories)}",
        f"tags: {format_yaml_list(tags)}",
        f'assets_dir: "{asset_dir}"',
        "---",
        "",
    ]
    return "\n".join(frontmatter_lines) + body + "\n"


def first_meta(entry: Entry, key: str, default: str = "") -> str:
    return entry.metadata.get(key, [default])[0]


def meta_list(entry: Entry, key: str) -> list[str]:
    return [item for item in entry.metadata.get(key, []) if item]


def split_tags(raw: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,，]", raw) if part.strip()]


def parse_mt_date(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%m/%d/%Y %H:%M:%S")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def normalize_status(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"publish", "published"}:
        return "published"
    if lowered in {"draft", "hold"}:
        return "draft"
    return lowered or "published"


def format_yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    escaped = [f'"{escape_yaml(value)}"' for value in values]
    return "[" + ", ".join(escaped) + "]"


def escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
