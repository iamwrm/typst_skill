#!/usr/bin/env python3
"""
embed_files.py — Post-process a Typst-generated PDF to embed file attachments.

Recommended usage:
    uv run --with pymupdf python3 tools/embed_files.py <input.typ> [--output output.pdf] [--base-dir .]

Workflow:
  1. Compile the .typ file to PDF via `typst compile`
  2. Query metadata with `typst query` to find embed-file markers
  3. Use PyMuPDF to embed each referenced file and place a clickable
     FileAttachment annotation near the marked position on the page.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


def require_pymupdf():
    try:
        import fitz  # PyMuPDF
    except ModuleNotFoundError:
        print(
            "Missing dependency: pymupdf (fitz).\n"
            "Run with uv (recommended):\n"
            "  uv run --with pymupdf python3 tools/embed_files.py <input.typ> -o <output.pdf>",
            file=sys.stderr,
        )
        sys.exit(2)
    return fitz


def run_typst_compile(typ_path: Path, pdf_path: Path) -> None:
    """Compile .typ → .pdf and surface all Typst warnings/errors."""
    cmd = ["typst", "compile", str(typ_path), str(pdf_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        print(f"typst compile failed:\n{details}", file=sys.stderr)
        sys.exit(1)

    if result.stderr.strip():
        print("typst compile warnings:", file=sys.stderr)
        for line in result.stderr.splitlines():
            print(line, file=sys.stderr)


def query_embed_metadata(typ_path: Path) -> list[dict]:
    """Query all embed-file metadata from the .typ file."""
    cmd = ["typst", "query", str(typ_path), "metadata", "--format", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"typst query failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        all_meta = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"typst query returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    entries = []
    for m in all_meta:
        val = m.get("value", {})
        if isinstance(val, dict) and val.get("kind") == "embed-file":
            entries.append(val)
    return entries


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prompt_rename_on_hash_conflict(
    name: str, existing_hash: str, new_hash: str
) -> Optional[str]:
    """
    Ask user to provide a new attachment filename when the same name maps to
    different file content. Returns None if user chooses to skip.
    """
    print(
        "\n⚠ Attachment name conflict with different content:\n"
        f"  name: {name}\n"
        f"  existing sha256: {existing_hash[:12]}...\n"
        f"  new      sha256: {new_hash[:12]}..."
    )

    if not sys.stdin.isatty():
        print(
            "ERROR: Cannot prompt for rename in non-interactive mode. "
            f"Please rename one of the files referenced as '{name}' in the Typst source.",
            file=sys.stderr,
        )
        sys.exit(1)

    while True:
        new_name = input("Enter a new attachment filename (or 'skip' to skip this marker): ").strip()
        if not new_name:
            print("Please enter a non-empty filename.")
            continue
        if new_name.lower() == "skip":
            return None
        return new_name


def embed_files_in_pdf(pdf_path: Path, entries: list[dict], base_dir: Path) -> None:
    """
    Open the PDF, embed files, and add FileAttachment annotations.
    Saves in-place.
    """
    fitz = require_pymupdf()
    doc = fitz.open(str(pdf_path))
    placement_counts: dict[tuple[int, int, int], int] = {}
    embedded_hash_by_name: dict[str, str] = {}

    embedded_count = 0
    reused_count = 0
    annotation_count = 0
    skipped_count = 0

    for entry in entries:
        filename = entry["file"]
        desc = entry.get("desc", filename)
        page_num = int(entry["page"]) - 1  # Typst pages are 1-indexed, PyMuPDF 0-indexed
        # Typst coordinates: x,y in points from top-left
        x_pt = float(entry.get("x", 0))
        y_pt = float(entry.get("y", 0))

        file_path = base_dir / filename
        if not file_path.exists():
            print(f"WARNING: File not found: {file_path}, skipping", file=sys.stderr)
            skipped_count += 1
            continue

        file_data = file_path.read_bytes()
        file_hash = sha256_hex(file_data)

        # 1) Add to PDF embedded files collection (shows in attachment panel)
        attach_name = filename
        while True:
            existing_hash = embedded_hash_by_name.get(attach_name)
            if existing_hash is None:
                doc.embfile_add(
                    name=attach_name,
                    buffer_=file_data,
                    filename=attach_name,
                    ufilename=attach_name,
                    desc=desc,
                )
                embedded_hash_by_name[attach_name] = file_hash
                embedded_count += 1
                if attach_name == filename:
                    print(f"  ✓ Embedded file: {attach_name} ({len(file_data)} bytes)")
                else:
                    print(
                        f"  ✓ Embedded file as renamed attachment: {attach_name} "
                        f"(source: {filename}, {len(file_data)} bytes)"
                    )
                break

            if existing_hash == file_hash:
                reused_count += 1
                print(
                    f"  ↺ Reused embedded file: {attach_name} "
                    f"(same sha256 {file_hash[:12]}...)"
                )
                break

            new_name = prompt_rename_on_hash_conflict(attach_name, existing_hash, file_hash)
            if new_name is None:
                print(f"  ⚠ Skipped marker for {filename}")
                skipped_count += 1
                attach_name = None
                break
            attach_name = new_name

        if attach_name is None:
            continue

        # 2) Add a FileAttachment annotation on the marked page
        if page_num < 0 or page_num >= len(doc):
            print(f"WARNING: Page {page_num + 1} out of range for {filename}", file=sys.stderr)
            skipped_count += 1
            continue

        page = doc[page_num]
        rect = page.rect
        icon_size = 20
        margin = 12

        # Place annotation near the metadata marker and keep it on-page.
        anchor_x = max(margin, min(x_pt, rect.width - icon_size - margin))
        anchor_y = max(margin, min(y_pt, rect.height - icon_size - margin))

        # If multiple attachments map to the same place, stack downward.
        key = (page_num, round(anchor_x / 8), round(anchor_y / 8))
        offset = placement_counts.get(key, 0)
        placement_counts[key] = offset + 1

        stacked_y = min(anchor_y + offset * (icon_size + 4), rect.height - icon_size - margin)
        point = fitz.Point(anchor_x, stacked_y)

        annot = page.add_file_annot(
            point=point,
            buffer_=file_data,
            filename=attach_name,
            ufilename=attach_name,
            desc=desc,
            icon="Paperclip",  # Options: Graph, Paperclip, PushPin, Tag
        )

        # Style the annotation
        annot.set_colors(stroke=(0.1, 0.2, 0.5))  # Dark blue
        annot.update()
        annotation_count += 1

        print(
            f"  ✓ Annotation on page {page_num + 1} near marker "
            f"({point.x:.1f}, {point.y:.1f}): {attach_name}"
        )

    doc.saveIncr()
    doc.close()

    print(
        "\nAttachment summary: "
        f"embedded={embedded_count}, reused={reused_count}, "
        f"annotations={annotation_count}, skipped={skipped_count}"
    )


def main() -> None:
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
    pdf_path = Path(args.output).resolve() if args.output else typ_path.with_suffix(".pdf")

    print(f"[1/3] Compiling {typ_path.name} → {pdf_path.name}")
    run_typst_compile(typ_path, pdf_path)

    print("[2/3] Querying embed-file metadata")
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
    print("   Open in a PDF viewer to see attachments (📎 panel or page annotations)")


if __name__ == "__main__":
    main()
