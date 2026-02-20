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
└── references/
    └── example-report.typ            # Full example: Chinese report with math, tables, blocks
```

## Skill overview

The skill instructs agents to produce technical reports via two workflows:

| Workflow | Output | Toolchain |
|----------|--------|-----------|
| **PDF** | `.pdf` via Typst | `template.typ` + `report.typ` → `typst compile` |
| **HTML** | Self-contained `.html` | KaTeX CDN for math, Google Fonts for CJK |

## Development workflow

### 1. Edit the skill

Edit `SKILL.md` in this directory. The file contains:
- YAML frontmatter (name, description, license, compatibility, metadata)
- Markdown body with instructions for both PDF and HTML workflows
- Embedded Typst template (copy-verbatim block)
- HTML skeleton with KaTeX setup

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

### 5. Visual verification

Render outputs to images and inspect:

```bash
# HTML → PNG (chromium headless)
chromium --headless --disable-gpu --no-sandbox \
  --screenshot=local_data/report_html.png \
  --window-size=1200,2400 \
  "file://$(pwd)/local_data/report.html"

# PDF → SVG → PNG (no ImageMagick needed)
typst compile local_data/report.typ "local_data/page_{n}.svg"
for f in local_data/page_*.svg; do
  chromium --headless --disable-gpu --no-sandbox \
    --screenshot="${f%.svg}.png" \
    --window-size=850,1200 "file://$(pwd)/$f"
done
rm local_data/page_*.svg

# Alternative: use pymupdf for PDF→PNG (install via uv)
uv pip install pymupdf
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

### 6. Commit

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
├── report.pdf            # Compiled PDF
├── report.html           # Self-contained HTML
├── report_html.png       # HTML screenshot
├── report_pdf_p1.png     # PDF page renders
├── report_pdf_p2.png
├── ...
```

## Known issues

- **`Latin Modern Roman` font warning**: The font may not be installed on all systems. Typst falls back gracefully to the CJK serif font. Not a blocker.
- **`typst compile --format html`**: Experimental in Typst — drops math equations. The skill intentionally uses hand-written HTML with KaTeX instead.
- **Chromium PDF→PNG**: Indirect route (PDF → SVG → chromium → PNG). Use `uv pip install pymupdf` for a cleaner path.
