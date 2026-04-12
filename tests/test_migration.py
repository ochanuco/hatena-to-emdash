from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from hatena_to_emdash.cli import run_migrate
from hatena_to_emdash.converter import convert_entry
from hatena_to_emdash.image_migrator import extract_image_urls
from hatena_to_emdash.mt_parser import parse_mt_export


SAMPLE_MT = textwrap.dedent(
    """\
    AUTHOR: user
    TITLE: Hello World
    STATUS: Publish
    CATEGORY: Tech
    CATEGORY: Blog
    DATE: 04/12/2026 09:30:00
    TAGS: python, migration
    -----
    BODY:
    Paragraph

    ![alt](https://example.com/image.png)
    -----
    EXTENDED BODY:
    More body
    -----
    --------
    """
)


class MigrationTests(unittest.TestCase):
    def test_parse_mt_export(self) -> None:
        entries = parse_mt_export(SAMPLE_MT)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].metadata["TITLE"][0], "Hello World")
        self.assertIn("BODY", entries[0].sections)

    def test_convert_entry(self) -> None:
        entry = parse_mt_export(SAMPLE_MT)[0]
        converted = convert_entry(entry)
        self.assertIn('title: "Hello World"', converted.markdown)
        self.assertIn('categories: ["Tech", "Blog"]', converted.markdown)
        self.assertEqual(converted.output_path, "posts/2026/04/hello-world.md")

    def test_extract_image_urls(self) -> None:
        urls = extract_image_urls("![x](https://example.com/a.jpg)<img src=\"https://example.com/b.png\">")
        self.assertEqual(urls, ["https://example.com/a.jpg", "https://example.com/b.png"])

    def test_run_migrate_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "export.txt"
            output_dir = Path(tmpdir) / "out"
            input_path.write_text(SAMPLE_MT, encoding="utf-8")
            args = type(
                "Args",
                (),
                {
                    "input": str(input_path),
                    "output_dir": str(output_dir),
                    "report_path": "migration-report.json",
                    "dry_run": True,
                    "limit": 0,
                    "command": "migrate",
                },
            )
            exit_code = run_migrate(args)
            self.assertEqual(exit_code, 0)
            self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
