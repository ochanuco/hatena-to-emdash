from __future__ import annotations

import hashlib
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from .models import MigrationReport


MARKDOWN_IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()(?P<url>https?://[^)]+)(\))")
HTML_IMAGE_RE = re.compile(r'(?P<prefix><img\b[^>]*\bsrc=["\'])(?P<url>https?://[^"\']+)(?P<suffix>["\'][^>]*>)')


def migrate_images(
    markdown: str,
    asset_dir: Path,
    dry_run: bool,
    report: MigrationReport,
) -> tuple[str, int]:
    replacements: dict[str, str] = {}
    urls = extract_image_urls(markdown)

    for index, url in enumerate(urls, start=1):
        relative_path = f"{asset_dir.name}/{build_image_name(url, index)}"
        replacements[url] = relative_path
        if dry_run:
            report.skipped_images += 1
            continue

        destination = asset_dir / build_image_name(url, index)
        try:
            download_image(url, destination)
            report.downloaded_images += 1
        except Exception as exc:  # noqa: BLE001
            report.failed_images.append({"url": url, "error": str(exc)})

    rewritten = markdown
    for url, relative_path in replacements.items():
        rewritten = rewritten.replace(url, relative_path)
    return rewritten, len(urls)


def extract_image_urls(markdown: str) -> list[str]:
    urls = [match.group("url") for match in MARKDOWN_IMAGE_RE.finditer(markdown)]
    urls.extend(match.group("url") for match in HTML_IMAGE_RE.finditer(markdown))
    return list(dict.fromkeys(urls))


def build_image_name(url: str, index: int) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if not suffix:
        suffix = mimetypes.guess_extension("image/jpeg") or ".jpg"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    return f"{index:02d}-{digest}{suffix}"


def download_image(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url) as response:  # noqa: S310
        data = response.read()
    destination.write_bytes(data)
