# ⚡ Power BI TMDL Converter

Convert a Power BI **Semantic Model** (`.SemanticModel` folder, TMDL format) into clean,
AI-ready text files — so you can drop them straight into ChatGPT, Claude, Copilot, or any
other LLM and ask questions about your model, get DAX measure suggestions, or review your
relationships.

Built by **Rajat Sachan** — supporting the Power BI community 🚀

---

## What it does

1. **Pick your `.SemanticModel` folder** — this happens entirely in your browser. The app
   scans the folder, skips heavy/irrelevant files (`cache.abf`, anything inside `.pbi`, lock
   files, etc.), and zips up only the small text-based definition files — keeping the
   relative folder structure intact. The filtered zip downloads automatically.

2. **Upload the filtered zip** back into the app. Since the heavy cache file is already
   excluded, this stays small and uploads instantly.

3. **Click Convert.** The app extracts:
   - `model.tmdl` → `model.txt`
   - `relationships.tmdl` → `relationships.txt`
   - `expressions.tmdl` → `expressions.txt`
   - `diagramLayout.json` → `diagramlayout.txt`
   - every table under `definition/tables/` → `Tables/<TableName>.txt`

   It also generates:
   - **`SemanticModelSummary.txt`** — a quick-glance overview (project name, table count,
     relationship count, measure/column counts, list of tables, list of relationships)
   - **`Instructions.txt`** — guidance on what order to upload files into an LLM

4. **Download the converted package** as a single zip, ready to upload to your AI assistant
   of choice.

### Output structure

```
Converted_Output/
│ SemanticModelSummary.txt
│ Instructions.txt
│ model.txt
│ relationships.txt
│ expressions.txt
│ diagramlayout.txt
│
└── Tables/
    ├── Sales.txt
    ├── Customer.txt
    ├── Product.txt
    └── ...
```

---

## Why this exists

Power BI's TMDL files are:
- ❌ Not AI-friendly out of the box
- ❌ Spread across a deep, complex folder structure
- ❌ Bundled with a heavy `cache.abf` file that's irrelevant for analysis and can blow past
  upload limits

This tool strips out the noise and gives you a clean, structured, lightweight text export an
AI assistant can actually reason about.

---

## Running locally

**Requirements:** Python 3.8+

```bash
pip install -r requirements.txt
streamlit run PowerBITMDL.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

**Browser note:** the folder picker uses `webkitdirectory`, which works in Chrome, Edge, and
Firefox, but is **not supported in Safari on iOS**. Use a desktop browser.

---

## Using the output with an AI assistant

1. Upload `SemanticModelSummary.txt` first — gives the AI a quick overview without
   overwhelming it with raw TMDL syntax.
2. Upload `model.txt`, `relationships.txt`, `expressions.txt`, and `diagramlayout.txt` for
   the core model structure.
3. For deep-dive questions on a specific table (e.g. new DAX measures), upload that table's
   file from `Tables/` individually rather than all of them at once.

Example prompts:
- "Analyze my model and suggest additional measures."
- "Review the relationships for any potential issues."
- "Write a DAX measure for year-over-year sales growth using the Sales and Date tables."
