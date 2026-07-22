#!/usr/bin/env python3
"""Render the authoritative standalone Fold Protein paper as a publication PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "papers" / "From_One_Theorem_to_Blind_Protein_Structure_A_Zero_Parameter_Computational_Proof.md"
OUTPUT = ROOT / "output" / "pdf" / "00_MAIN_PAPER_From_One_Self_Proven_Theorem_to_Blind_Protein_Structure.pdf"

NAVY = colors.HexColor("#102A43")
TEAL = colors.HexColor("#087F8C")
CYAN = colors.HexColor("#DDF4F5")
PALE = colors.HexColor("#F3F7FA")
MID = colors.HexColor("#637381")
RULE = colors.HexColor("#C9D6E2")
TEXT = colors.HexColor("#172B4D")


def register_fonts() -> None:
    base = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("Ernos", str(base / "Arial Unicode.ttf")))
    pdfmetrics.registerFont(TTFont("ErnosBold", str(base / "Arial Bold.ttf")))
    pdfmetrics.registerFont(TTFont("ErnosItalic", str(base / "Arial Italic.ttf")))
    pdfmetrics.registerFont(TTFont("ErnosBoldItalic", str(base / "Arial Bold Italic.ttf")))
    pdfmetrics.registerFontFamily(
        "Ernos",
        normal="Ernos",
        bold="ErnosBold",
        italic="ErnosItalic",
        boldItalic="ErnosBoldItalic",
    )


def inline_markup(value: str) -> str:
    value = html.escape(value.strip(), quote=True)
    value = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<link href="\2" color="#087F8C"><u>\1</u></link>',
        value,
    )
    value = re.sub(
        r"&lt;(https?://[^&]+)&gt;",
        r'<link href="\1" color="#087F8C"><u>\1</u></link>',
        value,
    )
    value = re.sub(r"`([^`]+)`", r'<font name="Ernos">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    return value


def formula_text(value: str) -> str:
    value = value.strip()
    replacements = {
        r"\operatorname{cast\_out}": "cast_out",
        r"\longrightarrow": "→",
        r"\qquad": "    ",
        r"\cdot": "·",
        r"\times": "×",
        r"\alpha": "α",
        r"\beta": "β",
        r"\phi": "φ",
        r"\psi": "ψ",
        r"\in": "∈",
        r"\circ": "°",
        r"\text{Å}": "Å",
        r"\left": "",
        r"\right": "",
        r"\lfloor": "⌊",
        r"\rfloor": "⌋",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1/\2", value)
    value = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", value)
    value = re.sub(r"_\{([^{}]+)\}", r"_(\1)", value)
    value = value.replace("\\[", "").replace("\\]", "")
    return value


def styles():
    sample = getSampleStyleSheet()
    common = dict(fontName="Ernos", textColor=TEXT, allowWidows=0, allowOrphans=0)
    return {
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontSize=9.25,
            leading=13.1,
            spaceAfter=6.2,
            alignment=TA_LEFT,
            **common,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=sample["BodyText"],
            fontSize=9.5,
            leading=13.8,
            spaceAfter=7,
            leftIndent=7 * mm,
            rightIndent=7 * mm,
            **common,
        ),
        "h1": ParagraphStyle(
            "Section",
            parent=sample["Heading1"],
            fontName="ErnosBold",
            fontSize=16,
            leading=19,
            textColor=NAVY,
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "Subsection",
            parent=sample["Heading2"],
            fontName="ErnosBold",
            fontSize=12.2,
            leading=15,
            textColor=TEAL,
            spaceBefore=9,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "Minor",
            parent=sample["Heading3"],
            fontName="ErnosBold",
            fontSize=10.2,
            leading=13,
            textColor=NAVY,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName="Ernos",
            fontSize=9.1,
            leading=12.7,
            leftIndent=6 * mm,
            firstLineIndent=-3.5 * mm,
            bulletIndent=1.5 * mm,
            spaceAfter=3,
            textColor=TEXT,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=sample["BodyText"],
            fontName="ErnosItalic",
            fontSize=9,
            leading=13,
            leftIndent=8 * mm,
            rightIndent=6 * mm,
            borderColor=TEAL,
            borderWidth=1.5,
            borderPadding=(3, 6, 3, 8),
            backColor=PALE,
            textColor=TEXT,
            spaceAfter=7,
        ),
        "formula": ParagraphStyle(
            "Formula",
            parent=sample["BodyText"],
            fontName="Ernos",
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
            textColor=NAVY,
            backColor=PALE,
            borderColor=RULE,
            borderWidth=0.5,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=6.7,
            leading=9,
            leftIndent=4 * mm,
            rightIndent=4 * mm,
            backColor=colors.HexColor("#EEF2F6"),
            borderColor=RULE,
            borderWidth=0.5,
            borderPadding=6,
            textColor=colors.HexColor("#243B53"),
            spaceBefore=4,
            spaceAfter=8,
        ),
        "toc": ParagraphStyle(
            "TOC",
            fontName="Ernos",
            fontSize=10,
            leading=15,
            textColor=TEXT,
            leftIndent=3 * mm,
            spaceAfter=1,
        ),
    }


class PublicationDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="From One Self-Proven Theorem to Blind Protein Structure: Blind Predictive Super Parity across 24 Sealed Whole-Structure Tests",
            author="Maria Smith — Ernos Labs",
            subject="Blind Predictive Super Parity across 24 sealed whole-structure tests through a zero-parameter, machine-checked protein computational proof",
            keywords="protein structure, ubiquitin, Smithian Fold Theory, computational proof, blind prediction, AlphaFold parity",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="paper", frames=[frame], onPage=self.decorate))

    @staticmethod
    def decorate(canvas, doc) -> None:
        canvas.saveState()
        page = canvas.getPageNumber()
        width, height = A4
        if page > 1:
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.45)
            canvas.line(20 * mm, height - 13 * mm, width - 20 * mm, height - 13 * mm)
            canvas.setFont("Ernos", 7.2)
            canvas.setFillColor(MID)
            canvas.drawString(20 * mm, height - 10 * mm, "FROM ONE SELF-PROVEN THEOREM TO BLIND PROTEIN STRUCTURE")
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.45)
        canvas.line(20 * mm, 12 * mm, width - 20 * mm, 12 * mm)
        canvas.setFillColor(MID)
        canvas.setFont("Ernos", 7.2)
        canvas.drawString(20 * mm, 8 * mm, "concept doi:10.5281/zenodo.21482127")
        canvas.drawRightString(width - 20 * mm, 8 * mm, f"{page}")
        canvas.restoreState()


def cover(st):
    story = [Spacer(1, 10 * mm)]
    story.append(
        Paragraph(
            "ERNOS LABS&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;SMITHIAN FOLD THEORY",
            ParagraphStyle("Brand", fontName="ErnosBold", fontSize=9, leading=12, textColor=TEAL, alignment=TA_CENTER, spaceAfter=15),
        )
    )
    story.append(
        Paragraph(
            "From One Self-Proven Theorem<br/>to Blind Protein Structure",
            ParagraphStyle("Title", fontName="ErnosBold", fontSize=25, leading=29, textColor=NAVY, alignment=TA_CENTER, spaceAfter=10),
        )
    )
    story.append(
        Paragraph(
            "Blind Predictive Super Parity across 24 sealed<br/>whole-structure tests",
            ParagraphStyle("Subtitle", fontName="Ernos", fontSize=13, leading=17, textColor=TEAL, alignment=TA_CENTER, spaceAfter=15),
        )
    )
    story.append(Paragraph("<b>Maria Smith</b><br/>Ernos Labs", ParagraphStyle("Author", fontName="Ernos", fontSize=11, leading=15, textColor=TEXT, alignment=TA_CENTER, spaceAfter=9)))
    story.append(Paragraph("22 July 2026&nbsp;&nbsp;·&nbsp;&nbsp;Standalone publication edition 2.1<br/><link href=\"https://doi.org/10.5281/zenodo.21482127\" color=\"#087F8C\"><u>concept doi:10.5281/zenodo.21482127</u></link>", ParagraphStyle("Edition", fontName="Ernos", fontSize=9, leading=13, textColor=MID, alignment=TA_CENTER, spaceAfter=16)))

    key_data = [
        [Paragraph("<b>BLIND PREDICTIVE SUPER PARITY</b>", ParagraphStyle("BoxHead", fontName="ErnosBold", fontSize=8, leading=10, textColor=colors.white, alignment=TA_CENTER))],
        [Paragraph("<b>24</b> complete blind structures&nbsp;&nbsp;|&nbsp;&nbsp;<b>0.9255486262</b> median TM<sub>repo</sub>&nbsp;&nbsp;|&nbsp;&nbsp;<b>0.7833590149 Å</b> median Cα RMSD95", ParagraphStyle("BoxResult", fontName="Ernos", fontSize=10.0, leading=15, textColor=NAVY, alignment=TA_CENTER))],
        [Paragraph("15/24 at or beyond AlphaFold's reported median · 0 weights · 0 fitted parameters · 0 target accesses before every seal", ParagraphStyle("BoxDetail", fontName="Ernos", fontSize=8.5, leading=12, textColor=TEXT, alignment=TA_CENTER))],
    ]
    key = Table(key_data, colWidths=[164 * mm], rowHeights=[9 * mm, 15 * mm, 14 * mm])
    key.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("BACKGROUND", (0, 1), (-1, -1), CYAN),
        ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([key, Spacer(1, 12 * mm)])
    story.append(
        Paragraph(
            "Twenty-four complete structures were sealed before experimental comparison. Their AlphaFold-class median accuracy is joined to first-principles derivation, machine checking, zero parameters and reproducible empirical measurement. Predictive parity plus transparent proof establishes Super Parity.",
            ParagraphStyle("CoverClaim", fontName="Ernos", fontSize=10.2, leading=15, textColor=TEXT, alignment=TA_CENTER, leftIndent=13 * mm, rightIndent=13 * mm, spaceAfter=12),
        )
    )
    story.append(Paragraph("OPEN PAPER · OPEN SOURCE · HASH-BOUND EVIDENCE", ParagraphStyle("Open", fontName="ErnosBold", fontSize=8.5, leading=11, textColor=TEAL, alignment=TA_CENTER)))
    story.append(PageBreak())
    return story


def contents(st, headings):
    flow = [Paragraph("Contents", st["h1"]), Spacer(1, 2 * mm)]
    for level, title in headings:
        if level == 2 and not title.startswith("Blind Predictive Super Parity across 24 sealed"):
            flow.append(Paragraph(inline_markup(title), st["toc"]))
    flow.append(PageBreak())
    return flow


def parse_table(lines, st, width):
    raw = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    raw = [row for row in raw if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in row)]
    cols = max(len(row) for row in raw)
    for row in raw:
        row.extend([""] * (cols - len(row)))
    if cols == 2:
        fractions = [0.33, 0.67]
    elif cols == 3:
        fractions = [0.18, 0.39, 0.43]
    elif cols == 4:
        fractions = [0.20, 0.23, 0.27, 0.30]
    elif cols == 5:
        fractions = [0.13, 0.21, 0.20, 0.23, 0.23]
    else:
        fractions = [1 / cols] * cols
    cell_style = ParagraphStyle("TableCell", parent=st["body"], fontSize=7.2, leading=9.1, spaceAfter=0)
    head_style = ParagraphStyle("TableHead", parent=cell_style, fontName="ErnosBold", textColor=colors.white)
    data = []
    for ridx, row in enumerate(raw):
        data.append([Paragraph(inline_markup(cell), head_style if ridx == 0 else cell_style) for cell in row])
    table = LongTable(data, colWidths=[width * f for f in fractions], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [table, Spacer(1, 7)]


def markdown_story(text: str, st, doc_width):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "## Abstract")
    lines = lines[start:]
    flow = []
    i = 0
    abstract_mode = False
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped or stripped == "---":
            i += 1
            continue
        if stripped.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1
            flow.append(Preformatted("\n".join(code), st["code"], maxLineLength=115))
            continue
        if stripped == "\\[":
            formula = []
            i += 1
            while i < len(lines) and lines[i].strip() != "\\]":
                formula.append(lines[i].strip())
                i += 1
            i += 1
            flow.append(Paragraph(html.escape(formula_text(" ".join(formula))), st["formula"]))
            continue
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            flow.extend(parse_table(table_lines, st, doc_width))
            continue
        if stripped.startswith("### "):
            abstract_mode = False
            flow.append(Paragraph(inline_markup(stripped[4:]), st["h2"]))
            i += 1
            continue
        if stripped.startswith("## "):
            title = stripped[3:]
            abstract_mode = title == "Abstract"
            flow.append(Paragraph(inline_markup(title), st["h1"]))
            i += 1
            continue
        if stripped.startswith("#### "):
            flow.append(Paragraph(inline_markup(stripped[5:]), st["h3"]))
            i += 1
            continue
        bullet = re.match(r"^(-|\d+\.)\s+(.*)$", stripped)
        if bullet:
            marker, body = bullet.groups()
            i += 1
            continuation = []
            while i < len(lines):
                candidate = lines[i].strip()
                if not candidate or candidate.startswith(("#", "|", "```", "\\[")) or re.match(r"^(-|\d+\.)\s+", candidate):
                    break
                continuation.append(candidate)
                i += 1
            body = " ".join([body] + continuation)
            symbol = "•" if marker == "-" else marker
            flow.append(Paragraph(inline_markup(body), st["bullet"], bulletText=symbol))
            continue
        if stripped.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip("> "))
                i += 1
            flow.append(Paragraph(inline_markup(" ".join(quote)), st["quote"]))
            continue
        paragraph = [stripped]
        i += 1
        while i < len(lines):
            candidate = lines[i].strip()
            if not candidate or candidate.startswith(("#", "|", "```", "\\[", ">")) or re.match(r"^(-|\d+\.)\s+", candidate):
                break
            paragraph.append(candidate)
            i += 1
        style = st["abstract"] if abstract_mode else st["body"]
        flow.append(Paragraph(inline_markup(" ".join(paragraph)), style))
    return flow


def build() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    st = styles()
    headings = []
    for line in source.splitlines():
        if line.startswith("## "):
            headings.append((2, line[3:]))
        elif line.startswith("### "):
            headings.append((3, line[4:]))
    doc = PublicationDoc(str(OUTPUT))
    story = cover(st)
    story.extend(contents(st, headings))
    story.extend(markdown_story(source, st, doc.width))
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
