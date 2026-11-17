NaNoGenMo 2026 - Linguistic Rewilding Pipeline
Project Purpose
The Linguistic Rewilding Pipeline is an experimental physics engine and digital publisher developed for National Novel Generation Month (NaNoGenMo) 2026. The system ingests standard text and systematically translates human language structures into non-human vocalizations, simulating an organic shift from structured syntax back into raw, environmental acoustic events rendered directly into a typeset manuscript.
Transformation Workflow
The pipeline processes input text using a continuous character map combined with localized Z-Axis Deep Map macro and micro calculations to generate the typeset artifact:

Continuous Character Mapping — Evaluates phonetic stream transitions in real-time, mapping character sequences directly to non-human vocalization notation.
Z-Axis Deep Map (Macro) — Calculates global acoustic density and broad spatial placement across whole narrative arcs.
Z-Axis Deep Map (Micro) — Controls fine-grained pitch contours, biomechanical resonance, and localized typographic placement per utterance.
Output Artifacts
Manuscript (Text): Text output containing the translated non-human vocalization notation.
Typeset PDF: A structurally identical layout document rendered with custom visual typography, representing the primary output artifact.
Setup Instructions
Environment Dependencies
Ensure Python 3.x is installed along with the required libraries:

FPDF (PDF generation)
Pillow / PIL (Image processing)
NLTK (Linguistic tokenization and parsing)
Required Directory Structure
All script execution relies on relative assets. Keep the following files within the same root directory:

Filename
Description
book.py
Main execution pipeline script
sounds.jsonl
Phoneme-to-vocalization mapping database
baskerville.ttf
Serif font for primary text elements
gwendolyn.ttf
Display font for vocalization notation


Run the generation pipeline via:
python book.py
NaNoGenMo Guidelines
This project adheres to the core rules of National Novel Generation Month:

50,000+ Words: The pipeline generates a complete novelty manuscript exceeding the 50k word minimum constraint.
Open Source: All code, assets, and generation algorithms are fully open-source and shared publicly for the event.
