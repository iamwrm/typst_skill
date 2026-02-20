# typst-technical-report — Development & Verification

## Specification

This skill follows the [Agent Skills specification](https://agentskills.io/specification).

Key requirements from the spec:
- `SKILL.md` has YAML frontmatter with required `name` and `description` fields
- `name` must match the parent directory name (`typst-technical-report`)
- `name`: lowercase letters, numbers, hyphens only; no leading/trailing/consecutive hyphens; max 64 chars
- `description`: max 1024 chars; describes what the skill does and when to use it
- Optional fields: `license`, `compatibility`, `metadata`, `allowed-tools`
- Keep `SKILL.md` body under 500 lines; move detailed references to separate files

## Directory structure

```
.agents/skills/typst-technical-report/
├── SKILL.md                          # Skill definition (frontmatter + instructions)
├── AGENTS.md                         # This file — development/verification docs
├── references/
│   └── example-report.typ            # Full example: Chinese report with math, tables, blocks
└── tools/
    ├── embed_files.py                # Post-processor: embed file attachments into PDF
    └── pdf-viewer.html               # Static HTML PDF viewer with attachment extraction
```

## Skill overview

The skill instructs agents to produce technical reports via two workflows:

| Workflow | Output | Toolchain |
|----------|--------|-----------|
| **PDF** | `.pdf` via Typst | `template.typ` + `report.typ` → `typst compile` |
| **HTML** | Self-contained `.html` | KaTeX CDN for math, Google Fonts for CJK |
| **PDF + attachments** | `.pdf` with embedded files | `report.typ` with `#attach()` → `tools/embed_files.py` |

## Development workflow

### 1. Edit the skill

Edit `SKILL.md` in this directory. The file contains:
- YAML frontmatter (name, description, license, compatibility, metadata)
- Markdown body with instructions for both PDF and HTML workflows
- Embedded Typst template (copy-verbatim block)
- HTML skeleton with KaTeX setup
- PDF file attachment workflow using `tools/embed_files.py`

### 2. Validate skill loading

Launch a subagent from the repo root and confirm the skill is detected without conflicts:

```bash
cd /home/wr/gh/typst_skill
pi --model claude-sonnet-4-6 --provider anthropic -p "<prompt>"
```

**What to check:**
- No `[Skill conflicts]` errors (e.g. `name does not match parent directory`)
- The skill appears under `[Skills] → project`

### 3. Test PDF workflow

Prompt the subagent to generate a PDF with Chinese text and math:

```bash
pi --model claude-opus-4-6 --provider anthropic -p "
Use the typst-technical-report skill (PDF workflow). Create template.typ and report.typ
in ./local_data/. Topic: 傅里叶变换与信号处理基础. Chinese (lang: zh). Include:
- Chinese title and English subtitle
- 3+ sections with Chinese text
- Math: Fourier transform integral, inverse transform, convolution theorem, Parseval theorem, DFT
- A table of common transform pairs
- Use theorem/definition/remark blocks
Then run: typst compile local_data/report.typ local_data/report.pdf
"
```

**Verify:**
- `typst compile` succeeds (check for font warnings — `Latin Modern Roman` warning is expected if not installed)
- PDF has correct CJK rendering, math formulas, styled blocks, and table

### 4. Test HTML workflow

```bash
pi --model claude-opus-4-6 --provider anthropic -p "
Use the typst-technical-report skill (HTML workflow). Write a self-contained HTML file
at ./local_data/report.html. Same topic, Chinese text, KaTeX math (LaTeX syntax,
NOT Typst syntax). Include table, styled sections, LXGW WenKai font.
"
```

**Verify:**
- Math uses LaTeX syntax (`\frac{a}{b}`), not Typst syntax (`frac(a, b)`)
- KaTeX CDN and Google Fonts are included in `<head>`

### 5. Test PDF attachment workflow

```bash
pi --model claude-opus-4-6 --provider anthropic -p "
Use the typst-technical-report skill. Create a PDF report about a Python sorting algorithm.
Include the Python source code in the document and also embed/attach it inside the PDF
so readers can download the original file. Output to ./local_data/report.pdf
"
```

**Verify:**
- The agent uses the `#attach()` helper in the `.typ` file
- The agent runs `tools/embed_files.py` instead of plain `typst compile`
- PyMuPDF venv is set up automatically
- The resulting PDF contains embedded files (check with):

```bash
source /tmp/embed-venv/bin/activate
python3 -c "
import fitz
doc = fitz.open('local_data/report.pdf')
print(f'Embedded files: {doc.embfile_count()}')
for i in range(doc.embfile_count()):
    info = doc.embfile_info(i)
    data = doc.embfile_get(i)
    print(f'  {info[\"name\"]} — {len(data)} bytes')
for p in range(len(doc)):
    for a in doc[p].annots():
        if a.type[1] == 'FileAttachment':
            print(f'  Annotation page {p+1}: {a.file_info[\"filename\"]} (top-right)')
"
```

**Attachment checklist:**
- [ ] `embfile_count() > 0` — files are in the embedded files collection
- [ ] FileAttachment annotations present at top-right of relevant pages
- [ ] Extracted file content is byte-identical to the original source file

### 6. Test PDF viewer

Copy `tools/pdf-viewer.html` alongside the PDF and open in a browser:

```bash
cp .agents/skills/typst-technical-report/tools/pdf-viewer.html local_data/
cd local_data && python3 -m http.server 8080
# Open http://localhost:8080/pdf-viewer.html?url=./report.pdf
```

**Verify:**
- PDF renders in the viewer
- Sidebar shows attachment cards with file icon, name, size
- Text file previews are shown inline
- Download button saves the correct file
- Copy button copies text content to clipboard

### 7. Visual verification

Render outputs to images and inspect:

```bash
# HTML → PNG (chromium headless)
chromium --headless --disable-gpu --no-sandbox \
  --screenshot=local_data/report_html.png \
  --window-size=1200,2400 \
  "file://$(pwd)/local_data/report.html"

# PDF → PNG via pymupdf
source /tmp/embed-venv/bin/activate
python3 -c "
import fitz
doc = fitz.open('local_data/report.pdf')
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    pix.save(f'local_data/report_pdf_p{i+1}.png')
"
```

**Visual checklist:**
- [ ] Chinese characters render correctly (not boxes/tofu)
- [ ] Math equations are properly typeset (integrals, fractions, subscripts)
- [ ] Theorem/definition/remark blocks have colored left borders
- [ ] Table headers are bold, rows are aligned
- [ ] Page headers show author names and page numbers (PDF, page 2+)
- [ ] Paperclip annotation icons visible at top-right of pages with attachments

### 8. Commit

```bash
git add .agents/skills/typst-technical-report/
git commit -m "Update typst-technical-report skill"
git push
```

## Output directory

Test outputs go in `./local_data/` (git-ignored). Expected files after a full test run:

```
local_data/
├── template.typ          # Typst template (copied from SKILL.md)
├── report.typ            # Generated Typst source
├── report.pdf            # Compiled PDF (with or without attachments)
├── report.html           # Self-contained HTML
├── pdf-viewer.html       # Copied from tools/ for browser testing
├── report_html.png       # HTML screenshot
├── report_pdf_p1.png     # PDF page renders
├── report_pdf_p2.png
└── ...
```

## Tools reference

### `tools/embed_files.py`

Post-processes a Typst PDF to add embedded file attachments.

**Usage:**
```bash
python3 tools/embed_files.py <input.typ> [-o output.pdf] [-d base_dir]
```

**What it does (3 steps):**
1. `typst compile input.typ output.pdf`
2. `typst query input.typ metadata --format json` — extracts `embed-file` markers with page/position
3. PyMuPDF post-processing:
   - Adds files to the PDF embedded files collection (visible in attachment panels)
   - Places FileAttachment annotations at top-right of each relevant page (stacked vertically if multiple per page)

**Requires:** `pymupdf` (installed via `uv pip install pymupdf`)

### `tools/pdf-viewer.html`

Single-file static HTML page that renders PDFs and extracts embedded attachments using PDF.js (loaded from CDN).

**Features:**
- Drag-and-drop or file picker to open PDFs
- Scrollable multi-page rendering
- Sidebar listing all embedded attachments with:
  - File icon (extension-based), filename, size
  - Inline preview for text files
  - Download and copy-to-clipboard buttons
- URL parameter support: `?url=./report.pdf`
- Works on any static hosting (GitHub Pages, S3, etc.) — no server needed

## Known issues

- **`Latin Modern Roman` font warning**: The font may not be installed on all systems. Typst falls back gracefully to the CJK serif font. Not a blocker.
- **`typst compile --format html`**: Experimental in Typst — drops math equations. The skill intentionally uses hand-written HTML with KaTeX instead.
- **PDF attachments in Preview.app**: macOS Preview does not support PDF file attachments. Use Firefox, Adobe Acrobat Reader, or the bundled `pdf-viewer.html`.
