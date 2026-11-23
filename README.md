# NaNoGenMo 2026 — Linguistic Rewilding Pipeline

## Project Purpose

The **Linguistic Rewilding Pipeline** is an experimental text-processing engine and digital publisher developed for National Novel Generation Month (NaNoGenMo) 2026[cite: 1]. Executed via `book.py`, the system ingests source texts from Erasmus Darwin's *Zoonomia* (`Zoonomia.txt` and `Zoonomia2.txt`) and systematically translates human language structures into nonhuman vocalizations across a continuous character map (`DeepMapEngine`), rendering a multi-page typeset PDF with dual typography[cite: 1].

---

## Procedural Notes

### Transformation Workflow

The pipeline in `book.py` processes selected source text through a three-tier structural calculation to establish dynamic baseline averages and determine the loci of rewilding[cite: 1]:

1. **Tiered Threshold Calculation (`calculate_dynamic_averages`)** — Analyzes paragraphs, sentences, and words to establish rounded baseline averages for sentences per paragraph (`base_sents`), words per sentence (`base_words`), and syllables per word (`base_syls`)[cite: 1].
2. **Locus Identification** — When a structural unit exceeds its baseline average, the point of excess acts as a locus that triggers a rewilding wave[cite: 1].
3. **Cascading Wave Processing (`DeepMapEngine`)** — Wave processing cascades from Macro to Micro across a continuous character array (`char_map`), tracking transformed coordinates via `is_locus` flags[cite: 1]:
   * **Tier 3 (Macro / Paragraph):** Triggered when a paragraph exceeds the average sentence count[cite: 1].
   * **Tier 2 (Mid / Sentence):** Triggered when a sentence exceeds the average word count[cite: 1].
   * **Tier 1 (Micro / Word):** Triggered when a word exceeds the average syllable count[cite: 1].
4. **Asymmetric Wave Propagation (`apply_wave`)** — Backward waves (from wave start to locus) preserve human spacing and punctuation while overwriting alphabetic or previously rewilded characters; forward waves (from locus to wave end) overwrite all characters, including spaces and punctuation, fitting selected vocalizations from `sounds.jsonl` to the target span length[cite: 1].

### Output Artifact

* **Typeset PDF (`Zoonomia_rewilded.pdf` / `Zoonomia2_rewilded.pdf`):** A rasterized, multi-page PDF generated directly via Pillow (`LazyPageSequence`), featuring a procedurally blended cover page and dual-font typography (`baskerville.ttf` for human prose and `gwendolyn.ttf` for rewilded vocalizations and drop caps)[cite: 1].

---

## Setup & Execution

### Environment Dependencies

Ensure Python 3.x is installed along with the required libraries[cite: 1]:

* `Pillow` (`PIL`) — Image rendering, typography layout, and multi-page PDF streaming[cite: 1]
* `nltk` — Punkt sentence tokenization[cite: 1]
* `pyphen` — English (`en_US`) syllable hyphenation[cite: 1]
* `tkinter` — Desktop GUI for volume selection, threshold confirmation, and progress tracking (included with most standard Python installations)[cite: 1]

### Required Directory Structure

`book.py` resolves relative assets from its parent directory and working directory[cite: 1]. Keep the following files in the same root folder[cite: 1]:

| Filename | Description |
| :--- | :--- |
| `book.py` | Main execution script containing `DeepMapEngine`, `PDFRenderer`, and the `RewildingApp` GUI[cite: 1] |
| `sounds.jsonl` | Corpus of nonhuman vocalizations (`word`, `ortho`, `rate`, `burst`)[cite: 1] |
| `Zoonomia.txt` | Source text for Volume I[cite: 1] |
| `Zoonomia2.txt` | Source text for Volume II[cite: 1] |
| `baskerville.ttf` | Serif font for primary human text elements[cite: 1] |
| `gwendolyn.ttf` | Display font for rewilded vocalization notation and drop caps[cite: 1] |

### Running the Pipeline

Launch the application from the repository root[cite: 1]:

```bash
python book.py
```

Select either **Zoonomia Volume I** or **Zoonomia Volume II** in the GUI, review and confirm the calculated structural thresholds, and allow the pipeline to compile the character map and write the output PDF[cite: 1].

---

## NaNoGenMo 2026 Guidelines

* **50,000+ Words:** The pipeline processes full-length source volumes exceeding the 50,000-word NaNoGenMo minimum[cite: 1].
* **Open Source:** All code, vocalization data, and generation algorithms are shared publicly for the event[cite: 1].
