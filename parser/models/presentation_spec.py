"""Data model for a parsed presentation.

!!! VERSION 1.0 code -> refactored by Claude from Ben's code !!!

The Markdown parser produces these objects and the PowerPoint renderer
consumes them, so neither side needs to know about the other.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class SlideSpec:
    """Content of a single slide."""

    title: str
    bullets: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)  # Absolute file paths.
    callouts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PresentationSpec:
    """Content of a whole deck: opening title, content slides, closing title."""

    title: str
    slides: list[SlideSpec] = field(default_factory=list)
    closing_title: str = ""
