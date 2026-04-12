from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import convert_entry
from .image_migrator import migrate_images
from .models import MigrationReport
from .mt_parser import parse_mt_export
from .report import write_report

DEFAULT_INPUT_DIR = Path(".local/input")
DEFAULT_INPUT_PATTERN = "*.export.txt"
DEFAULT_OUTPUT_DIR = Path(".local/output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hatena-to-emdash")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate = subparsers.add_parser("migrate")
    migrate.add_argument("--input", help="Path to the MT export file")
    migrate.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output root directory",
    )
    migrate.add_argument(
        "--report-path",
        default="migration-report.json",
        help="Relative path to the JSON report under output-dir",
    )
    migrate.add_argument("--dry-run", action="store_true")
    migrate.add_argument("--limit", type=int, default=0)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "migrate":
        return run_migrate(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


def run_migrate(args: argparse.Namespace) -> int:
    input_path = resolve_input_path(args.input)
    if input_path is None:
        return 2
    output_dir = Path(args.output_dir)
    report = MigrationReport()
    entries = parse_mt_export(input_path.read_text(encoding="utf-8"))
    if args.limit:
        entries = entries[: args.limit]
    report.total_entries = len(entries)

    for entry in entries:
        post = convert_entry(entry)
        asset_dir = output_dir / post.asset_dir
        markdown, image_count = migrate_images(
            post.markdown,
            asset_dir,
            dry_run=args.dry_run,
            report=report,
        )
        post.image_count = image_count
        if args.dry_run:
            continue
        output_path = output_dir / post.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        report.written_posts += 1

    write_report(report, output_dir / args.report_path, dry_run=args.dry_run)
    print_summary(report, dry_run=args.dry_run)
    return 0


def resolve_input_path(raw_input: str | None) -> Path | None:
    if raw_input:
        input_path = Path(raw_input)
        if not input_path.exists():
            print(f"input file not found: {input_path}", file=sys.stderr)
            return None
        if not input_path.is_file():
            print(f"input path is not a file: {input_path}", file=sys.stderr)
            return None
        return input_path

    candidates = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_INPUT_PATTERN))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        print(
            f"no input file found under {DEFAULT_INPUT_DIR} matching {DEFAULT_INPUT_PATTERN}\n"
            "Place your MT export there or pass --input explicitly.",
            file=sys.stderr,
        )
        return None

    print(
        f"multiple input files found under {DEFAULT_INPUT_DIR} matching {DEFAULT_INPUT_PATTERN}:",
        file=sys.stderr,
    )
    for candidate in candidates:
        print(f"- {candidate}", file=sys.stderr)
    print("Pass --input explicitly.", file=sys.stderr)
    return None


def print_summary(report: MigrationReport, dry_run: bool) -> None:
    mode = "dry-run" if dry_run else "write"
    print(
        f"[{mode}] entries={report.total_entries} "
        f"posts={report.written_posts} "
        f"downloaded_images={report.downloaded_images} "
        f"skipped_images={report.skipped_images} "
        f"failed_images={len(report.failed_images)}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
