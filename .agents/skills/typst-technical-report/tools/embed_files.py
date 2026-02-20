#!/usr/bin/env python3
"""
embed_files.py — Post-process a Typst-generated PDF to embed file attachments.

Usage:
    python embed_files.py <input.typ> [--output output.pdf] [--base-dir .]

Workflow:
  1. Compiles the .typ file to PDF via `typst compile`
  2. Queries metadata labels with `typst query` to find embed-file markers
  3. Uses PyMuPDF to embed each referenced file and place a clickable
     FileAttachment annotation at the marked position on the page.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF


def run_typst_compile(typ_path: Path, pdf_path: Path) -> None:
    """Compile .typ → .pdf"""
    cmd = ["typst", "compile", str(typ_path), str(pdf_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Typst prints warnings to stderr even on success
    if result.returncode != 0:
        print(f"typst compile failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    if result.stderr:
        # Print warnings but don't fail
        for line in result.stderr.splitlines():
            if "error" in line.lower():
                print(line, file=sys.stderr)


def query_embed_metadata(typ_path: Path) -> list[dict]:
    """Query all embed-file metadata from the .typ file."""
    cmd = ["typst", "query", str(typ_path), "metadata", "--format", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"typst query failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    all_meta = json.loads(result.stdout)
    # Filter to embed-file entries
    entries = []
    for m in all_meta:
        val = m.get("value", {})
        if isinstance(val, dict) and val.get("kind") == "embed-file":
            entries.append(val)
    return entries


def embed_files_in_pdf(pdf_path: Path, entries: list[dict], base_dir: Path) -> None:
    """
    Open the PDF, embed files, and add FileAttachment annotations.
    Saves in-place.
    """
    doc = fitz.open(str(pdf_path))

    for entry in entries:
        filename = entry["file"]
        desc = entry.get("desc", filename)
        page_num = int(entry["page"]) - 1  # Typst pages are 1-indexed, PyMuPDF 0-indexed
        # Typst coordinates: x,y in points from top-left
        x_pt = float(entry["x"])
        y_pt = float(entry["y"])

        file_path = base_dir / filename
        if not file_path.exists():
            print(f"WARNING: File not found: {file_path}, skipping", file=sys.stderr)
            continue

        file_data = file_path.read_bytes()

        # 1) Add to PDF embedded files collection (shows in attachment panel)
        try:
            doc.embfile_add(
                name=filename,
                buffer_=file_data,
                filename=filename,
                ufilename=filename,
                desc=desc,
            )
            print(f"  ✓ Embedded file: {filename} ({len(file_data)} bytes)")
        except ValueError:
            # Already embedded (duplicate name)
            print(f"  ⚠ File already embedded: {filename}")

        # 2) Add a FileAttachment annotation on the page at the marked position
        if page_num < 0 or page_num >= len(doc):
            print(f"WARNING: Page {page_num+1} out of range for {filename}", file=sys.stderr)
            continue

        page = doc[page_num]

        # Place the annotation icon at the top-right corner of the page.
        # Count existing file annotations on this page to stack them vertically.
        existing = sum(1 for a in page.annots() if a.type[1] == "FileAttachment")
        margin = 16
        icon_size = 20
        spacing = icon_size + 6
        rect = page.rect
        point = fitz.Point(
            rect.width - margin - icon_size,   # right edge
            margin + existing * spacing,        # stack downward
        )
        annot = page.add_file_annot(
            point=point,
            buffer_=file_data,
            filename=filename,
            ufilename=filename,
            desc=desc,
            icon="Paperclip",  # Options: Graph, Paperclip, PushPin, Tag
        )

        # Style the annotation
        annot.set_colors(stroke=(0.1, 0.2, 0.5))  # Dark blue
        annot.update()

        print(f"  ✓ Annotation on page {page_num+1} at top-right ({point.x:.1f}, {point.y:.1f}): {filename}")

    doc.saveIncr()
    doc.close()


def main():
    parser = argparse.ArgumentParser(
        description="Compile Typst to PDF with embedded file attachments"
    )
    parser.add_argument("input", help="Path to .typ file")
    parser.add_argument("--output", "-o", help="Output PDF path (default: same name as input)")
    parser.add_argument("--base-dir", "-d", help="Base directory for resolving file paths")
    args = parser.parse_args()

    typ_path = Path(args.input).resolve()
    if not typ_path.exists():
        print(f"Error: {typ_path} not found", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(args.base_dir).resolve() if args.base_dir else typ_path.parent
    pdf_path = Path(args.output) if args.output else typ_path.with_suffix(".pdf")

    print(f"[1/3] Compiling {typ_path.name} → {pdf_path.name}")
    run_typst_compile(typ_path, pdf_path)

    print(f"[2/3] Querying embed-file metadata")
    entries = query_embed_metadata(typ_path)
    if not entries:
        print("  No embed-file metadata found. PDF is ready (no attachments).")
        return

    print(f"  Found {len(entries)} file(s) to embed")
    for e in entries:
        print(f"    - {e['file']} (page {e['page']})")

    print(f"[3/3] Embedding files into {pdf_path.name}")
    embed_files_in_pdf(pdf_path, entries, base_dir)

    print(f"\n✅ Done! Output: {pdf_path}")
    print(f"   Open in a PDF viewer to see attachments (📎 panel or page annotations)")


if __name__ == "__main__":
    main()
