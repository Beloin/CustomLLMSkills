---
name: slide-creator
description: >
  Use when the user asks for a PowerPoint deck, a .pptx file, slides for a
  talk, a conference presentation, or a thesis defense deck. Builds a styled
  16:9 dark deck from a Python script with python-pptx and a reusable layout
  toolkit, then renders it for a visual check.
metadata:
  version: 0.1.0
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

Every layout helper, its item shape, the color attributes, and the geometry
grid: `references/layouts.md`. Read it when picking a layout or restyling a
deck.

Quick map: `title_slide` cover, `section` divider, `content` scaffold,
`text` prose, `cards` parallel concepts, `steps` ordered process, `bullets`
term plus explanation, `callout` thesis line, `code` code block, `table`
comparison, `kpis` headline metrics, `flow` pipeline, `references`
bibliography, `quote` pull quote, `image` picture.

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

## Verification

`audit(path)` from `scripts/deck_kit.py` flags shapes outside the canvas and
text whose estimated height exceeds its box by more than 35 percent. The
estimate is rough, so treat hits as "look at this slide", not "this is
broken". Run it after every build.

Render the deck and read the images before calling it done:

```bash
libreoffice --headless --convert-to pdf --outdir /tmp deck.pptx
pdftoppm -png -r 60 /tmp/deck.pdf /tmp/deck
```

The audit catches off-canvas shapes and gross overflow. Only the image catches
a bad layout.

## Provenance

This skill was extracted from a hand-written deck script: 18 slides on 6G
network slicing, dark palette, PT-BR. `deck_kit.py` keeps that exact visual
style and adds `section`, `kpis`, `flow`, `quote`, `references`, `image`, and
`notes`. Use `deck_kit.py` for anything new.
