#!/usr/bin/env python3
"""Generate a readable PDF from a small Markdown file without third-party deps."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PAGE_WIDTH = 595.28
PAGE_HEIGHT = 841.89
MARGIN_X = 48
MARGIN_TOP = 54
MARGIN_BOTTOM = 52
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN_X)


def clean_inline(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text


def escape_pdf_text(text: str) -> str:
    encoded = text.encode("cp1252", "replace").decode("cp1252")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_text(text: str, font_size: float, max_width: float, code: bool = False) -> list[str]:
    if not text:
        return [""]

    width_factor = 0.56 if code else 0.50
    max_chars = max(18, int(max_width / (font_size * width_factor)))

    lines: list[str] = []
    for original_line in text.splitlines():
        words = original_line.split(" ")
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if len(candidate) <= max_chars:
                current = candidate
                continue
            if current:
                lines.append(current)
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            current = word
        lines.append(current)
    return lines


class SimplePdf:
    def __init__(self) -> None:
        self.pages: list[str] = []
        self.current: list[str] = []
        self.y = PAGE_HEIGHT - MARGIN_TOP
        self.page_number = 0
        self._new_page()

    def _new_page(self) -> None:
        if self.current:
            self._footer()
            self.pages.append("\n".join(self.current))
        self.page_number += 1
        self.current = []
        self.y = PAGE_HEIGHT - MARGIN_TOP
        self._text("Tutorial MIP SDK Milestone", 9, "F3", MARGIN_X, PAGE_HEIGHT - 30)
        self._line(MARGIN_X, PAGE_HEIGHT - 40, PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - 40)

    def _footer(self) -> None:
        self._line(MARGIN_X, 36, PAGE_WIDTH - MARGIN_X, 36)
        self._text(f"Pagina {self.page_number}", 8, "F1", PAGE_WIDTH - MARGIN_X - 48, 22)

    def _ensure_space(self, needed: float) -> None:
        if self.y - needed < MARGIN_BOTTOM:
            self._new_page()

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.current.append(f"0.78 0.78 0.78 RG {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def _text(self, text: str, size: float, font: str, x: float, y: float) -> None:
        safe = escape_pdf_text(text)
        self.current.append(f"BT /{font} {size:.2f} Tf {x:.2f} {y:.2f} Td ({safe}) Tj ET")

    def add_paragraph(
        self,
        text: str,
        *,
        size: float = 10.5,
        font: str = "F1",
        before: float = 2,
        after: float = 5,
        indent: float = 0,
        code: bool = False,
    ) -> None:
        text = clean_inline(text) if not code else text
        lines = wrap_text(text, size, CONTENT_WIDTH - indent, code=code)
        leading = size * (1.32 if not code else 1.22)
        self._ensure_space(before + (len(lines) * leading) + after)
        self.y -= before
        for line in lines:
            self._text(line, size, font, MARGIN_X + indent, self.y)
            self.y -= leading
        self.y -= after

    def add_heading(self, text: str, level: int) -> None:
        if level == 1:
            size, before, after = 20, 12, 9
        elif level == 2:
            size, before, after = 15, 10, 7
        else:
            size, before, after = 12.5, 7, 4
        self.add_paragraph(text, size=size, font="F2", before=before, after=after)

    def add_spacer(self, height: float = 7) -> None:
        self._ensure_space(height)
        self.y -= height

    def finish(self) -> bytes:
        self._footer()
        self.pages.append("\n".join(self.current))
        return build_pdf(self.pages)


def markdown_to_pdf(markdown: str) -> bytes:
    pdf = SimplePdf()
    in_code = False

    for raw in markdown.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            pdf.add_spacer(4)
            continue

        if in_code:
            pdf.add_paragraph(line, size=8.3, font="F4", after=1, code=True)
            continue

        if not stripped:
            pdf.add_spacer(4)
            continue

        if stripped == "---":
            pdf._ensure_space(12)
            pdf._line(MARGIN_X, pdf.y, PAGE_WIDTH - MARGIN_X, pdf.y)
            pdf.y -= 12
            continue

        if stripped.startswith("# "):
            pdf.add_heading(stripped[2:], 1)
            continue
        if stripped.startswith("## "):
            pdf.add_heading(stripped[3:], 2)
            continue
        if stripped.startswith("### "):
            pdf.add_heading(stripped[4:], 3)
            continue

        if stripped.startswith("> "):
            pdf.add_paragraph(stripped[2:], size=9.8, font="F3", indent=12)
            continue

        if stripped.startswith("- [ ] "):
            pdf.add_paragraph(f"[ ] {stripped[6:]}", indent=12)
            continue
        if stripped.startswith("- "):
            pdf.add_paragraph(f"- {stripped[2:]}", indent=12)
            continue
        if re.match(r"^\d+\. ", stripped):
            pdf.add_paragraph(stripped, indent=12)
            continue

        if stripped.startswith("|"):
            compact = " | ".join(part.strip() for part in stripped.strip("|").split("|"))
            if set(compact.replace(" ", "").replace("|", "").replace("-", "")) == set():
                continue
            pdf.add_paragraph(compact, size=8.6, font="F4", after=2, code=True)
            continue

        pdf.add_paragraph(stripped)

    return pdf.finish()


def build_pdf(page_streams: list[str]) -> bytes:
    objects: list[bytes] = []

    def add(obj: str | bytes) -> int:
        objects.append(obj.encode("latin-1") if isinstance(obj, str) else obj)
        return len(objects)

    catalog_id = add("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add("PLACEHOLDER")
    font_regular = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font_bold = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    font_oblique = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")
    font_mono = add("<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>")

    page_ids: list[int] = []
    for stream in page_streams:
        stream_bytes = stream.encode("cp1252", "replace")
        content_id = add(b"<< /Length " + str(len(stream_bytes)).encode("ascii") + b" >>\nstream\n" + stream_bytes + b"\nendstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH:.2f} {PAGE_HEIGHT:.2f}] "
            f"/Resources << /Font << /F1 {font_regular} 0 R /F2 {font_bold} 0 R "
            f"/F3 {font_oblique} 0 R /F4 {font_mono} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: simple_markdown_pdf.py input.md output.pdf", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    markdown = source.read_text(encoding="utf-8")
    target.write_bytes(markdown_to_pdf(markdown))
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
