# Intake Projecten

Dit is de repository voor het Intake Projecten systeem van HR-DataLab-EAS. Hier vind je alle benodigde informatie over het project, inclusief installatie-instructies, gebruiksrichtlijnen en projectstructuur.

## Inhoudsopgave
- [Intake Projecten](#intake-projecten)
  - [Inhoudsopgave](#inhoudsopgave)
  - [Beschrijving](#beschrijving)
    - [Wat doet dit systeem?](#wat-doet-dit-systeem)
    - [Waarom dit systeem?](#waarom-dit-systeem)
  - [Projectstructuur](#projectstructuur)
  - [Vereisten](#vereisten)
    - [Benodigde Python packages](#benodigde-python-packages)
  - [Installatie](#installatie)
    - [Stap 1: Repository clonen](#stap-1-repository-clonen)
    - [Stap 2: Python environment aanmaken (aanbevolen)](#stap-2-python-environment-aanmaken-aanbevolen)
    - [Stap 3: Dependencies installeren](#stap-3-dependencies-installeren)
    - [Stap 4: Controleer de installatie](#stap-4-controleer-de-installatie)
    - [Excel bestand](#excel-bestand)
  - [Gebruik](#gebruik)
    - [Stap 1: Excel bestand voorbereiden](#stap-1-excel-bestand-voorbereiden)
    - [Stap 2: Formulieren genereren](#stap-2-formulieren-genereren)
    - [Stap 3: Output bekijken](#stap-3-output-bekijken)
  - [Output formaten](#output-formaten)
    - [HTML naar PDF converteren](#html-naar-pdf-converteren)
    - [LaTeX naar PDF converteren](#latex-naar-pdf-converteren)
  - [Mappenstructuur output](#mappenstructuur-output)
  - [LaTeX Templates](#latex-templates)
  - [Troubleshooting](#troubleshooting)
    - [❌ "forms.xlsx niet gevonden"](#-formsxlsx-niet-gevonden)
    - [❌ "ModuleNotFoundError: No module named 'pandas'"](#-modulenotfounderror-no-module-named-pandas)
    - [❌ "UnicodeDecodeError" bij het lezen van Excel](#-unicodedecodeerror-bij-het-lezen-van-excel)
    - [❌ "Kolom 'Naam' niet gevonden"](#-kolom-naam-niet-gevonden)
    - [❌ Python versie te oud](#-python-versie-te-oud)
  - [Contact](#contact)

---
ßßßßßß
## Beschrijving

Het **Intake Projecten systeem** is ontworpen om het intakeproces van projecten te stroomlijnen binnen de datalabs van de Hogeschool Rotterdam. 

### Wat doet dit systeem?
1. **Verzamelen**: Intakeformulieren worden verzameld via Microsoft Forms
2. **Exporteren**: De verzamelde data wordt geëxporteerd naar een Excel-bestand (`forms.xlsx`)
3. **Converteren**: Het Python-script converteert automatisch elke intake naar meerdere formaten:
   - 📄 **Markdown** (.md) - Voor documentatie en versiebeheer
   - 🌐 **HTML** (.html) - Voor weergave in de browser (GitHub-style)
   - 📑 **LaTeX** (.tex) - Voor professionele PDF-documenten

### Waarom dit systeem?
- **Gestandaardiseerd**: Alle intakes volgen dezelfde structuur
- **Automatisering**: Geen handmatig werk meer bij het opmaken van formulieren
- **Meerdere formaten**: Flexibel in hoe je de intakes wilt delen of archiveren
- **Versiebeheer**: Alle gegenereerde bestanden kunnen in Git worden bijgehouden

---

## Projectstructuur

```
Intake-projecten/
├── README.md                    # Dit bestand
├── requirements.txt             # Python dependencies
├── forms.xlsx                   # Input: Excel met intake data (niet in Git)
│
├── src/
│   └── generate_intake_forms.py # Hoofdscript voor het genereren van formulieren
│
└── docs/
    ├── intake_forms/            # LaTeX templates voor intake formulieren
    │   ├── INTAKE_FORMULIER.tex
    │   ├── intake_main.tex
    │   └── README.md
    │
    └── output/                  # Gegenereerde output per persoon
        └── Intake_{naam}/
            ├── Intake_{naam}.md
            ├── Intake_{naam}.html
            └── Intake_{naam}.tex
```

---

## Vereisten

Voordat je begint, zorg ervoor dat je het volgende hebt:

| Vereiste | Versie | Opmerkingen |
|----------|--------|-------------|
| Python | 3.10+ | Controleer met `python --version` |
| Git | Laatste versie | Voor versiebeheer |
| pip | Inbegrepen bij Python | Voor package management |

### Benodigde Python packages
Zie [requirements.txt](requirements.txt) voor de volledige lijst:
- `pandas` - Excel bestanden lezen
- `openpyxl` - Excel engine voor pandas
- `markdown` - Markdown naar HTML conversie
- `markdown-pdf` - Markdown naar PDF conversie
- `pillow` - Afbeeldingen bewerken (optioneel)

---

## Installatie

### Stap 1: Repository clonen
```bash
git clone https://github.com/HR-DataLab-EAS/Intake-projecten.git
cd Intake-projecten
```

### Stap 2: Python environment aanmaken (aanbevolen)
```bash
# Maak een virtuele omgeving aan
python -m venv venv

# Activeer de omgeving
# Op macOS/Linux:
source venv/bin/activate

# Op Windows:
venv\Scripts\activate
```

### Stap 3: Dependencies installeren

```bash
pip install -r requirements.txt
```

### Stap 4: Controleer de installatie

```bash
python --version  # Moet 3.10 of hoger zijn
pip list          # Toont geïnstalleerde packages
```

### Excel bestand

Voor het excel bestand `forms.xlsx`, zorg ervoor dat deze in de root van het project staat.

---

## Gebruik

### Stap 1: Excel bestand voorbereiden 

Voordat je het script kan uitvoeren zijn er een aantal dingen die je moet instellen om ervoor te zorgen dat alle gegevens correct in het `forms.xlsx` bestand komen te staan. Hieronder zijn de stappen die je moet volgen:
1. **Maak een Microsoft Form aan** met de benodigde velden voor de intake (bijv. Naam, Datum, Emailadres, Project naam, Projectbeschrijving, etc.).


Deze automatie voegt zodra er een nieuwe forum is ingevuld een rij aan het Excel bestand toe. 

**Voorbeeld van forms.xlsx structuur:**

| Naam | Datum | Emailadres | Project naam | Projectbeschrijving |
|------|-------|------------|--------------|---------------------|
| Jan | 2026-01-15 | jan@hr.nl | Dashboard Analytics | Een dashboard voor... |
| Piet | 2026-01-20 | piet@hr.nl | AI Chatbot | Een chatbot die... |

### Stap 2: Formulieren genereren

Voer het generatie-script uit vanuit de project root:

```bash
python src/generate_intake_forms.py
```

**Verwachte output:**
```
📖 Lezen van forms.xlsx...
   Gevonden kolommen: ['Naam', 'Datum', 'Emailadres', ...]
   Aantal rijen: 5

✅ Jan - Intake_Jan/
   📄 Markdown: Intake_Jan.md
   🌐 HTML: Intake_Jan.html
   📑 LaTeX: Intake_Jan.tex

✅ Piet - Intake_Piet/
   ...

🎉 Klaar! 5 formulieren verwerkt, 0 overgeslagen.
```

### Stap 3: Output bekijken

De gegenereerde bestanden vind je in `docs/output/`:

```bash
# Open de output folder
open docs/output/  # macOS
# of
explorer docs/output/  # Windows
```

---

## Output formaten

| Formaat | Extensie | Geschikt voor |
|---------|----------|---------------|
| **Markdown** | `.md` | GitHub weergave, documentatie, versiebeheer |
| **HTML** | `.html` | Direct openen in browser, presentaties |
| **LaTeX** | `.tex` | Professionele PDFs (compileren met pdflatex) |

### HTML naar PDF converteren

Open het `.html` bestand in een browser en gebruik "Afdrukken" → "Opslaan als PDF"

### LaTeX naar PDF converteren

```bash
cd docs/output/Intake_Jan/
pdflatex Intake_Jan.tex
```

---

## Mappenstructuur output

Per persoon wordt een map aangemaakt:

```
docs/output/
├── Intake_Jan/
│   ├── Intake_Jan.md       # Markdown versie
│   ├── Intake_Jan.html     # HTML versie (GitHub-styled)
│   └── Intake_Jan.tex      # LaTeX versie
│
├── Intake_Piet/
│   └── ...
```

---

## LaTeX Templates

In `docs/intake_forms/` vind je LaTeX templates voor het handmatig maken van intake formulieren:

- **intake_main.tex** - Hoofdbestand met opmaak en styling
- **INTAKE_FORMULIER.tex** - Standalone template

Zie [docs/intake_forms/README.md](docs/intake_forms/README.md) voor meer informatie over de LaTeX structuur.

---

## Troubleshooting

### ❌ "forms.xlsx niet gevonden"
- Zorg dat `forms.xlsx` in de **root** van het project staat (naast `README.md`)
- Controleer de bestandsnaam (let op hoofdletters)

### ❌ "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install -r requirements.txt
```

### ❌ "UnicodeDecodeError" bij het lezen van Excel
- Sla het Excel bestand op met UTF-8 encoding
- Of open en sla opnieuw op in een recente versie van Excel

### ❌ "Kolom 'Naam' niet gevonden"
- Het script zoekt naar `naam` of `name` (case-insensitive)
- Controleer of de kolomnamen in je Excel correct zijn

### ❌ Python versie te oud
```bash
# Controleer je Python versie
python --version

# Installeer Python 3.10+ via https://www.python.org/downloads/
```

---

## Contact

- **Team**: HR-DataLab-EAS
- **Repository**: [github.com/HR-DataLab-EAS/Intake-projecten](https://github.com/HR-DataLab-EAS/Intake-projecten)
- **Aangemaakt door**: Mitchel Reints (1040953)

---

**Laatste update:** 30 januari 2026