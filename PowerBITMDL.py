import streamlit as st
from pathlib import Path
import tempfile
import zipfile
import os
import re
from io import BytesIO
import streamlit.components.v1 as components

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Power BI TMDL Converter",
    page_icon="⚡",
    layout="wide"
)

# =====================================================
# DARK THEME
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b0f19;
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    background: linear-gradient(135deg, #111827, #1f2937);
    padding: 2rem;
    border-radius: 16px;
    border: 1px solid #374151;
    margin-bottom: 1.5rem;
}

.hero h1 {
    color: #60a5fa;
}

.stButton>button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e3a8a);
}

.step-box {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

.step-box h3 {
    color: #60a5fa;
    margin-top: 0;
}

.footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #1f2937;
    color: #9ca3af;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="hero">
<h1>⚡ Power BI TMDL Converter</h1>
<p>Convert Power BI Semantic Models into AI-ready text format</p>
<p style="color:#9ca3af;">Built by Rajat Sachan — supporting the data community 🚀</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-box">
<h3>Step 1 — Open the report in your PowerBi desktop</h3>
<h3>Step 2 — Goto File -> Select Save As</h3>
<h3>Step 3 — Change the format from PBIX to PBIP (Ignore PBIT)</h3>
<h3>Step 4 — Pick your .SemanticModel folder</h3>
<p>This runs entirely in your browser. It walks the folder, <b>skips heavy/irrelevant files</b>
(<code>cache.abf</code>, anything inside <code>.pbi</code>, lock files, etc.), keeps every file's
relative path intact.</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CLIENT-SIDE FOLDER PICKER + FILTER + ZIP (runs in browser, one-way)
# =====================================================

components.html(
    """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <style>
        body { font-family: sans-serif; }
        #pickBtn {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.95rem;
        }
        #pickBtn:hover { background: linear-gradient(135deg, #1d4ed8, #1e3a8a); }
        #status { color: #9ca3af; margin-top: 0.8rem; font-size: 0.9rem; white-space: pre-wrap; }
        #folderInput { display: none; }
    </style>

    <input type="file" id="folderInput" webkitdirectory directory multiple />
    <button id="pickBtn">📁 Choose .SemanticModel Folder</button>
    <div id="status"></div>

    <script>
        const input = document.getElementById('folderInput');
        const btn = document.getElementById('pickBtn');
        const status = document.getElementById('status');

        const EXCLUDE_NAME_PARTS = ['cache.abf', '.lock', '.ds_store', 'thumbs.db'];
        const EXCLUDE_DIR_PARTS = ['.pbi', '.git', '__pycache__', 'node_modules'];
        const MAX_FILE_BYTES = 5 * 1024 * 1024;

        btn.addEventListener('click', () => input.click());

        input.addEventListener('change', async (e) => {
            const files = Array.from(e.target.files);
            if (!files.length) return;

            status.textContent = `Scanning ${files.length} files...`;

            const zip = new JSZip();
            let kept = 0;
            let skipped = 0;
            let rootName = 'SemanticModel';

            for (const file of files) {
                const relPath = file.webkitRelativePath || file.name;
                const lower = relPath.toLowerCase();
                const parts = lower.split('/');

                if (parts.length > 0 && rootName === 'SemanticModel') {
                    rootName = relPath.split('/')[0];
                }

                const inExcludedDir = parts.some(p => EXCLUDE_DIR_PARTS.includes(p));
                const isExcludedName = EXCLUDE_NAME_PARTS.some(part => lower.includes(part));
                const tooBig = file.size > MAX_FILE_BYTES;

                if (inExcludedDir || isExcludedName || tooBig) {
                    skipped++;
                    continue;
                }

                const buffer = await file.arrayBuffer();
                zip.file(relPath, buffer);
                kept++;
            }

            status.textContent = `Zipping ${kept} files (skipped ${skipped} heavy/irrelevant files)...`;

            const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = rootName.replace(/[^a-z0-9_\\-]/gi, '_') + '_filtered.zip';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            status.textContent = `✅ Done! Kept ${kept} files, skipped ${skipped}. ` +
                `Your filtered zip "${a.download}" has been downloaded — upload it below in Step 2.`;
        });
    </script>
    """,
    height=160,
)

st.markdown("""
<div class="step-box">
<h3>Step 2 — Upload the filtered zip</h3>
<p>Upload the small zip file that was just downloaded to your computer. It already has the correct
folder structure preserved, with the heavy cache files removed.</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# HELPERS
# =====================================================

def safe_read(file_path: Path):
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def write_file(output_dir, relative_path, content):
    out_path = output_dir / relative_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")


def find_definition_folder(root: Path):
    for p in root.rglob("definition"):
        if p.is_dir():
            return p
    return None


def extract_table_name(tmdl_text: str, fallback: str) -> str:
    match = re.search(r"^\s*table\s+(.+?)\s*$", tmdl_text, re.MULTILINE)
    if match:
        return match.group(1).strip().strip("'\"")
    return fallback


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, re.MULTILINE))


def extract_relationships(relationships_text: str):
    pairs = []
    blocks = re.split(r"\n\s*relationship\s+", relationships_text)
    for block in blocks[1:]:
        from_match = re.search(r"fromColumn:\s*(.+)", block)
        to_match = re.search(r"toColumn:\s*(.+)", block)
        if from_match and to_match:
            pairs.append((from_match.group(1).strip(), to_match.group(1).strip()))
    return pairs


def build_summary(project_name, table_names, relationship_pairs, measure_count, column_count):
    lines = []
    lines.append(f"Project Name: {project_name}")
    lines.append(f"Tables: {len(table_names)}")
    lines.append(f"Relationships: {len(relationship_pairs)}")
    lines.append(f"Measures: {measure_count}")
    lines.append(f"Columns: {column_count}")
    lines.append("")
    lines.append("Tables Found:")
    for t in table_names:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("Relationships Found:")
    for frm, to in relationship_pairs:
        lines.append(f"- {frm} -> {to}")
    return "\n".join(lines)


INSTRUCTIONS_TEXT = """How to use this export with an AI assistant (ChatGPT, Claude, Copilot, etc.)

1. Start by uploading SemanticModelSummary.txt. This gives the AI a quick overview of your
   model — table count, relationship count, measure/column counts, and the list of tables and
   relationships — without overwhelming it with raw TMDL syntax.

2. Then upload model.txt, relationships.txt, expressions.txt, and diagramlayout.txt for the
   core structure of the model (relationships, shared expressions, layout).

3. For deeper analysis — generating new DAX measures, reviewing existing ones, or asking
   questions about a specific table — upload that table's file individually from the Tables/
   folder. Uploading every table at once is usually unnecessary and can dilute the AI's
   attention; add tables one at a time as the conversation needs them.

Example prompts once uploaded:
- "Analyze my model and suggest additional measures."
- "Review the relationships for any potential issues."
- "Write a DAX measure for year-over-year sales growth using the Sales and Date tables."
"""

# =====================================================
# UPLOAD (single small zip, structure preserved inside it)
# =====================================================

uploaded_zip = st.file_uploader(
    "📦 Upload the filtered .zip from Step 1",
    type=["zip"],
    accept_multiple_files=False
)

if uploaded_zip:

    with tempfile.TemporaryDirectory() as tmp:

        root = Path(tmp)

        with zipfile.ZipFile(BytesIO(uploaded_zip.getbuffer())) as zf:
            zf.extractall(root)

        definition = find_definition_folder(root)

        if not definition:
            st.error("❌ 'definition' folder not found inside the uploaded zip. "
                     "Make sure you selected the .SemanticModel folder itself in Step 1.")
            st.stop()

        diagram_candidates = list(definition.parent.rglob("diagramLayout.json"))
        diagram = diagram_candidates[0] if diagram_candidates else (definition.parent / "diagramLayout.json")

        model = definition / "model.tmdl"
        relationships = definition / "relationships.tmdl"
        expressions = definition / "expressions.tmdl"
        tables_folder = definition / "tables"

        table_files = []
        if tables_folder.exists():
            table_files = list(tables_folder.rglob("*.tmdl"))

        st.subheader("🔍 Validation Results")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"{'✅' if diagram.exists() else '❌'} diagramLayout.json")
            st.write(f"{'✅' if model.exists() else '❌'} model.tmdl")
            st.write(f"{'✅' if expressions.exists() else '❌'} expressions.tmdl")

        with col2:
            st.write(f"{'✅' if relationships.exists() else '❌'} relationships.tmdl")
            st.write(f"📊 Tables found: {len(table_files)}")

        st.divider()

        if st.button("🚀 Convert Model", use_container_width=True):

            progress = st.progress(0)

            output = root / "Converted_Output"
            tables_out = output / "Tables"
            output.mkdir(parents=True, exist_ok=True)
            tables_out.mkdir(parents=True, exist_ok=True)

            progress.progress(10)

            if diagram.exists():
                write_file(output, "diagramlayout.txt", safe_read(diagram))

            progress.progress(20)

            if model.exists():
                write_file(output, "model.txt", safe_read(model))

            progress.progress(30)

            relationships_text = safe_read(relationships) if relationships.exists() else ""
            if relationships.exists():
                write_file(output, "relationships.txt", relationships_text)

            progress.progress(40)

            if expressions.exists():
                write_file(output, "expressions.txt", safe_read(expressions))

            progress.progress(50)

            table_names = []
            measure_count = 0
            column_count = 0

            for i, t in enumerate(table_files):
                rel_path = t.relative_to(tables_folder)
                table_text = safe_read(t)

                table_names.append(extract_table_name(table_text, fallback=t.stem))
                measure_count += count_pattern(table_text, r"^\s*measure\s")
                column_count += count_pattern(table_text, r"^\s*column\s")

                write_file(tables_out, str(rel_path) + ".txt", table_text)

                progress.progress(50 + int((i / max(len(table_files), 1)) * 35))

            progress.progress(90)

            relationship_pairs = extract_relationships(relationships_text)
            project_name = uploaded_zip.name.replace("_filtered.zip", "").replace(".SemanticModel", "")

            summary_text = build_summary(
                project_name=project_name,
                table_names=table_names,
                relationship_pairs=relationship_pairs,
                measure_count=measure_count,
                column_count=column_count,
            )
            write_file(output, "SemanticModelSummary.txt", summary_text)
            write_file(output, "Instructions.txt", INSTRUCTIONS_TEXT)

            progress.progress(100)

            st.subheader("📋 Semantic Model Summary")
            st.code(summary_text, language=None)

            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for folder, _, files in os.walk(output):
                    for f in files:
                        full_path = Path(folder) / f
                        arcname = full_path.relative_to(output)
                        zipf.write(full_path, arcname)
            zip_buffer.seek(0)

            st.success("🎉 Conversion Completed Successfully!")

            st.download_button(
                "📥 Download Converted Package",
                zip_buffer,
                file_name="PowerBI_TMDL_Text_Export.zip",
                mime="application/zip",
                use_container_width=True
            )

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer">
<strong>Power BI TMDL Converter</strong><br>
Built by <strong>Rajat Sachan</strong> — supporting the Power BI community 🚀
</div>
""", unsafe_allow_html=True)