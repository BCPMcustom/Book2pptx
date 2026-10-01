# presentation_spec.py

from dataclasses import dataclass, field


@dataclass
class SlideSpec:
    title: str
    bullets: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    callouts: list[str] = field(default_factory=list)


@dataclass
class PresentationSpec:
    title: str
    slides: list[SlideSpec] = field(default_factory=list)
    closing_title: str = ""
