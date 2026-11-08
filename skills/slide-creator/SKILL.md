---
name: slide-creator
description: >
  Build styled 16:9 PowerPoint decks (.pptx) with python-pptx using a dark theme
  and reusable layout helpers. Use when the user asks to create a presentation,
  a slide deck, a .pptx file, slides for a talk, a conference talk, a thesis
  defense deck, or wants to restyle/extend an existing deck built with
  deck_kit.py. Triggers on: pptx, powerpoint, slide deck, presentation, slides,
  "make a deck", "build slides", "converter para pptx".
---

# Slide creator

Build a presentation as a Python script, not as a binary file. The script is
the source of truth: edit it, rerun it, get a new `.pptx`.

## Requirements

- Python 3.10 or newer.
- `python-pptx`.
- Optionally LibreOffice (`libreoffice --headless --convert-to pdf`) to render
  the deck to PDF or PNG for a visual check.

Pick whichever install path fits the machine:

```bash
# isolated, no install step needed
uv run --with python-pptx python build_deck.py

# inside a virtualenv
python -m venv .venv && . .venv/bin/activate && pip install python-pptx

# user install, when the system Python allows it
pip install --user python-pptx
```

If `pip install` fails with an "externally managed environment" error, the
system Python is PEP 668 managed. Use `uv run --with python-pptx` or a
virtualenv instead of `--break-system-packages`.

## Files

```
slide-creator/
├── SKILL.md                 # this file
├── scripts/deck_kit.py      # layout toolkit (import it, do not edit per deck)
└── examples/example_deck.py # full worked example
```

`scripts/deck_kit.py` sits next to this `SKILL.md`. The skill directory is the
base path for every reference below, so resolve it relative to the file the
agent is reading. Copy the `scripts/` directory next to the deck script, or
import it by path:

```python
import os, sys
SKILL_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills", "slide-creator")
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from deck_kit import Deck, audit
```

If the skill was installed somewhere else, point `SKILL_DIR` at that location.
The installed path is the parent directory of the `SKILL.md` file being read.

## How to build a deck

Follow this order every time.

1. **Outline first.** Write the slide list as plain text before writing any
   Python. One line per slide: title plus the single point it makes. A deck
   that states three things per slide states none of them.
2. **Pick one layout per slide.** Match the point to the layout. Do not force
   a table of five paragraphs into a two-column layout.
3. **Write the script.** Use `deck_kit` helpers only. Never hand-place shapes
   with raw `add_shape` unless the layout table has no match.
4. **Run it.** Fix errors, then read the audit output.
5. **Look at it.** Render to PNG and read the images. The audit catches
   off-canvas shapes and gross overflow; only the image catches a bad layout.
6. **Iterate.** Adjust `top`/`height` values until nothing collides and the
   bottom third of each slide is not empty.

## Layout catalog

| Method | Use for | Item shape |
|---|---|---|
| `title_slide` | cover | kicker, `parts=[(text, style)]`, subtitle, meta |
| `section` | section divider | kicker, title, sub |
| `content` | any content slide | returns the slide; then add blocks |
| `text` | one paragraph of prose | body string |
| `cards` | 2-6 parallel concepts | `(tag, title, desc)` or `(tag, title, desc, accent)` |
| `steps` | ordered process | `(title, desc)` |
| `bullets` | term + explanation list | `(term, desc)` |
| `callout` | the one-line thesis of the slide | `[(text, "x"\|"em"\|"q")]` |
| `code` | code or config sample | `[(text, color)]` |
| `table` | comparison or numbers | headers, rows, `accent_cols={col: color}`, `col_w` |
| `kpis` | headline metrics | `(value, label, note)` |
| `flow` | left-to-right pipeline | `(title, desc)` |
| `references` | bibliography | `(author, citation)` |
| `quote` | pull quote | text, cite |
| `image` | picture or figure | path, `width`, `height` (ratio preserved) |

Style codes inside `parts`: `"x"` normal, `"em"` emphasis (white, bold),
`"q"` mono accent (teal).

Colors come from `d.t`: `d.t.accent` (teal), `d.t.accent2` (amber),
`d.t.text`, `d.t.muted`, `d.t.faint`, `d.t.surface`, `d.t.line`.

## Geometry rules

- Canvas is 13.333 x 7.5 inches (16:9). Margin is 0.7.
- Header occupies 0.5 to 1.77. Content starts at 2.0 or below.
- Footer sits at 7.02 to 7.14. Content must end by 6.9.
- Three-column grid: card width is `d.t.col3`, gap is 0.25.
- Text boxes do not clip in PowerPoint. A box set to 0.5 inches tall still
  renders a full paragraph. Give boxes the height the text actually needs, or
  the following block overlaps it.

## The example

`examples/example_deck.py` builds a 10-slide deck about 6G network slicing:
cover, three cards, callout plus steps, bullets, code block, table, section
divider, flow plus KPIs, quote, references. It covers every layout except
`image` and `notes`.

Run it from the skill directory:

```bash
uv run --with python-pptx python examples/example_deck.py
```

It writes `examples/example.pptx` and prints the audit result.

Minimal version of the same pattern:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from deck_kit import Deck, audit

d = Deck()
s = d.content("Fundamentos", "5G: uma rede baseada em serviços")
d.text(s, "O 5G substituiu o modelo tamanho unico por um modelo baseado em servicos.")
d.cards(s, [
    ("eMBB", "Banda Larga Movel Aprimorada", "Alta largura de banda e alto throughput."),
    ("uRLLC", "Comunicacao Ultraconfiavel", "Latencia submilissegundo para tarefas criticas."),
    ("mMTC", "Comunicacao Massiva entre Maquinas", "Enorme numero de dispositivos IoT."),
], top=2.8, height=1.7)
d.save("slides.pptx")

for p in audit("slides.pptx"):
    print("audit:", p)
```

## Audit

`audit(path)` returns a list of strings. It flags shapes outside the canvas
and text whose estimated height exceeds its box by more than 35 percent. The
estimate is rough, so treat hits as "look at this slide", not "this is
broken". Run it after every build.

## Restyling

Pass a custom `Theme` to `Deck`:

```python
from deck_kit import Deck, Theme

t = Theme(accent="FF8A5C", accent2="3EE6D0", display="Inter", body="Inter")
d = Deck(theme=t)
```

Hex values are without the `#`. `Theme` also takes `bg`, `surface`, `surface2`,
`line`, `text`, `muted`, `faint`, `display`, `body`, `mono`, `width`, `height`,
`margin`.

For a light deck, set `bg` to `FFFFFF`, `text` to `111827`, `muted` to `4B5563`,
`faint` to `9CA3AF`, `surface` to `F3F4F6`, `surface2` to `E5E7EB`, `line` to
`D1D5DB`. The `callout` helper hardcodes a dark teal background, so a light
theme needs that one changed in `deck_kit.py`.

## Provenance

This skill was extracted from a hand-written deck script: 18 slides on 6G
network slicing, dark palette, PT-BR. `deck_kit.py` keeps that exact visual
style and adds `section`, `kpis`, `flow`, `quote`, `references`, `image`, and
`notes`. Use `deck_kit.py` for anything new.
