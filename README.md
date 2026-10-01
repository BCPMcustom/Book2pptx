# Book2pptx

Converts a Markdown export of a notebook into a PowerPoint (`.pptx`) deck.

> **Status:** V0.1 (work in progress). The renderer is still being reworked; see [Known limitations](#known-limitations).

## Requirements

- Python 3.9 or newer
- [python-pptx](https://python-pptx.readthedocs.io/)
- [matplotlib](https://matplotlib.org/) (used to render HTML tables as images)

```bash
pip install python-pptx matplotlib
```

## Usage

```bash
python book2pptx.py MintClassics.zip
```

The input is a `.zip` archive containing one Markdown file plus any images it references. The deck is saved next to the archive with a `.pptx` extension.

| Option | Description |
| --- | --- |
| `-o`, `--output` | Output `.pptx` path (default: archive name with a `.pptx` suffix) |
| `-v`, `--verbose` | Enable debug logging |

A relative archive name is looked for in the current folder first, then in the project folder, so the program can be launched from any directory.

## Markdown syntax

| Syntax | Result |
| --- | --- |
| `# Text` | First occurrence sets the presentation title; any later one sets the closing slide title |
| `## Text` | Starts a new slide |
| `- Text` | Adds a bullet to the current slide |
| `![alt](path)` | Adds an image to the current slide (path relative to the Markdown file) |
| `#### Text` | Adds a callout to the current slide |
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
book2pptx.py        Command-line entry point
parser/             Markdown parsing and table rendering
renderer/           PowerPoint rendering
```

## Known limitations

- Sequential `####` callouts that carry bullets do not yet start a new slide. This needs a structural change in the renderer.

## License

To be added.
