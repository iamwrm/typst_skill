# typst_skill

An agent skill for creating technical reports, academic papers, and formatted documents as PDF or HTML using [Typst](https://typst.app/).

## Features

- **PDF workflow** — Typst template with CJK support, math, theorem/definition/remark blocks, tables
- **HTML workflow** — Self-contained HTML with KaTeX math and Google Fonts
- **PDF file attachments** — Embed source code and data files directly inside PDFs so readers can extract them without external hosting
- **[PDF Viewer](https://gisthost.github.io/?5c30d22b56d4f124647ac416949e87fa)** — Static HTML viewer that renders PDFs and lists embedded attachments for download (uses PDF.js)

## Usage

### With pi (or compatible agent harness)

The skill is defined in `.agents/skills/typst-technical-report/` and is automatically picked up by compatible agent harnesses (e.g. [pi](https://github.com/mariozechner/pi-coding-agent)).

### With Claude.ai

1. Build the skill zip:
   ```bash
   make zip
   ```
2. Upload `local_data/typst-technical-report.zip` to a [Claude.ai](https://claude.ai) project's **Project knowledge**.

See [SKILL.md](.agents/skills/typst-technical-report/SKILL.md) for full instructions.
