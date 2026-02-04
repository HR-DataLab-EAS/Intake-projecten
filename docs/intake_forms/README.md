# Intake Formulier - LaTeX Structuur

## 📁 Bestandsstructuur

De LaTeX formulieren zijn nu opgesplitst in een modulaire structuur:

### Nieuwe Modulaire Structuur

```
intake_main.tex          # Hoofdbestand met preamble, packages en opmaak
intake_content.tex       # Alle content en hoofdstukken
```

#### **intake_main.tex** - Structuur & Opmaak
Dit bestand bevat:
- Document class en packages
- Pagina instellingen (marges, paper size)
- Header en footer configuratie
- Kleurdefinities (hrblue, hrgray)
- Hyperref instellingen
- Titel styling (sections, subsections)
- Custom commands voor formuliervelden:
  - `\textfield{name}{width}` - Enkelvoudig tekstveld
  - `\textfieldmultiline{name}{width}{height}` - Meerdere regels
  - `\checkbox{name}` - Checkbox
- Include statement voor content

#### **intake_content.tex** - Alle Hoofdstukken
Dit bestand bevat alle inhoud:
- Titelpagina
- Sectie 1: Algemene Projectinformatie
- Sectie 2: Contactinformatie
- Sectie 3: Projectdoelen en Scope
- Sectie 4: Technische Informatie
- Sectie 5: Kennisdeling en Herbruikbaarheid
- Sectie 6: Aanvullende Informatie
- Sectie 7: Verklaring
- Indieningsinstructies

### Oude Structuur (Backwards Compatible)

```
INTAKE_FORMULIER.tex     # Origineel bestand met alles in één
```

## 🚀 Compileren

### Nieuwe Versie (Aanbevolen)
```bash
pdflatex intake_main.tex
```

### Automatisch compileren (beide versies)
```bash
./compile.sh
```

Dit script compileert beide versies:
- `intake_main.pdf` - Modulaire versie
- `INTAKE_FORMULIER.pdf` - Originele versie

## ✏️ Aanpassingen Maken

### Opmaak wijzigen
Edit **intake_main.tex**:
- Kleuren aanpassen
- Marges veranderen
- Header/footer styling
- Font sizes
- Nieuwe custom commands toevoegen

### Content wijzigen
Edit **intake_content.tex**:
- Secties toevoegen/verwijderen
- Vragen aanpassen
- Volgorde wijzigen
- Teksten updaten

## 📦 Voordelen van de Nieuwe Structuur

1. **Scheiding van zorgen** - Opmaak en content gescheiden
2. **Herbruikbaarheid** - Opmaak kan voor meerdere documenten gebruikt worden
3. **Onderhoudbaarheid** - Makkelijker om specifieke delen aan te passen
4. **Overzichtelijkheid** - Kleinere, georganiseerde bestanden
5. **Samenwerking** - Meerdere mensen kunnen tegelijk werken (opmaak vs content)

## 🔄 Migratie

De oude `INTAKE_FORMULIER.tex` blijft beschikbaar voor backwards compatibility. 
Nieuwe wijzigingen worden aanbevolen in de modulaire structuur (`intake_main.tex` + `intake_content.tex`).

## 📋 Custom Commands

Gebruik in `intake_content.tex`:

```latex
% Enkelvoudig tekstveld
\textfield{fieldname}{12cm}

% Meerdere regels
\textfieldmultiline{fieldname}{\textwidth}{4cm}

% Checkbox
\checkbox{checkboxname}
```

## 🎨 Kleuren Aanpassen

In `intake_main.tex`:

```latex
\definecolor{hrblue}{RGB}{204,0,0}     % Hoofkleur
\definecolor{hrgray}{RGB}{100,100,100}  % Secundaire kleur
```

## 📄 Output

Beide compilaties genereren invulbare PDF formulieren met:
- Interactieve tekstvelden
- Checkboxen
- Professionele HR-styling
- Header en footer
- Genummerde secties

---

*Voor meer informatie over LaTeX, zie [LATEX_INSTRUCTIES.md](LATEX_INSTRUCTIES.md)*
