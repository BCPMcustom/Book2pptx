#!/usr/bin/env python3
"""book2pptx: convert a zipped Markdown export into a PowerPoint deck.

!!! VERSION 1.0 code -> refactored by Claude from Ben's code !!!

The input archive must contain a Markdown file and any images it references.
The archive is extracted into a temporary directory, parsed into a presentation
spec, rendered to a deck, and saved next to the archive with a .pptx extension
(or at the path given with --output). The temporary directory is removed on exit,
including when an error occurs.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import tempfile
import zipfile
from pathlib import Path

from parser.markdown_parser import MarkdownParser
from renderer.pptx_renderer import PowerPointRenderer

logger = logging.getLogger("book2pptx")

# Project directory (the folder containing this script), independent of the
# directory the program is launched from.
BASE_DIR = Path(__file__).resolve().parent


class BookToPptxError(Exception):
    """A user-correctable failure, such as a missing or invalid input archive."""


def resolve_archive(archive: Path) -> Path:
    """Locate the input archive.

    Absolute paths are used as given. Relative paths are tried against the
    current directory first, then against the project directory, so the program
    can be launched from any folder.
    """
    archive = archive.expanduser()
    candidates = [archive] if archive.is_absolute() else [Path.cwd() / archive, BASE_DIR / archive]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise BookToPptxError(
        f"Could not find '{archive}' in the current directory or in '{BASE_DIR}'."
    )


def extract_archive(archive: Path, destination: Path) -> None:
    """Extract ``archive`` into ``destination``."""
    try:
        with zipfile.ZipFile(archive) as zip_file:
            zip_file.extractall(destination)
    except FileNotFoundError:
        raise BookToPptxError(f"Could not find the archive at '{archive}'.") from None
    except zipfile.BadZipFile:
        raise BookToPptxError(f"'{archive}' is not a valid zip archive.") from None


def find_markdown(directory: Path) -> Path:
    """Return the Markdown file to convert, preferring the shallowest match."""
    matches = sorted(directory.rglob("*.md"), key=lambda p: (len(p.parts), str(p)))
    if not matches:
        raise BookToPptxError("No .md file found inside the archive.")
    if len(matches) > 1:
        logger.warning(
            "Archive contains %d Markdown files; using '%s'.",
            len(matches),
            matches[0].relative_to(directory),
        )
    return matches[0]


def convert(archive: Path, output: Path) -> None:
    """Convert ``archive`` to a PowerPoint deck saved at ``output``."""
    with tempfile.TemporaryDirectory(prefix="book2pptx_") as scratch:
        workdir = Path(scratch)

        logger.info("Extracting %s", archive)
        extract_archive(archive, workdir)

        markdown_path = find_markdown(workdir)
        logger.info("Processing %s", markdown_path.name)

        # Table images are written into the working directory alongside the
        # extracted assets and are removed with it.
        presentation = MarkdownParser(assets_dir=workdir).parse(markdown_path)
        deck = PowerPointRenderer().render(presentation)
        deck.save(str(output))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="book2pptx",
        description="Convert a zipped Markdown export into a PowerPoint deck.",
    )
    arg_parser.add_argument(
        "archive",
        type=Path,
        help="path to a .zip archive containing a Markdown file and its images; "
        "relative paths are also searched for in the project folder",
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output .pptx path (default: the archive name with a .pptx suffix)",
    )
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug logging"
    )
    return arg_parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    try:
        archive = resolve_archive(args.archive)
        # Resolve the output path against the launch directory before changing it.
        output = (args.output.expanduser() if args.output else archive.with_suffix(".pptx")).resolve()

        # Anchor the working directory to the project folder so any relative
        # resource paths used by the renderer behave the same from every launch
        # directory. All paths used below are absolute.
        os.chdir(BASE_DIR)

        convert(archive, output)
    except BookToPptxError as exc:
        logger.error("Error: %s", exc)
        return 1
    except Exception:
        logger.exception("Unexpected error during conversion.")
        return 1

    logger.info("Saved %s", output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
