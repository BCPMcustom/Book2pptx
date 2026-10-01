"""Markdown parsing for book2pptx.

Converts a Markdown document into a ``PresentationSpec``

!!! VERSION 1.0 code -> refactored by Claude from Ben's code !!!


Supported syntax
----------------
``# Text``        First occurrence sets the presentation title; any later
                  occurrence sets the closing slide title.
``## Text``       Starts a new slide.
``- Text``        Adds a bullet to the current slide.
``![alt](path)``  Adds an image to the current slide. Relative paths are
                  resolved against the directory of the Markdown file.
``#### Text``     Adds a callout to the current slide.
``### Text``      Opens an ignored region. Content, including HTML tables, is
                  skipped until the next ``#``, ``##``, or ``####`` line, or
                  until another ``###`` line, which closes the region and is
                  itself skipped. Wrap unwanted tables in a pair of ``###``
                  lines to avoid rendering them.
``<table>``       HTML tables are rendered to PNG and attached to the current
                  slide as images.
"""

from __future__ import annotations

import logging
import re
from html.parser import HTMLParser
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Headless backend: no display or GUI toolkit required.
import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)

from parser.models.presentation_spec import PresentationSpec, SlideSpec  # noqa: E402

logger = logging.getLogger(__name__)

# Maximum characters per cell used when estimating column widths.
HEADER_LIMIT = 20
CELL_LIMIT = 40

IMAGE_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")

# Heading prefixes that end an ignored region and are then parsed normally.
# A '### ' line also ends the region, but it is consumed rather than parsed.
IGNORE_TERMINATORS = ("# ", "## ", "#### ")

DEFAULT_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class TableParser(HTMLParser):
    """Extract the text content of an HTML table as a list of rows."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell: list[str] = []
        self._in_cell = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ("th", "td"):
            self._in_cell = True
            self._current_cell = []
        elif tag == "tr":
            self._current_row = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("th", "td"):
            self._current_row.append("".join(self._current_cell).strip())
            self._in_cell = False
        elif tag == "tr" and self._current_row:
            self.rows.append(self._current_row)


class HTMLTableRenderer:
    """Render an HTML table to a PNG image with Matplotlib.

    The first row is treated as the header. Images are written to
    ``output_dir`` as ``table_<n>.png``.
    """

    def __init__(self, output_dir: Path | str) -> None:
        self.output_dir = Path(output_dir)
        self.table_count = 0

    def render(self, html_table: str) -> Path | None:
        """Render ``html_table`` and return the PNG path, or None if it has no cells."""
        parser = TableParser()
        parser.feed(html_table)
        rows = self._pad_rows(parser.rows)
        if not rows:
            logger.warning("Skipping HTML table that contains no cells.")
            return None

        header, data = rows[0], rows[1:]
        column_widths = self._column_widths(header, data)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"table_{self.table_count}.png"
        self.table_count += 1

        fig, ax = plt.subplots()
        try:
            ax.axis("off")
            table = ax.table(
                cellText=data or [[""] * len(header)],
                colLabels=header,
                loc="center",
                colWidths=column_widths,
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.2)
            fig.savefig(output_path, bbox_inches="tight", dpi=200)
        finally:
            plt.close(fig)

        return output_path

    @staticmethod
    def _pad_rows(rows: list[list[str]]) -> list[list[str]]:
        """Pad ragged rows with empty cells so every row has the same length."""
        if not rows:
            return []
        num_columns = max(len(row) for row in rows)
        return [row + [""] * (num_columns - len(row)) for row in rows]

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        return text if len(text) <= limit else text[: limit - 3] + "..."

    @classmethod
    def _column_widths(cls, header: list[str], data: list[list[str]]) -> list[float]:
        """Estimate relative column widths from the longest cell in each column.

        Cells are truncated to HEADER_LIMIT / CELL_LIMIT before measuring.
        Matplotlib's table() does not account for header width when it computes
        the rendered table geometry, so when a header is wider than the data in
        its column the normalizing total is reduced to compensate.
        """
        display_rows = [[cls._truncate(c, HEADER_LIMIT) for c in header]]
        display_rows += [[cls._truncate(c, CELL_LIMIT) for c in row] for row in data]

        widths: list[int] = []
        adjustment = 0.0
        for col in range(len(header)):
            widths.append(max(len(row[col]) for row in display_rows))

            header_length = len(header[col])
            data_length = max((len(row[col]) for row in data), default=0)
            if data_length and header_length > data_length:
                adjustment -= header_length / data_length

        total = sum(widths) + adjustment
        if total <= 0:
            return [1 / len(widths)] * len(widths)  # Degenerate input: equal widths.
        return [width / total for width in widths]


class MarkdownParser:
    """Parse a Markdown file into a ``PresentationSpec``."""

    def __init__(self, assets_dir: Path | str | None = None) -> None:
        self.assets_dir = Path(assets_dir) if assets_dir else DEFAULT_ASSETS_DIR
        self.table_renderer = HTMLTableRenderer(self.assets_dir)
        self.base_dir = Path()
        self._reset()

    def _reset(self) -> None:
        """Clear per-document state so a parser instance can be reused."""
        self.presentation_title = ""
        self.closing_title = ""
        self.slides: list[SlideSpec] = []
        self.current_slide: SlideSpec | None = None

    def parse_heading(self, line: str) -> None:
        if line.startswith("# "):
            text = line[2:].strip()
            if not self.presentation_title:
                self.presentation_title = text
            else:
                self.closing_title = text
        elif line.startswith("## "):
            title = line[3:].strip()
            logger.info("NEW SLIDE: %s", title)
            self.current_slide = SlideSpec(title)
            self.slides.append(self.current_slide)

    def parse_ignore(self, line: str, in_ignore: bool) -> bool:
        """Return True when a ``###`` line opens an ignored region."""
        return in_ignore or line.startswith("### ")

    def parse_bullet(self, line: str) -> None:
        if line.startswith("- ") and self.current_slide:
            self.current_slide.bullets.append(line[2:].strip())

    def parse_image(self, line: str) -> None:
        match = IMAGE_RE.search(line)
        if match:
            self.add_image(match.group(2))

    def add_image(self, image_path: Path | str) -> None:
        """Attach an image to the current slide as an absolute path."""
        if self.current_slide is None:
            logger.warning("Image found before the first slide was ignored: %s", image_path)
            return
        self.current_slide.images.append(str((self.base_dir / image_path).resolve()))

    def parse_callouts(self, line: str) -> None:
        if not line.startswith("#### "):
            return
        if self.current_slide is None:
            logger.warning("Callout found before the first slide was ignored: %s", line)
            return
        self.current_slide.callouts.append(line[5:].strip())

    def _flush_table(self, table_lines: list[str]) -> None:
        image_path = self.table_renderer.render("\n".join(table_lines))
        if image_path is not None:
            self.add_image(image_path)

    def parse(self, filename: Path | str) -> PresentationSpec:
        path = Path(filename)
        self.base_dir = path.parent
        self._reset()

        table_lines: list[str] = []
        in_table = False
        in_ignore = False

        with path.open(encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue

                if in_ignore:
                    if line.startswith(IGNORE_TERMINATORS):
                        in_ignore = False  # Resume normal parsing of this line.
                    elif line.startswith("### "):
                        in_ignore = False  # Closing marker: consume it and resume.
                        continue
                    else:
                        continue

                # Table markup may span many lines or sit on a single line.
                if in_table or "<table" in line:
                    in_table = True
                    table_lines.append(line)
                    if "</table>" in line:
                        self._flush_table(table_lines)
                        table_lines = []
                        in_table = False
                    continue

                self.parse_heading(line)
                self.parse_bullet(line)
                self.parse_image(line)
                self.parse_callouts(line)
                in_ignore = self.parse_ignore(line, in_ignore)

        return PresentationSpec(
            title=self.presentation_title,
            slides=self.slides,
            closing_title=self.closing_title,
        )
