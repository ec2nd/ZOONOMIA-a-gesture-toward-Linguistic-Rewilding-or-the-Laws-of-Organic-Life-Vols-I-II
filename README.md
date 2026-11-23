# NaNoGenMo 2026 — Linguistic Rewilding Pipeline

## Project Purpose

The **Linguistic Rewilding Pipeline** is an experimental text-processing engine and digital publisher developed for National Novel Generation Month (NaNoGenMo) 2026. Executed via `book.py`, the system ingests source texts from Erasmus Darwin's *Zoonomia* (`Zoonomia.txt` and `Zoonomia2.txt`) and systematically translates human language structures into nonhuman vocalizations across a continuous character map (`DeepMapEngine`), rendering a multi-page typeset PDF with dual typography.

---

## Procedural Notes

### Transformation Workflow

The pipeline in `book.py` processes selected source text through a three-tier structural calculation to establish dynamic baseline averages and determine the loci of rewilding:

1. **Tiered Threshold Calculation (`calculate_dynamic_averages`)** — Analyzes paragraphs, sentences, and words to establish rounded baseline averages for sentences per paragraph (`base_sents`), words per sentence (`base_words`), and syllables per word (`base_syls`).
2. **Locus Identification** — When a structural unit exceeds its baseline average, the point of excess acts as a locus that triggers a rewilding wave.
3. **Cascading Wave Processing (`DeepMapEngine`)** — Wave processing cascades from Macro to Micro across a continuous character array (`char_map`), tracking transformed coordinates via `is_locus` flags:
   * **Tier 3 (Macro / Paragraph):** Triggered when a paragraph exceeds the average sentence count.
   * **Tier 2 (Mid / Sentence):** Triggered when a sentence exceeds the average word count.
   * **Tier 1 (Micro / Word):** Triggered when a word exceeds the average syllable count.
4. **Asymmetric Wave Propagation (`apply_wave`)** — Backward waves (from wave start to locus) preserve human spacing and punctuation while overwriting alphabetic or previously rewilded characters; forward waves (from locus to wave end) overwrite all characters, including spaces and punctuation, fitting selected vocalizations from `sounds.jsonl` to the target span length.

### Output Artifact

* **Typeset PDF (`Zoonomia_rewilded.pdf` / `Zoonomia2_rewilded.pdf`):** A rasterized, multi-page PDF generated directly via Pillow (`LazyPageSequence`), featuring a procedurally blended cover page and dual-font typography (`baskerville.ttf` for human prose and `gwendolyn.ttf` for rewilded vocalizations and drop caps).

---

## Setup & Execution

### Environment Dependencies

Ensure Python 3.x is installed along with the required libraries:

* `Pillow` (`PIL`) — Image rendering, typography layout, and multi-page PDF streaming
* `nltk` — Punkt sentence tokenization
* `pyphen` — English (`en_US`) syllable hyphenation
* `tkinter` — Desktop GUI for volume selection, threshold confirmation, and progress tracking (included with most standard Python installations)

### Required Directory Structure

`book.py` resolves relative assets from its parent directory and working directory. Keep the following files in the same root folder:

| Filename | Description |
| :--- | :--- |
| `book.py` | Main execution script containing `DeepMapEngine`, `PDFRenderer`, and the `RewildingApp` GUI |
| `sounds.jsonl` | Corpus of nonhuman vocalizations (`word`, `ortho`, `rate`, `burst`) |
| `Zoonomia.txt` | Source text for Volume I |
| `Zoonomia2.txt` | Source text for Volume II |
| `baskerville.ttf` | Serif font for primary human text elements |
| `gwendolyn.ttf` | Display font for rewilded vocalization notation and drop caps |

### Running the Pipeline

Launch the application from the repository root:

```bash
python book.py
```

Select either **Zoonomia Volume I** or **Zoonomia Volume II** in the GUI, review and confirm the calculated structural thresholds, and allow the pipeline to compile the character map and write the output PDF.

---

## NaNoGenMo 2026 Guidelines

* **50,000+ Words:** The pipeline processes full-length source volumes exceeding the 50,000-word NaNoGenMo minimum.
* **Open Source:** All code, vocalization data, and generation algorithms are shared publicly for the event.
