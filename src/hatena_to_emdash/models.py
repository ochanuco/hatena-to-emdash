from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Entry:
    metadata: dict[str, list[str]]
    sections: dict[str, str]


@dataclass(slots=True)
class ConvertedPost:
    slug: str
    output_path: str
    asset_dir: str
    markdown: str
    image_count: int = 0


@dataclass(slots=True)
class MigrationReport:
    total_entries: int = 0
    written_posts: int = 0
    downloaded_images: int = 0
    skipped_images: int = 0
    failed_images: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
