# typst_skill

An agent skill for creating technical reports, academic papers, and formatted documents as PDF or HTML using [Typst](https://typst.app/).

## Features

- **PDF workflow** — Typst template with CJK support, math, theorem/definition/remark blocks, tables
- **HTML workflow** — Self-contained HTML with KaTeX math and Google Fonts
- **PDF file attachments** — Embed source code and data files directly inside PDFs so readers can extract them without external hosting
- **[PDF Viewer](https://gisthost.github.io/?5c30d22b56d4f124647ac416949e87fa)** — Static HTML viewer that renders PDFs and lists embedded attachments for download (uses PDF.js)

## Usage

The skill is defined in `.agents/skills/typst-technical-report/` and is automatically picked up by compatible agent harnesses (e.g. [pi](https://github.com/mariozechner/pi-coding-agent)).

See [SKILL.md](.agents/skills/typst-technical-report/SKILL.md) for full instructions.
