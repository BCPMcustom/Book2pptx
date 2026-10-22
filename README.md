# Book2pptx

Converts a Markdown export of a notebook into a PowerPoint (`.pptx`) deck.

> **Status:** V1.0 (work in progress).

## Requirements

- Python 3.10 or newer
- [python-pptx](https://python-pptx.readthedocs.io/)
- [matplotlib](https://matplotlib.org/) (renders HTML tables as images)

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 book2pptx.py MintClassics.zip
```

The input is a `.zip` archive containing one Markdown file plus any images it references. The deck is saved next to the archive with a `.pptx` extension.

| Option | Description |
| --- | --- |
| `-t`, `--template` | Render with `renderer/templates/Template.pptx` |
| `-o`, `--output` | Output `.pptx` path (default: archive name with a `.pptx` suffix) |
| `-v`, `--verbose` | Enable debug logging |

A relative archive name is looked for in the current folder first, then in the project folder, so the program can be launched from any directory:

```bash
python3 ~/Book2pptx/book2pptx.py MintClassics.zip
```

## Markdown syntax

| Syntax | Result |
| --- | --- |
| `# Text` | First occurrence sets the presentation title; any later one sets the closing slide title |
| `## Text` | Starts a new slide |
| `- Text` | Adds a bullet to the current slide |
| `![alt](path)` | Adds an image to the current slide (path relative to the Markdown file) |
| `#### Text` | Adds a callout to the current slide; each further callout in the same section gets its own slide with the same title |
| `<table>...</table>` | Rendered to a PNG and added to the current slide |
| `### Text` | Opens an ignored region (see below) |

### Skipping content

A `### ` line opens an ignored region. Everything after it, including HTML tables, is skipped until the next `#`, `##`, or `####` line, or until another `### ` line, which closes the region and is itself skipped.

To keep a table out of the deck, wrap it in a pair of `###` lines:

```markdown
### skip
<table>...</table>
### end skip
```

Skipped tables are not rendered, which also shortens run time.

## Project layout

```
book2pptx.py                      Command-line entry point
parser/markdown_parser.py         Markdown parsing and table rendering
parser/models/presentation_spec.py  Slide and presentation data classes
renderer/pptx_renderer.py         PowerPoint rendering
renderer/templates/Template.pptx  Template used with --template
```

## Known limitations

- A callout and bullets in the same section are placed in the same area of the slide and can overlap.
- Font sizes are fixed (title 42 pt, body 22 pt); long text is not yet shrunk to fit.

