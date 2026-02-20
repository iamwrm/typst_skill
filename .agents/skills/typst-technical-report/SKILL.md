---
name: typst-technical-report
description: "Create technical reports, academic papers, or formatted documents as PDF or HTML using Typst. Use when the user wants math equations, code blocks, tables, theorems, or CJK (Chinese/Japanese) content in a publication-quality document. Also triggers on 'Typst', '.typ', or requests for LaTeX-quality output. Do NOT use for .docx (use docx skill) or slides (use pptx skill)."
license: MIT
compatibility: "Requires typst ≥0.14 (pre-installed). System fonts: Latin Modern Roman, Noto Serif/Sans CJK SC/TC/JP/KR, DejaVu Sans Mono. HTML output needs network for KaTeX CDN."
metadata:
  version: "1.0"
---

# Typst Technical Report

## Output choice

| User signal | Output | Method |
|---|---|---|
| "PDF", "paper", "print", "download", or no preference | **PDF** | `typst compile report.typ report.pdf` |
| "HTML", "artifact", "preview", "render in chat" | **HTML** | Write self-contained `.html` with KaTeX |

## PDF workflow

1. Create `template.typ` in `/home/claude` using the template below
2. Create `report.typ` that imports it
3. `typst compile report.typ report.pdf`
4. Copy to `/mnt/user-data/outputs/`

### Template (copy verbatim to `template.typ`)

```typst
#let conf(
  title: none, title-en: none,
  authors: (), affiliations: (),
  date: datetime.today(),
  abstract-zh: none, abstract-en: none,
  keywords: (),
  lang: "zh", region: "cn",
  paper: "a4", columns: 1, font-size: 10.5pt,
  body,
) = {
  let cjk-serif = if lang == "ja" { "Noto Serif CJK JP" }
    else if region in ("tw","hk") { "Noto Serif CJK TC" }
    else { "Noto Serif CJK SC" }
  let first-line = if lang in ("zh","ja") { 2em } else { 0em }

  set document(
    title: if title-en != none { title-en } else { title },
    author: authors.map(a => a.name), date: date,
  )
  set page(
    paper: paper, columns: columns,
    margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
    header: context {
      if counter(page).get().first() > 1 {
        set text(7.5pt, fill: luma(120))
        [#authors.map(a => a.name).join(", ") #h(1fr) #counter(page).display()]
      }
    },
  )
  set text(font: ("Latin Modern Roman", cjk-serif), size: font-size, lang: lang, region: region)
  set par(justify: true, leading: 0.68em, spacing: 0.68em, first-line-indent: first-line)
  set heading(numbering: "1.")
  show heading.where(level: 1): it => { set text(13pt, weight: "bold"); v(1em); it; v(0.4em) }
  show heading.where(level: 2): it => { set text(11pt, weight: "bold"); v(0.7em); it; v(0.3em) }
  show raw.where(block: true): it => {
    set text(font: "DejaVu Sans Mono", size: 8.5pt)
    block(fill: luma(248), inset: 0.7em, radius: 2pt, stroke: 0.5pt + luma(220), width: 100%, it)
  }
  show raw.where(block: false): it => {
    set text(font: "DejaVu Sans Mono", size: 0.9em)
    box(fill: luma(245), inset: (x: 0.3em, y: 0.1em), radius: 1.5pt, it)
  }
  set figure(gap: 0.6em)
  show figure.caption: set text(9pt)
  set table(stroke: none, inset: (x: 0.6em, y: 0.4em))
  show table.cell.where(y: 0): set text(weight: "bold", size: 9pt)

  // Title block
  { set par(first-line-indent: 0em)
    place(top + center, scope: "parent", float: true)[
      #align(center)[
        #if title != none { text(18pt, weight: "bold")[#title] }
        #if title-en != none { v(0.2em); text(12pt, style: "italic")[#title-en] }
        #v(0.7em)
        #for (i, a) in authors.enumerate() {
          if i > 0 [, ]; text(10.5pt)[#a.name]; if "id" in a [#super[#a.id]]
        }
        #v(0.2em)
        #for af in affiliations {
          text(8.5pt, fill: luma(100), style: "italic")[#super[#af.id]#af.text]; linebreak()
        }
      ]
      #v(0.6em); #line(length: 100%, stroke: 1pt); #v(0.1em); #line(length: 100%, stroke: 0.3pt); #v(0.6em)
      #if abstract-zh != none {
        text(8.5pt, weight: "bold", fill: rgb("#8b0000"))[摘要——]
        text(9.5pt)[#abstract-zh]; v(0.4em)
      }
      #if abstract-en != none {
        text(8.5pt, weight: "bold", fill: rgb("#1a3a5c"))[Abstract—]
        text(9.5pt, style: "italic")[#abstract-en]; v(0.4em)
      }
      #if keywords.len() > 0 {
        v(0.2em); text(8.5pt)[*关键词：*#keywords.join("，")]
      }
      #v(0.3em); #line(length: 100%, stroke: 0.3pt)
    ]
  }
  body
}

#let theorem(title, body) = block(
  fill: rgb("#f0f3f8"), inset: 0.7em, below: 0.6em, above: 0.6em,
  stroke: (left: 3pt + rgb("#1a3a5c"), rest: 0.5pt + rgb("#d0d8e8")),
)[#text(9pt, weight: "bold", fill: rgb("#1a3a5c"))[#title] #v(0.2em) #body]

#let definition(title, body) = block(
  fill: rgb("#f3f8f3"), inset: 0.7em, below: 0.6em, above: 0.6em,
  stroke: (left: 3pt + rgb("#2e7d32"), rest: 0.5pt + rgb("#c8e6c9")),
)[#text(9pt, weight: "bold", fill: rgb("#2e7d32"))[#title] #v(0.2em) #body]

#let remark(title, body) = block(
  fill: rgb("#fdf8ee"), inset: 0.7em, below: 0.6em, above: 0.6em,
  stroke: (left: 3pt + rgb("#b8860b"), rest: 0.5pt + rgb("#f0e0b0")),
)[#text(9pt, weight: "bold", fill: rgb("#b8860b"))[#title] #v(0.2em) #body]
```

### Usage example

```typst
#import "template.typ": conf, theorem, definition, remark

#show: conf.with(
  title: "自适应网格细化方法",
  title-en: "Adaptive Mesh Refinement for CFD",
  authors: ((name: "陈明远", id: "†"), (name: "Elena Vasquez", id: "†")),
  affiliations: ((id: "†", text: "ETH Zürich, Applied Mathematics"),),
  abstract-zh: [本文提出自适应网格细化策略，达到 $O(h^(p+1))$ 收敛速度。],
  abstract-en: [We present an AMR strategy achieving $O(h^(p+1))$ convergence.],
  keywords: ("自适应网格", "CFD", "有限元"),
  lang: "zh",
)

= 引言
正文……

= 数学建模
$ frac(partial bold(u), partial t) + (bold(u) dot nabla) bold(u) = -frac(1, rho) nabla p + nu nabla^2 bold(u) $

#theorem[定理 1][$ norm(bold(u) - bold(u)_h)_(H^1) <= C h^p abs(bold(u))_(H^(p+1)) $]
```

### Language config

| `lang` | `region` | CJK font selected | Indent |
|---|---|---|---|
| `"zh"` | `"cn"` (default) | Noto Serif CJK SC | 2em |
| `"zh"` | `"tw"` / `"hk"` | Noto Serif CJK TC | 2em |
| `"ja"` | `"jp"` | Noto Serif CJK JP | 2em |
| `"en"` | any | Latin Modern only | 0em |

For English-only: set `lang: "en"`, `abstract-zh: none`.

## HTML workflow

Write a self-contained `.html` directly. Do **not** use `typst compile --format html` (drops math).

### Minimal skeleton

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>Report</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=LXGW+WenKai:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
body { font-family: 'LXGW WenKai', serif; max-width: 46rem; margin: 0 auto;
       padding: 2rem; line-height: 1.72; color: #111; }
h2 { color: #8b0000; font-size: 1.05rem; margin: 1.2rem 0 0.4rem; }
p { text-align: justify; text-indent: 2em; margin-bottom: 0.7rem; }
pre { background: #1c1c1c; color: #d4d4d4; padding: 0.8rem 1rem;
      border-radius: 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }
.math-block { margin: 0.7rem 0; text-align: center; }
</style>
</head>
<body>
<!-- KaTeX uses LaTeX syntax: \frac{a}{b}, NOT Typst syntax frac(a,b) -->
<script>
document.addEventListener("DOMContentLoaded", () =>
  renderMathInElement(document.body, {
    delimiters: [{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],
    throwOnError: false
  })
);
</script>
</body>
</html>
```

### HTML font presets

| Style | CSS `font-family` | Google Fonts slug |
|---|---|---|
| LXGW WenKai (楷) | `'LXGW WenKai', serif` | `LXGW+WenKai:wght@400;700` |
| Noto Serif (宋) | `'Noto Serif SC', serif` | `Noto+Serif+SC:wght@400;600;700` |
| Noto Sans (黑) | `'Noto Sans SC', sans-serif` | `Noto+Sans+SC:wght@400;500;700` |

For Japanese → `SC` to `JP`. For Traditional Chinese → `SC` to `TC`.

## Typst math quick ref

```
frac(a, b)   bold(u)   nabla   partial   sqrt(x)   norm(x)   abs(x)
sum   integral   product   RR  NN  ZZ  CC
in   subset   forall   exists   <=   >=   !=   approx
dot   times   arrow   tilde
```

## Pitfalls

- **Fonts in PDF:** Only use system-installed fonts. LXGW WenKai / EB Garamond are **not** installed — use only in HTML via Google Fonts.
- **Math syntax:** Typst → `frac(a, b)`. KaTeX → `\frac{a}{b}`. Never mix.
- **Typst HTML export:** Experimental, **drops equations**. Write HTML manually.
- **CJK:** Always set `lang`/`region` — controls line-breaking, spacing, and font selection.
