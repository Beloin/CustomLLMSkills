"""deck_kit — layout toolkit for dark 16:9 decks with python-pptx.

Extracted from a hand-built deck (python-pptx only, no template file).
Import this module, compose slides with the layout helpers, save.

    from deck_kit import Deck
    d = Deck()
    s = d.content("Fundamentos", "5G: uma rede baseada em serviços")
    d.cards(s, [("eMBB", "Banda Larga", "Alta largura de banda.", d.t.teal)])
    d.save("slides.pptx")
"""
from __future__ import annotations

import math

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

NO_GRID = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"


class Theme:
    """Colors, fonts, and page geometry. Copy and edit to restyle a deck."""

    def __init__(
        self,
        bg="0A0F16",
        surface="121B27",
        surface2="172231",
        line="1E2C3D",
        text="E9F0F7",
        muted="9FB0C0",
        faint="6B7D90",
        accent="3EE6D0",
        accent2="FFB45E",
        display="Arial",
        body="Arial",
        mono="Courier New",
        width=13.333,
        height=7.5,
        margin=0.7,
    ):
        self.bg = RGBColor.from_string(bg)
        self.surface = RGBColor.from_string(surface)
        self.surface2 = RGBColor.from_string(surface2)
        self.line = RGBColor.from_string(line)
        self.text = RGBColor.from_string(text)
        self.muted = RGBColor.from_string(muted)
        self.faint = RGBColor.from_string(faint)
        self.accent = RGBColor.from_string(accent)
        self.accent2 = RGBColor.from_string(accent2)
        self.display = display
        self.body = body
        self.mono = mono
        self.width = width
        self.height = height
        self.margin = margin

    @property
    def content_width(self):
        return self.width - 2 * self.margin

    @property
    def col3(self):
        """Width of one card in a three-column grid."""
        return (self.content_width - 0.5) / 3


class Deck:
    """A presentation plus the layout helpers used to fill it."""

    def __init__(self, theme: Theme | None = None):
        self.t = theme or Theme()
        self.prs = Presentation()
        self.prs.slide_width = Inches(self.t.width)
        self.prs.slide_height = Inches(self.t.height)
        self.blank = self.prs.slide_layouts[6]
        self._n = 0
        self._footers = []  # (run_a, run_b, index) patched with the total on save

    # ------------------------------------------------------------------ core

    def add(self):
        """Blank slide with the theme background applied."""
        s = self.prs.slides.add_slide(self.blank)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = self.t.bg
        return s

    def box(self, s, l, t, w, h):
        """Text frame inside a textbox at (l, t) with size (w, h), inches."""
        tb = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        return tf

    def para(self, tf, first=False, align=PP_ALIGN.LEFT, before=0, after=0, line=None):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.alignment = align
        if before:
            p.space_before = Pt(before)
        if after:
            p.space_after = Pt(after)
        if line:
            p.line_spacing = line
        return p

    def run(self, p, text, font=None, size=16, color=None, bold=False, italic=False):
        r = p.add_run()
        r.text = text
        r.font.name = font or self.t.body
        r.font.size = Pt(size)
        r.font.color.rgb = color if color is not None else self.t.text
        r.font.bold = bold
        r.font.italic = italic
        return r

    def rect(self, s, l, t, w, h, fill=None, line=None, round_=False):
        shp = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE,
            Inches(l), Inches(t), Inches(w), Inches(h),
        )
        if round_:
            try:
                shp.adjustments[0] = 0.08
            except Exception:
                pass
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill if fill is not None else self.t.surface
        if line is None:
            shp.line.fill.background()
        else:
            shp.line.color.rgb = line
            shp.line.width = Pt(1)
        shp.shadow.inherit = False
        return shp

    # -------------------------------------------------------------- chrome

    def header(self, s, kicker, title, number=None):
        """Kicker line + slide title + accent rule. Returns the slide."""
        t = self.t
        tf = self.box(s, t.margin, 0.5, t.content_width, 0.4)
        p = self.para(tf, first=True)
        num = self._n if number is None else number
        self.run(p, f"{num:02d}", t.mono, 12, t.accent, bold=True)
        self.run(p, "   " + kicker.upper(), t.mono, 12, t.faint, bold=True)
        tf2 = self.box(s, t.margin, 0.92, t.content_width, 0.9)
        p2 = self.para(tf2, first=True)
        self.run(p2, title, t.display, 34, t.text, bold=True)
        self.rect(s, t.margin + 0.02, 1.72, 1.5, 0.045, t.accent)
        return s

    def footer(self, s, index=None):
        """Accent tick and 'NN / TOTAL' page number (total patched on save)."""
        t = self.t
        self.rect(s, t.margin, 7.14, 0.5, 0.045, t.accent)
        tf = self.box(s, t.width - t.margin - 1.4, 7.02, 1.4, 0.3)
        p = self.para(tf, first=True, align=PP_ALIGN.RIGHT)
        idx = self._n if index is None else index
        ra = self.run(p, f"{idx:02d}", t.mono, 11, t.accent, bold=True)
        rb = self.run(p, "", t.mono, 11, t.faint)
        self._footers.append((ra, rb, idx))
        return s

    def content(self, kicker, title, number=None, chrome=True):
        """Content slide: header (+footer) with numbering handled."""
        self._n += 1
        s = self.add()
        self.header(s, kicker, title, number=number)
        if chrome:
            self.footer(s, index=number if number is not None else self._n)
        return s

    def title_slide(self, kicker, title, subtitle="", meta="", parts=None):
        """Cover slide. `parts` = [(text, style)] where style is x/em/q."""
        t = self.t
        self._n += 1
        s = self.add()
        tf = self.box(s, t.margin, 1.7, t.content_width, 0.5)
        p = self.para(tf, first=True)
        self.run(p, kicker, t.mono, 15, t.accent, bold=True)
        tf = self.box(s, t.margin, 2.15, t.content_width, 2.6)
        p = self.para(tf, first=True)
        if parts:
            for text, style in parts:
                if style == "em":
                    self.run(p, text, t.display, 66, t.accent, bold=True)
                elif style == "q":
                    self.run(p, text, t.display, 66, t.text, bold=True)
                else:
                    self.run(p, text, t.display, 66, t.text, bold=True)
        else:
            self.run(p, title, t.display, 66, t.text, bold=True)
        if subtitle:
            tf = self.box(s, t.margin, 4.35, 9.5, 1.4)
            p = self.para(tf, first=True, line=1.2)
            self.run(p, subtitle, t.body, 20, t.muted)
        if meta:
            tf = self.box(s, t.margin, 6.7, t.content_width, 0.3)
            p = self.para(tf, first=True)
            self.run(p, meta, t.mono, 11, t.faint)
        return s

    def section(self, kicker, title, sub=""):
        """Divider slide with a big number."""
        t = self.t
        self._n += 1
        s = self.add()
        tf = self.box(s, t.margin, 2.6, t.content_width, 1.4)
        p = self.para(tf, first=True)
        self.run(p, f"{self._n:02d}", t.mono, 15, t.accent, bold=True)
        self.run(p, "   " + kicker.upper(), t.mono, 15, t.faint, bold=True)
        tf = self.box(s, t.margin, 3.1, t.content_width, 1.6)
        p = self.para(tf, first=True)
        self.run(p, title, t.display, 48, t.text, bold=True)
        self.rect(s, t.margin + 0.02, 4.55, 1.5, 0.045, t.accent)
        if sub:
            tf = self.box(s, t.margin, 4.85, 9.5, 0.8)
            p = self.para(tf, first=True, line=1.2)
            self.run(p, sub, t.body, 17, t.muted)
        return s

    # -------------------------------------------------------------- content

    def text(self, s, body, top=2.05, left=None, width=None, size=16, color=None,
             align=PP_ALIGN.LEFT, height=0.5, line=1.2):
        """Plain paragraph under the header."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        tf = self.box(s, left, top, width, height)
        p = self.para(tf, first=True, align=align, line=line)
        self.run(p, body, t.body, size, color if color is not None else t.muted)
        return tf

    def cards(self, s, items, top=2.15, left=None, width=None, height=1.7, cols=3,
              gap=0.25, accent=None):
        """Grid of cards. items = [(tag, title, desc)] or [(tag, title, desc, accent)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        cw = (width - gap * (cols - 1)) / cols
        for i, item in enumerate(items):
            tag, title, desc = item[0], item[1], item[2]
            ac = item[3] if len(item) > 3 else (accent or t.accent)
            row, col = divmod(i, cols)
            x = left + col * (cw + gap)
            y = top + row * (height + gap)
            self.rect(s, x, y, cw, height, t.surface, t.line, round_=True)
            self.rect(s, x, y, cw, 0.06, ac)
            tf = self.box(s, x + 0.18, y + 0.16, cw - 0.36, height - 0.28)
            p = self.para(tf, first=True, after=4)
            self.run(p, str(tag).upper(), t.mono, 11, ac, bold=True)
            p2 = self.para(tf, after=4)
            self.run(p2, title, t.display, 17, t.text, bold=True)
            p3 = self.para(tf, line=1.15)
            self.run(p3, desc, t.body, 12.5, t.muted)
        return s

    def steps(self, s, items, top=3.4, left=None, width=None, height=1.6, cols=3,
              gap=0.25, numbered=True):
        """Numbered cards. items = [(title, desc)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        cw = (width - gap * (cols - 1)) / cols
        for i, (title, desc) in enumerate(items):
            row, col = divmod(i, cols)
            x = left + col * (cw + gap)
            y = top + row * (height + gap)
            self.rect(s, x, y, cw, height, t.surface, t.line, round_=True)
            tf = self.box(s, x + 0.2, y + 0.15, cw - 0.4, height - 0.3)
            p = self.para(tf, first=True, after=4)
            if numbered:
                self.run(p, str(i + 1), t.display, 20, t.accent, bold=True)
                self.run(p, "  " + title, t.display, 17, t.text, bold=True)
            else:
                self.run(p, title, t.display, 17, t.text, bold=True)
            p2 = self.para(tf, line=1.2)
            self.run(p2, desc, t.body, 13.5, t.muted)
        return s

    def bullets(self, s, items, top=2.6, left=None, width=None, gap=0.22, size=16):
        """Term/description bullets. items = [(term, desc)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        tf = self.box(s, left, top, width, 4.6)
        first = True
        for term, desc in items:
            p = self.para(tf, first=first, after=int(gap * 72), line=1.2)
            first = False
            self.run(p, "◆  ", t.mono, 11, t.accent, bold=True)
            self.run(p, term + ": ", t.body, size, t.text, bold=True)
            self.run(p, desc, t.body, size - 1, t.muted)
        return s

    def callout(self, s, parts, top=2.0, left=None, width=None, height=1.05):
        """Highlighted sentence. parts = [(text, style)] with style x/em/q."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        self.rect(s, left, top, width, height, RGBColor.from_string("10242B"), t.line, round_=True)
        self.rect(s, left, top, 0.07, height, t.accent)
        tf = self.box(s, left + 0.3, top + 0.2, width - 0.5, height - 0.36)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = self.para(tf, first=True, line=1.2)
        for text, style in parts:
            if style == "em":
                self.run(p, text, t.body, 17, t.text, bold=True)
            elif style == "q":
                self.run(p, text, t.mono, 15, t.accent, bold=True)
            else:
                self.run(p, text, t.body, 17, t.muted)
        return s

    def code(self, s, lines, top=2.0, left=None, width=None, height=4.3, size=13):
        """Monospace code block. lines = [(text, color)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        self.rect(s, left, top, width, height, RGBColor.from_string("0D141E"), t.line, round_=True)
        tf = self.box(s, left + 0.28, top + 0.18, width - 0.56, height - 0.32)
        first = True
        for text, color in lines:
            p = self.para(tf, first=first, after=2, line=1.15)
            first = False
            self.run(p, text if text else " ", t.mono, size, color)
        return s

    def table(self, s, headers, rows, top=2.05, left=None, width=None,
              accent_cols=None, col_w=None, row_h=0.4):
        """Grid with the theme table style. accent_cols = {col: color}."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        accent_cols = accent_cols or {}
        nrows = len(rows) + 1
        ncols = len(headers)
        gf = s.shapes.add_table(nrows, ncols, Inches(left), Inches(top),
                                Inches(width), Inches(row_h * nrows))
        tbl = gf.table
        tbl.first_row = False
        tbl.horz_banding = False
        tbl.vert_banding = False
        tblPr = tbl._tbl.tblPr
        for el in tblPr.findall(qn("a:tableStyleId")):
            tblPr.remove(el)
        sid = tblPr.makeelement(qn("a:tableStyleId"), {})
        sid.text = NO_GRID
        tblPr.append(sid)
        if col_w:
            for i, cwid in enumerate(col_w):
                tbl.columns[i].width = Inches(cwid)
        tbl.rows[0].height = Inches(row_h + 0.02)
        for r in range(1, nrows):
            tbl.rows[r].height = Inches(row_h)
        for c, htxt in enumerate(headers):
            cell = tbl.cell(0, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = t.surface2
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.14)
            cell.margin_right = Inches(0.1)
            cell.margin_top = Inches(0.05)
            cell.margin_bottom = Inches(0.05)
            p = cell.text_frame.paragraphs[0]
            color = accent_cols.get(c, t.faint)
            self.run(p, htxt.upper(), t.mono, 11, color, bold=True)
        for r, row in enumerate(rows, start=1):
            for c, val in enumerate(row):
                cell = tbl.cell(r, c)
                cell.fill.solid()
                cell.fill.fore_color.rgb = t.surface if (r % 2 == 1) else t.surface2
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.margin_left = Inches(0.14)
                cell.margin_right = Inches(0.1)
                cell.margin_top = Inches(0.06)
                cell.margin_bottom = Inches(0.06)
                p = cell.text_frame.paragraphs[0]
                p.line_spacing = 1.1
                if c == 0:
                    self.run(p, val, t.body, 14, t.text, bold=True)
                else:
                    self.run(p, val, t.body, 14, accent_cols.get(c, t.muted))
        return tbl

    def kpis(self, s, items, top=2.2, left=None, width=None, height=1.6, gap=0.25):
        """Big-number tiles. items = [(value, label, note)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        cw = (width - gap * (len(items) - 1)) / len(items)
        for i, item in enumerate(items):
            value, label = item[0], item[1]
            note = item[2] if len(item) > 2 else ""
            x = left + i * (cw + gap)
            self.rect(s, x, top, cw, height, t.surface, t.line, round_=True)
            self.rect(s, x, top, cw, 0.06, t.accent)
            tf = self.box(s, x + 0.2, top + 0.2, cw - 0.4, height - 0.35)
            p = self.para(tf, first=True, after=2)
            self.run(p, value, t.display, 34, t.accent, bold=True)
            p2 = self.para(tf, after=2)
            self.run(p2, label, t.body, 13, t.text, bold=True)
            if note:
                p3 = self.para(tf, line=1.15)
                self.run(p3, note, t.body, 11.5, t.muted)
        return s

    def quote(self, s, text, cite="", top=2.2, left=None, width=None, height=1.6):
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        self.rect(s, left, top, width, height, t.surface, t.line, round_=True)
        self.rect(s, left, top, 0.07, height, t.accent)
        tf = self.box(s, left + 0.35, top + 0.25, width - 0.7, height - 0.45)
        p = self.para(tf, first=True, line=1.25)
        self.run(p, text, t.body, 20, t.text, italic=True)
        if cite:
            p2 = self.para(tf, before=6)
            self.run(p2, cite, t.mono, 11.5, t.faint)
        return s

    def flow(self, s, nodes, top=2.6, left=None, width=None, height=1.55, gap=0.5):
        """Horizontal flow with arrow separators. nodes = [(title, desc)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        nw = (width - gap * (len(nodes) - 1)) / len(nodes)
        for i, (title, desc) in enumerate(nodes):
            x = left + i * (nw + gap)
            self.rect(s, x, top, nw, height, t.surface, t.line, round_=True)
            self.rect(s, x, top, nw, 0.06, t.accent)
            tf = self.box(s, x + 0.18, top + 0.18, nw - 0.36, height - 0.3)
            p = self.para(tf, first=True, after=4)
            self.run(p, str(i + 1), t.display, 18, t.accent, bold=True)
            self.run(p, "  " + title, t.display, 16, t.text, bold=True)
            p2 = self.para(tf, line=1.2)
            self.run(p2, desc, t.body, 12.5, t.muted)
        for i in range(len(nodes) - 1):
            ax = left + (i + 1) * (nw + gap) - gap
            tf = self.box(s, ax - 0.08, top + 0.55, gap + 0.16, 0.5)
            p = self.para(tf, first=True, align=PP_ALIGN.CENTER)
            self.run(p, "→", t.mono, 22, t.accent, bold=True)
        return s

    def references(self, s, refs, top=2.1, left=None, width=None, cols=2, gap=0.3,
                   item_h=1.08, row_gap=0.16, size=12):
        """Numbered reference list in columns. refs = [(author, citation)]."""
        t = self.t
        left = t.margin if left is None else left
        width = t.content_width if width is None else width
        col_w = (width - gap * (cols - 1)) / cols
        per_col = math.ceil(len(refs) / cols)
        for i, (author, citation) in enumerate(refs):
            col = min(i // per_col, cols - 1)
            row = i % per_col
            x = left + col * (col_w + gap)
            y = top + row * (item_h + row_gap)
            self.rect(s, x, y, col_w, item_h, t.surface, t.line, round_=True)
            tf = self.box(s, x + 0.2, y + 0.12, col_w - 0.4, item_h - 0.2)
            p = self.para(tf, first=True, line=1.05)
            self.run(p, f"[{i + 1}]  ", t.mono, 12, t.accent, bold=True)
            self.run(p, author, t.body, size + 0.5, t.text, bold=True)
            self.run(p, ", " + citation, t.body, size, t.muted)
        return s

    def image(self, s, path, top=2.0, left=None, width=None, height=None, fit=True):
        """Place a picture. The aspect ratio is always preserved.

        With fit=True and both width and height given, the picture is scaled
        down to the smaller of the two and centered in the box.
        """
        left = self.t.margin if left is None else left
        pic = s.shapes.add_picture(path, Inches(left), Inches(top))
        ratio = pic.width / pic.height
        if width is not None and height is not None:
            if fit:
                if ratio > Inches(width) / Inches(height):
                    pic.width = Inches(width)
                    pic.height = Emu(int(Inches(width) / ratio))
                else:
                    pic.height = Inches(height)
                    pic.width = Emu(int(Inches(height) * ratio))
            else:
                pic.width = Inches(width)
                pic.height = Inches(height)
        elif width is not None:
            pic.width = Inches(width)
            pic.height = Emu(int(Inches(width) / ratio))
        elif height is not None:
            pic.height = Inches(height)
            pic.width = Emu(int(Inches(height) * ratio))
        if width is not None and height is not None and fit:
            pic.left = Emu(int(Inches(left) + (Inches(width) - pic.width) / 2))
            pic.top = Emu(int(Inches(top) + (Inches(height) - pic.height) / 2))
        return pic

    def notes(self, s, text):
        """Speaker notes."""
        s.notes_slide.notes_text_frame.text = text
        return s

    # --------------------------------------------------------------- output

    def save(self, path="slides.pptx"):
        total = len(self.prs.slides._sldIdLst)
        for ra, rb, idx in self._footers:
            ra.text = f"{idx:02d}"
            rb.text = f" / {total:02d}"
        self.prs.save(path)
        return path


# --------------------------------------------------------------------- audit


def audit(path):
    """Cheap pre-flight: report shapes off-canvas and likely text overflow.

    Returns a list of strings; empty list means no obvious problem.
    """
    prs = Presentation(path)
    sw, sh = prs.slide_width, prs.slide_height
    problems = []
    for i, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if shape.left is None or shape.top is None:
                continue
            r = Emu(shape.left + (shape.width or 0))
            b = Emu(shape.top + (shape.height or 0))
            if shape.left < -Emu(10000) or shape.top < -Emu(10000) or r > sw + Emu(10000) or b > sh + Emu(10000):
                problems.append(
                    f"slide {i}: shape '{shape.shape_type}' outside canvas "
                    f"(l={shape.left.inches:.2f} t={shape.top.inches:.2f} "
                    f"r={r.inches:.2f} b={b.inches:.2f})"
                )
            if not shape.has_text_frame:
                continue
            tf = shape.text_frame
            text = tf.text.strip()
            if not text:
                continue
            w_pt = (shape.width or 0) / 12700.0
            h_pt = (shape.height or 0) / 12700.0
            est = 0.0
            for p in tf.paragraphs:
                size = 16
                for r_ in p.runs:
                    if r_.font.size:
                        size = r_.font.size.pt
                        break
                chars = len(p.text)
                cpl = max(1, int(w_pt / (size * 0.52)))
                est += math.ceil(chars / cpl) * size * 1.25
            if est > h_pt * 1.35:
                problems.append(
                    f"slide {i}: text likely overflows "
                    f"(needs ~{est:.0f}pt in {h_pt:.0f}pt): {text[:60]!r}"
                )
    return problems


def main():
    import sys

    problems = audit(sys.argv[1] if len(sys.argv) > 1 else "slides.pptx")
    if not problems:
        print("audit: clean")
    for p in problems:
        print("audit:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
