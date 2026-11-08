# Layout catalog

Every layout helper in `scripts/deck_kit.py`. Call them on the slide returned
by `Deck.content()`, `Deck.title_slide()`, `Deck.section()`, or `Deck.add()`.

## Slide scaffolds

| Method | Use for | Item shape |
|---|---|---|
| `title_slide` | cover | kicker, `parts=[(text, style)]`, subtitle, meta |
| `section` | section divider | kicker, title, sub |
| `content` | any content slide | returns the slide; then add blocks |
| `add` | raw blank slide | no header, no numbering |

`content(kicker, title)` creates the slide, draws the header, and draws the
footer. `header(kicker, title)` and `footer()` draw them separately when you
need to control numbering.

## Content blocks

| Method | Use for | Item shape |
|---|---|---|
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

Every block takes `top`, `left`, and `width` in inches. `left` defaults to the
theme margin, `width` to the content width.

## Style codes

Inside `parts` lists:

| Code | Meaning |
|---|---|
| `"x"` | normal body text |
| `"em"` | emphasis: white, bold, larger |
| `"q"` | mono accent: teal, bold |

## Colors

| Attribute | Use |
|---|---|
| `d.t.accent` | primary accent (teal), headers, rules, numbers |
| `d.t.accent2` | secondary accent (amber), for contrast against a column |
| `d.t.text` | primary body text |
| `d.t.muted` | secondary body text |
| `d.t.faint` | tertiary text, labels |
| `d.t.surface` | card background |
| `d.t.surface2` | alternate row background |
| `d.t.line` | card border |

## Geometry

- Canvas is 13.333 x 7.5 inches (16:9). Margin is 0.7.
- Header occupies 0.5 to 1.77. Content starts at 2.0 or below.
- Footer sits at 7.02 to 7.14. Content must end by 6.9.
- Three-column grid: card width is `d.t.col3`, gap is 0.25.
- Text boxes do not clip in PowerPoint. A box set to 0.5 inches tall still
  renders a full paragraph. Give boxes the height the text actually needs, or
  the following block overlaps it.

## Low-level primitives

Use these when no layout helper matches. They are the same primitives the
helpers are built from.

| Method | Purpose |
|---|---|
| `box(s, l, t, w, h)` | text frame inside a textbox, word wrap on |
| `para(tf, first, align, before, after, line)` | paragraph with spacing |
| `run(p, text, font, size, color, bold, italic)` | a styled text run |
| `rect(s, l, t, w, h, fill, line, round_)` | rectangle or rounded rectangle |

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
theme needs that one changed in `scripts/deck_kit.py`.
