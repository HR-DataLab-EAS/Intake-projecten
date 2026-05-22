#!/usr/bin/env python3
"""
Generate Intake Forms - Consolidated Script
Leest forms.xlsx en genereert per naam:
- Intake_{naam}.md (Markdown)
- Intake_{naam}.html (HTML met GitHub-style CSS)
- Intake_{naam}.pdf (PDF via markdown-pdf)

Output locatie: docs/output/Intake_{naam}/
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import markdown
from markdown_pdf import MarkdownPdf, Section


# === CONFIGURATIE ===
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
FORMS_FILE = PROJECT_ROOT / "forms.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "output"

# Kolommen die als vraag/antwoord moeten worden opgenomen (excl. Naam en Datum)
QUESTION_COLUMNS = ["Emailadres", "Project naam", "Projectbeschrijving"]


# === HTML STYLING (GitHub-style) ===
HTML_STYLE = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            color: #24292f;
            background-color: #ffffff;
            max-width: 980px;
            margin: 0 auto;
            padding: 45px;
        }
        h1 {
            padding-bottom: 0.3em;
            font-size: 2em;
            border-bottom: 1px solid #d0d7de;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        h2 {
            padding-bottom: 0.3em;
            font-size: 1.5em;
            border-bottom: 1px solid #d0d7de;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        h3 {
            font-size: 1.25em;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        p {
            margin-top: 0;
            margin-bottom: 16px;
        }
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #d0d7de;
            border: 0;
        }
        blockquote {
            padding: 0 1em;
            color: #57606a;
            border-left: 0.25em solid #d0d7de;
            margin: 0 0 16px 0;
        }
        code {
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: #f6f8fa;
            border-radius: 6px;
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
        }
        pre {
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 6px;
            margin-bottom: 16px;
        }
        pre code {
            background-color: transparent;
            border: 0;
            padding: 0;
            font-size: 100%;
        }
        a {
            color: #0969da;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        ul, ol {
            padding-left: 2em;
            margin-top: 0;
            margin-bottom: 16px;
        }
        li {
            margin-top: 0.25em;
        }
        table {
            border-spacing: 0;
            border-collapse: collapse;
            margin-top: 0;
            margin-bottom: 16px;
            width: 100%;
        }
        table th {
            font-weight: 600;
            padding: 6px 13px;
            border: 1px solid #d0d7de;
            background-color: #f6f8fa;
        }
        table td {
            padding: 6px 13px;
            border: 1px solid #d0d7de;
        }
        table tr {
            background-color: #ffffff;
            border-top: 1px solid #d0d7de;
        }
        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }
        em {
            color: #57606a;
            font-style: italic;
        }
        strong {
            font-weight: 600;
        }
"""


def sanitize_filename(text: str) -> str:
    """Maak een veilige bestandsnaam van tekst."""
    if not text or pd.isna(text):
        return "onbekend"
    # Verwijder/vervang ongeldige karakters
    safe = re.sub(r'[<>:"/\\|?*]', '', str(text))
    safe = safe.strip().replace(' ', '_')
    return safe if safe else "onbekend"


def format_datum(datum_value) -> str:
    """Formatteer datum naar leesbaar formaat."""
    if pd.isna(datum_value):
        return "Onbekende datum"
    
    datum_str = str(datum_value)
    
    # Probeer ISO formaat te parsen (bijv. 2025-01-31T10:26:01.0385534Z)
    try:
        if 'T' in datum_str:
            # Verwijder microseconden en Z, parse als ISO
            clean_str = datum_str.split('.')[0]  # Verwijder microseconden
            dt = datetime.fromisoformat(clean_str)
            return dt.strftime('%d-%m-%Y %H:%M')
    except (ValueError, TypeError):
        pass
    
    # Probeer pandas timestamp
    try:
        dt = pd.to_datetime(datum_value)
        return dt.strftime('%d-%m-%Y %H:%M')
    except (ValueError, TypeError):
        pass
    
    # Fallback: return originele waarde
    return datum_str


def find_column_value(row: pd.Series, patterns: list[str]) -> str:
    """Zoek dynamisch naar kolomwaarde met case-insensitive matching."""
    for col in row.index:
        col_lower = str(col).lower().strip()
        for pattern in patterns:
            if pattern.lower() in col_lower:
                value = row[col]
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
    return ""


def get_column_value(row: pd.Series, column_name: str) -> str:
    """Haal waarde op uit specifieke kolom."""
    for col in row.index:
        if str(col).lower().strip() == column_name.lower().strip():
            value = row[col]
            if pd.notna(value):
                return str(value).strip()
    return ""


def generate_markdown(row: pd.Series, naam: str, datum: str) -> str:
    """Genereer markdown content voor een intake formulier."""
    lines = []
    
    # H1: Naam - Datum
    formatted_datum = format_datum(datum)
    lines.append(f"# {naam} - {formatted_datum}")
    lines.append("---")
    lines.append("")
    
    # H2: Per vraag met antwoord
    for col_name in QUESTION_COLUMNS:
        value = get_column_value(row, col_name)
        if not value:
            value = "*Geen antwoord gegeven*"
        
        lines.append(f"## {col_name}")
        lines.append(value)
        lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("*Gegenereerd uit forms.xlsx*")
    
    return "\n".join(lines)


def markdown_to_html(md_content: str, title: str) -> str:
    """Converteer markdown naar HTML met GitHub-style CSS."""
    # Converteer markdown naar HTML
    html_body = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    
    # Bouw volledige HTML document
    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <style>
{HTML_STYLE}
    </style>
    
</head>
<body>
    {html_body}
</body>
</html>
"""
    return html


def markdown_to_pdf(md_content: str, output_path: Path, title: str) -> None:
    """Converteer markdown naar PDF met markdown-pdf library."""
    pdf = MarkdownPdf(toc_level=0)
    pdf.add_section(Section(md_content, toc=False))
    pdf.meta["title"] = title
    pdf.meta["author"] = "HR-DataLab-EAS"
    pdf.save(str(output_path))


def markdown_to_latex(md_content: str, title: str) -> str:
    """Converteer markdown naar LaTeX document."""
    lines = md_content.split('\n')
    latex_lines = []
    
    # LaTeX document header
    latex_lines.append(r"\documentclass[a4paper,11pt]{article}")
    latex_lines.append(r"\usepackage[utf8]{inputenc}")
    latex_lines.append(r"\usepackage[T1]{fontenc}")
    latex_lines.append(r"\usepackage[dutch]{babel}")
    latex_lines.append(r"\usepackage{geometry}")
    latex_lines.append(r"\usepackage{hyperref}")
    latex_lines.append(r"\usepackage{parskip}")
    latex_lines.append(r"\geometry{margin=2.5cm}")
    latex_lines.append(r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue}")
    latex_lines.append("")
    latex_lines.append(r"\title{" + escape_latex(title) + r"}")
    latex_lines.append(r"\author{HR-DataLab-EAS}")
    latex_lines.append(r"\date{\today}")
    latex_lines.append("")
    latex_lines.append(r"\begin{document}")
    latex_lines.append(r"\maketitle")
    latex_lines.append("")
    
    # Converteer markdown naar LaTeX
    for line in lines:
        line = line.rstrip()
        
        # Skip lege regels
        if not line:
            latex_lines.append("")
            continue
        
        # Horizontale lijn
        if line == "---":
            latex_lines.append(r"\hrulefill")
            latex_lines.append("")
            continue
        
        # H1: # Titel
        if line.startswith("# "):
            section_title = escape_latex(line[2:])
            latex_lines.append(r"\section*{" + section_title + r"}")
            continue
        
        # H2: ## Vraag
        if line.startswith("## "):
            subsection_title = escape_latex(line[3:])
            latex_lines.append(r"\subsection*{" + subsection_title + r"}")
            continue
        
        # Italic tekst: *tekst*
        if line.startswith("*") and line.endswith("*") and not line.startswith("**"):
            italic_text = escape_latex(line[1:-1])
            latex_lines.append(r"\textit{" + italic_text + r"}")
            latex_lines.append("")
            continue
        
        # Normale tekst
        latex_lines.append(escape_latex(line))
        latex_lines.append("")
    
    # LaTeX document footer
    latex_lines.append(r"\end{document}")
    
    return "\n".join(latex_lines)


def escape_latex(text: str) -> str:
    """Escape speciale LaTeX karakters."""
    # Volgorde is belangrijk: eerst backslash, dan de rest
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def unique_path(path: Path) -> Path:
    """Return een niet-bestaand pad door een timestamp/counter toe te voegen als nodig.
    Dit vermijdt overschrijven van bestaande (mogelijk read-only) bestanden.
    """
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    new_path = path.parent / f"{stem}_{timestamp}{suffix}"
    counter = 1
    while new_path.exists():
        new_path = path.parent / f"{stem}_{timestamp}_{counter}{suffix}"
        counter += 1
    return new_path


def process_forms():
    """Hoofdfunctie: verwerk alle forms uit forms.xlsx."""
    
    # Check of forms.xlsx bestaat
    if not FORMS_FILE.exists():
        print(f"❌ Fout: {FORMS_FILE} niet gevonden!")
        print(f"   Zorg dat forms.xlsx in de project root staat: {PROJECT_ROOT}")
        sys.exit(1)
    
    # Lees Excel bestand
    print(f"📖 Lezen van {FORMS_FILE}...")
    try:
        df = pd.read_excel(FORMS_FILE, sheet_name=0)
    except Exception as e:
        print(f"❌ Fout bij lezen Excel: {e}")
        sys.exit(1)
    
    print(f"   Gevonden kolommen: {list(df.columns)}")
    print(f"   Aantal rijen: {len(df)}")
    
    # Maak output directory aan
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Verwerk elke rij
    processed = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        # Haal naam op
        naam = find_column_value(row, ['naam', 'name'])
        
        # Skip rijen zonder naam
        if not naam:
            print(f"   ⏭️  Rij {idx + 2}: Geen naam gevonden, overslaan...")
            skipped += 1
            continue
        
        # Haal datum op
        datum = find_column_value(row, ['datum', 'date', 'timestamp'])
        
        # Maak veilige bestandsnaam
        safe_naam = sanitize_filename(naam)
        folder_name = f"Intake_{safe_naam}"
        file_base = f"Intake_{safe_naam}"
        
        # Output directory voor deze persoon
        person_dir = OUTPUT_DIR / folder_name
        
        # Als directory bestaat: verander niets aan bestaande bestanden.
        # We maken geen bestanden read-only schrijfbaar en verwijderen niets.
        if person_dir.exists():
            print(f"   📁 Map bestaat: {folder_name}/ — bestanden worden niet verwijderd; nieuwe bestanden krijgen unieke namen")
        else:
            person_dir.mkdir(parents=True, exist_ok=True)
        
        # Genereer markdown
        md_content = generate_markdown(row, naam, datum)
        
        # === Opslaan Markdown ===
        md_path = unique_path(person_dir / f"{file_base}.md")
        md_path.write_text(md_content, encoding='utf-8')
        print(f"   📝 Markdown: {md_path.relative_to(PROJECT_ROOT)}")
        
        # === Opslaan HTML ===
        html_content = markdown_to_html(md_content, naam)
        html_path = unique_path(person_dir / f"{file_base}.html")
        html_path.write_text(html_content, encoding='utf-8')
        print(f"   🌐 HTML: {html_path.relative_to(PROJECT_ROOT)}")
        
        # === Opslaan PDF ===
        pdf_path = unique_path(person_dir / f"{file_base}.pdf")
        try:
            markdown_to_pdf(md_content, pdf_path, naam)
            print(f"   📄 PDF: {pdf_path.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"   ⚠️  PDF generatie mislukt: {e}")
        
        # === Opslaan LaTeX ===
        latex_content = markdown_to_latex(md_content, naam)
        latex_path = unique_path(person_dir / f"{file_base}.tex")
        latex_path.write_text(latex_content, encoding='utf-8')
        print(f"   📐 LaTeX: {latex_path.relative_to(PROJECT_ROOT)}")
        
        processed += 1
    
    # Samenvatting
    print("")
    print("=" * 50)
    print(f"✅ Verwerking voltooid!")
    print(f"   Verwerkt: {processed} formulieren")
    print(f"   Overgeslagen: {skipped} rijen (geen naam)")
    print(f"   Output: {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/")
    print("=" * 50)


def cleanup_old_directories():
    """Verwijder oude output directories indien gewenst."""
    old_dirs = [
        PROJECT_ROOT / "intake_forms_output",
        PROJECT_ROOT / "intake_forms_html"
    ]
    
    for old_dir in old_dirs:
        if old_dir.exists():
            response = input(f"🗑️  Verwijder oude directory '{old_dir.name}'? [j/N]: ")
            if response.lower() in ['j', 'ja', 'y', 'yes']:
                shutil.rmtree(old_dir)
                print(f"   Verwijderd: {old_dir.name}/")


if __name__ == "__main__":
    print("")
    print("=" * 50)
    print("📋 Intake Forms Generator")
    print("=" * 50)
    print("")
    
    # Verwerk formulieren
    process_forms()
    
    # Vraag of oude directories verwijderd moeten worden
    print("")
    cleanup_old_directories()
