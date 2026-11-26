
"""
NaNoGenMo 2026 - Linguistic Rewilding Pipeline
----------------------------------------------
A unified physics engine and publisher.
Processes text via a continuous character map, calculating localized 
T3 (Macro) to T1 (Micro) waves. Outputs a static PDF print layout.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import nltk
import random
import pyphen
from pathlib import Path
import json
import threading
from PIL import Image, ImageDraw, ImageFont
import os
import time
import traceback

# ------------------------------------------------------------------------
# Initialization
# ------------------------------------------------------------------------
try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except Exception:
    try:
        nltk.download('punkt_tab', quiet=True)
    except Exception:
        pass

dic = pyphen.Pyphen(lang='en_US')

CONTINUANTS = set("aeiouyAEIOUYrszmnlfvwhRSZMNLFVWH")
VOWELS = set("aeiouyAEIOUY")

FALLBACK_SOUNDS = [
    {"word": "arf", "ortho": "arrf-arrf", "rate": 8.0, "burst": "staccato"},
    {"word": "baa", "ortho": "baaa-aaah", "rate": 2.0, "burst": "oozing"},
    {"word": "boof", "ortho": "bwwwf-boof", "rate": 3.0, "burst": "oozing"},
    {"word": "chip", "ortho": "tchip-tchip", "rate": 12.0, "burst": "staccato"},
    {"word": "skree", "ortho": "skreeee-kchhh", "rate": 6.5, "burst": "rapid"}
]


def get_sentence_tokenizer():
    """Returns NLTK's trained English Punkt tokenizer for consistent sentence spans."""
    if hasattr(nltk.tokenize, '_get_punkt_tokenizer'):
        try:
            return nltk.tokenize._get_punkt_tokenizer('english')
        except Exception:
            pass
    try:
        return nltk.data.load('tokenizers/punkt/english.pickle')
    except Exception:
        return nltk.tokenize.punkt.PunktSentenceTokenizer()


def load_animal_corpus():
    script_dir = Path(__file__).parent
    possible_names = ["sounds.jsonl", "animal_sounds.jsonl"]
    for name in possible_names:
        test_path = script_dir / name
        if test_path.exists():
            try:
                sounds = []
                with open(test_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        # Preserve internal hyphens for orthographic articulation
                        clean_snd = re.sub(r'[^a-zA-Z\-]', '', data.get("ortho", "")).strip('-')
                        clean_snd = re.sub(r'-+', '-', clean_snd)
                        if clean_snd and any(c.isalpha() for c in clean_snd):
                            sounds.append({
                                "word": re.sub(r'[^a-zA-Z]', '', data.get("word", "")),
                                "ortho": clean_snd,
                                "rate": float(data.get("rate", 5.0)),
                                "burst": data.get("burst", "rapid")
                            })
                if sounds:
                    return sounds
            except Exception:
                pass
    return FALLBACK_SOUNDS


# ------------------------------------------------------------------------
# Structural Analysis & Acoustic Span-Fitting Tools
# ------------------------------------------------------------------------
def calculate_dynamic_averages(text: str):
    tokenizer = get_sentence_tokenizer()
    paras = [p for p in text.split('\n\n') if p.strip()]
    total_sents, total_words, total_syls = 0, 0, 0

    for p in paras:
        sents = list(tokenizer.span_tokenize(p))
        total_sents += len(sents)
        for s_start, s_end in sents:
            sent_str = p[s_start:s_end]
            words = re.findall(r'[a-zA-Z]+', sent_str)
            total_words += len(words)
            for w in words:
                syls = dic.inserted(w).split('-')
                total_syls += len(syls)

    base_sents = max(1, round(total_sents / len(paras))) if paras else 4
    base_words = max(1, round(total_words / total_sents)) if total_sents else 15
    base_syls = max(1, round(total_syls / total_words)) if total_words else 2

    return base_syls, base_words, base_sents


def select_voice(corpus: list, tier: int, target_len: int) -> dict:
    """
    Scale-aware voice selection weighting acoustic burst, rate, and orthographic
    length relative to the structural tier and breach span length.
    """
    weights = []
    for snd in corpus:
        ortho_len = len(snd.get("ortho", "arrf"))
        burst = snd.get("burst", "rapid")
        rate = float(snd.get("rate", 5.0))

        if tier == 1:
            burst_w = 2.5 if burst == "staccato" else (1.8 if burst == "rapid" else 0.6)
            rate_w = 1.0 + (rate / 12.0)
            len_w = 1.0 / (1.0 + abs(ortho_len - target_len) * 0.15)
        elif tier == 2:
            burst_w = 2.2 if burst == "rapid" else (1.5 if burst == "oozing" else 1.2)
            rate_w = 1.0 + (1.0 - abs(rate - 6.0) / 6.0) * 0.5
            len_w = 1.0 / (1.0 + abs(ortho_len * 2 - target_len) * 0.05)
        else:
            burst_w = 2.8 if burst == "oozing" else (1.5 if burst == "rapid" else 0.7)
            rate_w = 1.0 + ((12.0 - min(12.0, rate)) / 12.0)
            len_w = 1.0 + min(1.0, ortho_len / 20.0)

        weights.append(max(0.05, burst_w * rate_w * len_w))

    return random.choices(corpus, weights=weights, k=1)[0]


def stretch_unit_internally(unit: str, target_len: int) -> str:
    """
    Stretches or compresses a single vocalization unit from its internal vowel
    or continuant nucleus rather than droning the terminal letter.
    """
    if target_len <= 0:
        return ""
    if len(unit) == target_len:
        return unit

    runs = [m.group(0) for m in re.finditer(r'(.)\1*', unit)]
    if not runs:
        return "a" * target_len

    if len(unit) > target_len:
        while sum(len(r) for r in runs) > target_len:
            longest_idx = -1
            longest_len = 1
            for i, r in enumerate(runs):
                if len(r) > longest_len:
                    longest_len = len(r)
                    longest_idx = i
            if longest_idx != -1:
                runs[longest_idx] = runs[longest_idx][:-1]
            else:
                break
        return "".join(runs)[:target_len]

    shortfall = target_len - len(unit)
    candidates = [i for i, r in enumerate(runs) if len(r) > 1 and r[0] in CONTINUANTS]
    if not candidates:
        candidates = [i for i, r in enumerate(runs) if r[0] in VOWELS]
    if not candidates:
        candidates = [i for i, r in enumerate(runs) if r[0] in CONTINUANTS]
    if not candidates:
        candidates = [len(runs) - 1]

    for k in range(shortfall):
        idx = candidates[k % len(candidates)]
        runs[idx] += runs[idx][0]

    return "".join(runs)


def fit_vocalization(sound: dict, target_length: int) -> str:
    """
    Fits a nonhuman vocalization to target_length by combining cyclic call
    repetition with internal nucleus elongation while preserving hyphen articulation.
    """
    if target_length <= 0:
        return ""

    ortho = sound.get("ortho", "arrf")
    burst = sound.get("burst", "rapid")
    parts = [p for p in ortho.split("-") if p]
    if not parts:
        parts = ["arrf"]

    if target_length == len(ortho):
        return ortho

    if target_length < len(ortho):
        acc = [parts[0]]
        for p in parts[1:]:
            candidate = "-".join(acc + [p])
            if len(candidate) <= target_length:
                acc.append(p)
            else:
                break
        base_str = "-".join(acc)
        if len(base_str) > target_length:
            return stretch_unit_internally(parts[0], target_length)
        elif len(base_str) == target_length:
            return base_str
        else:
            extra = target_length - len(base_str)
            part_lens = [len(p) for p in acc]
            for k in range(extra):
                part_lens[k % len(acc)] += 1
            return "-".join(
                stretch_unit_internally(acc[i], part_lens[i]) for i in range(len(acc))
            )

    stretch_factor = 2.2 if burst == "oozing" else (1.15 if burst == "staccato" else 1.4)
    chosen_parts = list(parts)
    idx = 0

    while True:
        current_min_len = sum(len(p) for p in chosen_parts) + (len(chosen_parts) - 1)
        max_comfortable_len = int(
            sum(len(p) * stretch_factor for p in chosen_parts) + (len(chosen_parts) - 1)
        )
        if max_comfortable_len >= target_length:
            break
        next_p = parts[idx % len(parts)]
        if current_min_len + 1 + len(next_p) <= target_length:
            chosen_parts.append(next_p)
            idx += 1
        else:
            break

    num_hyphens = len(chosen_parts) - 1
    available_alpha = target_length - num_hyphens
    part_lens = [len(p) for p in chosen_parts]
    extra = available_alpha - sum(part_lens)

    for k in range(extra):
        part_lens[k % len(chosen_parts)] += 1

    return "-".join(
        stretch_unit_internally(chosen_parts[i], part_lens[i])
        for i in range(len(chosen_parts))
    )


def match_case(orig_char: str, new_char: str) -> str:
    return new_char.upper() if orig_char.isupper() else new_char.lower()


# ------------------------------------------------------------------------
# Deep Map Z-Axis Processor (Macro to Micro Overwrites)
# ------------------------------------------------------------------------
class DeepMapEngine:
    def __init__(self, text, corpus, b_syl, b_word, b_sent):
        self.text = text
        self.corpus = corpus
        self.b_syl = b_syl
        self.b_word = b_word
        self.b_sent = b_sent
        self.char_map = []

    def apply_wave(self, start_char: int, locus_char: int, end_char: int, tier: int):
        """
        Applies a rewilding wave across [start_char, end_char]:
        - Backward wave (start_char to locus_char - 1): preserves human spacing and
          punctuation, overwriting only alphabetic characters or already-rewilded spans.
        - Forward wave (locus_char to end_char): overwrites all characters (including
          spaces and punctuation) right up to the determinate edge end_char.
        """
        back_indices = [
            i for i in range(start_char, locus_char)
            if self.char_map[i]['is_alpha'] or self.char_map[i]['is_locus']
        ]
        fwd_indices = list(range(locus_char, end_char + 1))
        target_indices = back_indices + fwd_indices
        if not target_indices:
            return

        target_set = set(target_indices)
        sound = select_voice(self.corpus, tier, len(target_indices))
        voc = fit_vocalization(sound, len(target_indices))

        for k, idx in enumerate(target_indices):
            ch = voc[k]
            # Prevent a hyphen from landing flush against a preserved space/punctuation in backward waves
            if ch == '-' and ((idx - 1 not in target_set) or (idx + 1 not in target_set)):
                if k > 0 and voc[k - 1] != '-':
                    ch = voc[k - 1]
                elif k + 1 < len(voc) and voc[k + 1] != '-':
                    ch = voc[k + 1]
                else:
                    ch = 'a'
            self.char_map[idx]['char'] = match_case(self.char_map[idx]['orig'], ch)
            self.char_map[idx]['is_locus'] = True

    def build(self):
        for i, c in enumerate(self.text):
            self.char_map.append({
                'idx': i,
                'orig': c,
                'char': c,
                'is_alpha': c.isalpha(),
                'is_locus': False,
                'type': 'base'
            })

        tokenizer = get_sentence_tokenizer()
        para_spans = [(m.start(), m.end() - 1) for m in re.finditer(r'(?:[^\n]|\n(?!\n))+', self.text)]

        for p_start, p_end in para_spans:
            para_text = self.text[p_start:p_end + 1]
            sents = list(tokenizer.span_tokenize(para_text))

            # --- Tier 3 (Sentence/Macro) ---
            if len(sents) > self.b_sent:
                excess = len(sents) - self.b_sent
                locus = self.b_sent - 1
                start = max(0, locus - excess)

                start_char = p_start + sents[start][0]
                locus_char = p_start + sents[locus][0]
                end_char = p_start + sents[-1][1] - 1

                self.apply_wave(start_char, locus_char, end_char, tier=3)

            # --- Tier 2 (Word/Mid) ---
            for s_start, s_end in sents:
                s_start_glob = p_start + s_start
                s_end_glob = p_start + s_end - 1
                sent_text = self.text[s_start_glob:s_end_glob + 1]
                words = [(m.start(), m.end() - 1) for m in re.finditer(r'[a-zA-Z]+', sent_text)]

                if len(words) > self.b_word:
                    excess = len(words) - self.b_word
                    locus = self.b_word - 1
                    start = max(0, locus - excess)

                    start_char = s_start_glob + words[start][0]
                    locus_char = s_start_glob + words[locus][0]
                    end_char = s_start_glob + words[-1][1]

                    self.apply_wave(start_char, locus_char, end_char, tier=2)

                # --- Tier 1 (Syllable/Micro) ---
                for w_start, w_end in words:
                    w_start_glob = s_start_glob + w_start
                    w_end_glob = s_start_glob + w_end
                    word_text = self.text[w_start_glob:w_end_glob + 1]

                    syls = dic.inserted(word_text).split('-')
                    if len(syls) > self.b_syl:
                        excess = len(syls) - self.b_syl
                        locus = self.b_syl - 1
                        start = max(0, locus - excess)

                        syl_spans = []
                        curr = 0
                        for syl in syls:
                            syl_spans.append((curr, curr + len(syl) - 1))
                            curr += len(syl)

                        start_char = w_start_glob + syl_spans[start][0]
                        locus_char = w_start_glob + syl_spans[locus][0]
                        end_char = w_start_glob + syl_spans[-1][1]

                        self.apply_wave(start_char, locus_char, end_char, tier=1)

        return self.char_map


# ------------------------------------------------------------------------
# Lazy Multi-Page PIL Sequence for Direct PDF Streaming
# ------------------------------------------------------------------------
class LazyPageSequence(Image.Image):
    """
    Streams PIL page images into Pillow's PDF writer one frame at a time
    so the entire volume never has to reside in memory simultaneously.
    """
    def __init__(self, cover_img, schematic_pages, render_page_fn):
        super().__init__()
        self._cover_img = cover_img.convert("RGB")
        self._pages = schematic_pages
        self._render_page_fn = render_page_fn
        self.n_frames = 1 + len(schematic_pages)
        self._current_frame = -1
        self.seek(0)

    def seek(self, frame: int):
        if frame < 0 or frame >= self.n_frames:
            raise EOFError("End of page sequence")
        if frame == self._current_frame:
            return
        self._current_frame = frame
        if frame == 0:
            img = self._cover_img
        else:
            img = self._render_page_fn(frame - 1, self._pages[frame - 1])
        self.im = img.im
        self._mode = img.mode
        self._size = img.size
        self.info = img.info.copy()

    def tell(self) -> int:
        return self._current_frame

    def load(self):
        return super().load()


# ------------------------------------------------------------------------
# PDF Renderer (Schematic Layout & Print Output)
# ------------------------------------------------------------------------
class PDFRenderer:
    def __init__(self, char_map, pdf_path, title_str, callback):
        self.char_map = char_map
        self.pdf_path = pdf_path
        self.title_str = title_str
        self.callback = callback

        self.width = 1080
        self.height = 1440
        self.margin_x = 90
        self.margin_y = 160
        self.line_height = 42

        self.script_dir = Path(__file__).parent
        self.bask_path = str(self.script_dir / "baskerville.ttf")
        self.gwen_path = str(self.script_dir / "gwendolyn.ttf")
        self.setup_fonts()

    def setup_fonts(self):
        try:
            self.base_font = ImageFont.truetype(self.bask_path, 26)
            self.rewild_font = ImageFont.truetype(self.gwen_path, 32)
            self.base_drop_font = ImageFont.truetype(self.bask_path, 160)
            self.rewild_drop_font = ImageFont.truetype(self.gwen_path, 160)
            self.fonts_loaded = True
        except IOError:
            print("Warning: Custom TTF files not found. Using system defaults.")
            self.base_font = ImageFont.load_default()
            self.rewild_font = ImageFont.load_default()
            self.base_drop_font = ImageFont.load_default()
            self.rewild_drop_font = ImageFont.load_default()
            self.fonts_loaded = False

    def get_text_size(self, text, font):
        if hasattr(font, 'getlength'):
            return font.getlength(text)
        return len(text) * 12

    def generate_cover(self):
        cover_w, cover_h = self.width, self.height
        cover_img = Image.new('RGB', (cover_w, cover_h))

        space_color = (5, 5, 15)
        earth_color = (45, 60, 35)
        cloud_color = (220, 220, 220)

        draw_bg = ImageDraw.Draw(cover_img)
        for y in range(cover_h):
            ratio = y / cover_h
            r = int(space_color[0] * (1 - ratio) + earth_color[0] * ratio)
            g = int(space_color[1] * (1 - ratio) + earth_color[1] * ratio)
            b = int(space_color[2] * (1 - ratio) + earth_color[2] * ratio)
            draw_bg.line([(0, y), (cover_w, y)], fill=(r, g, b))

        lines = self.title_str.split('\n')
        txt_layer = Image.new('RGBA', (cover_w, cover_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)

        line_step = 150
        total_block_h = max(0, (len(lines) - 1) * line_step)
        y_cursor = max(240, int((cover_h - total_block_h) / 2))
        max_font_size = 120

        for line_idx, line in enumerate(lines):
            if line_idx % 2 == 0:
                start_human_scalar = 0.75
                start_nonhuman_scalar = 0.25
            else:
                start_human_scalar = 0.25
                start_nonhuman_scalar = 0.75

            char_count = max(1, len(line) - 1)
            total_w = 0
            char_measurements = []

            for c_idx, char in enumerate(line):
                prog = c_idx / char_count if char_count > 0 else 0

                if line_idx % 2 == 0:
                    h_scalar = start_human_scalar - (0.50 * prog)
                    nh_scalar = start_nonhuman_scalar + (0.50 * prog)
                else:
                    h_scalar = start_human_scalar + (0.50 * prog)
                    nh_scalar = start_nonhuman_scalar - (0.50 * prog)

                h_size = int(max_font_size * h_scalar)
                nh_size = int(max_font_size * nh_scalar)
                h_alpha = int(255 * h_scalar)
                nh_alpha = int(255 * nh_scalar)

                try:
                    h_fnt = ImageFont.truetype(self.bask_path, max(10, h_size))
                    nh_fnt = ImageFont.truetype(self.gwen_path, max(10, nh_size))
                except IOError:
                    h_fnt = ImageFont.load_default()
                    nh_fnt = ImageFont.load_default()

                w_h = h_fnt.getlength(char) if hasattr(h_fnt, 'getlength') else 12
                w_nh = nh_fnt.getlength(char) if hasattr(nh_fnt, 'getlength') else 12
                step_w = max(w_h, w_nh)

                char_measurements.append({
                    'char': char,
                    'step_w': step_w,
                    'h_fnt': h_fnt,
                    'nh_fnt': nh_fnt,
                    'h_alpha': h_alpha,
                    'nh_alpha': nh_alpha
                })
                total_w += step_w

            x_cursor = (cover_w - total_w) / 2

            for cm in char_measurements:
                draw.text(
                    (x_cursor + (cm['step_w'] / 2), y_cursor),
                    cm['char'],
                    font=cm['h_fnt'],
                    fill=(cloud_color[0], cloud_color[1], cloud_color[2], cm['h_alpha']),
                    anchor="mm"
                )
                draw.text(
                    (x_cursor + (cm['step_w'] / 2), y_cursor),
                    cm['char'],
                    font=cm['nh_fnt'],
                    fill=(cloud_color[0], cloud_color[1], cloud_color[2], cm['nh_alpha']),
                    anchor="mm"
                )
                x_cursor += cm['step_w']

            y_cursor += line_step

        cover_img.paste(txt_layer, (0, 0), txt_layer)
        return cover_img

    def _segment_word_runs(self, word_slice, is_first_char):
        """
        Splits a token slice into contiguous same-font runs so kerning pairs
        are measured and drawn across unbroken human or nonhuman substrings.
        """
        runs = []
        curr_chars = []
        curr_style = None

        for w_cm in word_slice:
            if is_first_char and w_cm['orig'].isalpha():
                if curr_chars:
                    runs.append((curr_style, curr_chars))
                    curr_chars = []
                w_cm['type'] = 'drop'
                runs.append(('drop', [w_cm]))
                is_first_char = False
            else:
                w_cm['type'] = 'base'
                style = 'rewild' if w_cm['is_locus'] else 'base'
                if style != curr_style and curr_chars:
                    runs.append((curr_style, curr_chars))
                    curr_chars = []
                curr_style = style
                curr_chars.append(w_cm)

        if curr_chars:
            runs.append((curr_style, curr_chars))

        return runs, is_first_char

    def _measure_run(self, style, chars):
        text = "".join(c['char'] for c in chars)
        if style == 'drop':
            return self.get_text_size(text, self.rewild_drop_font) + 10
        font = self.rewild_font if style == 'rewild' else self.base_font
        return self.get_text_size(text, font)

    def layout_pages(self):
        pages = []
        current_page = []
        x, y = self.margin_x, self.margin_y
        max_x = self.width - self.margin_x

        def advance_line(curr_y, curr_page):
            new_y = curr_y + self.line_height
            if new_y + self.line_height > self.height - 90:
                if curr_page:
                    pages.append(curr_page)
                return self.margin_x, self.margin_y, []
            return self.margin_x, new_y, curr_page

        is_first_char = True
        idx = 0
        total_chars = len(self.char_map)
        start_time = time.time()

        while idx < total_chars:
            if idx % 1000 == 0 and idx > 0:
                prog = idx / total_chars
                rem = ((time.time() - start_time) / prog) - (time.time() - start_time)
                m, s = divmod(int(rem), 60)
                self.callback(f"Mapping Schematic... ({idx}/{total_chars})", prog * 100, f"ETA: {m}m {s}s")

            cm = self.char_map[idx]
            cm['type'] = 'base'

            if cm['char'] == '\n':
                y += self.line_height
                if idx < total_chars - 1 and self.char_map[idx + 1]['char'] == '\n':
                    y += self.line_height * 0.5
                    idx += 1
                x = self.margin_x

                if y + self.line_height > self.height - 90:
                    if current_page:
                        pages.append(current_page)
                        current_page = []
                    x, y = self.margin_x, self.margin_y

                idx += 1
                continue

            if cm['char'].isspace():
                w = self.get_text_size(" ", self.base_font)
                if x + w > max_x:
                    x, y, current_page = advance_line(y, current_page)

                current_page.append({
                    'text': " ",
                    'x': x,
                    'y': y,
                    'style': 'space'
                })
                x += w
                idx += 1
                continue

            # Scan up to next whitespace or wrap-eligible hyphen boundary
            word_len = 0
            while idx + word_len < total_chars:
                c = self.char_map[idx + word_len]['char']
                if c == '\n' or c.isspace():
                    break
                word_len += 1
                if c == '-' and (idx + word_len >= total_chars or self.char_map[idx + word_len]['char'] != '-'):
                    break

            word_slice = [self.char_map[i] for i in range(idx, idx + word_len)]
            has_drop = is_first_char and any(c['orig'].isalpha() for c in word_slice)
            runs, is_first_char = self._segment_word_runs(word_slice, is_first_char)

            if has_drop:
                for style, chars in runs:
                    run_w = self._measure_run(style, chars)
                    if style == 'drop':
                        if x + run_w > max_x:
                            x, y, current_page = advance_line(y, current_page)

                        y += 134
                        for item in current_page:
                            if item['y'] == y - 134:
                                item['y'] = y

                    current_page.append({
                        'text': "".join(c['char'] for c in chars),
                        'x': x,
                        'y': y,
                        'style': style
                    })
                    x += run_w
            else:
                word_w = sum(self._measure_run(style, chars) for style, chars in runs)
                if x + word_w > max_x and x > self.margin_x:
                    x, y, current_page = advance_line(y, current_page)

                for style, chars in runs:
                    run_w = self._measure_run(style, chars)
                    if x + run_w <= max_x:
                        current_page.append({
                            'text': "".join(c['char'] for c in chars),
                            'x': x,
                            'y': y,
                            'style': style
                        })
                        x += run_w
                    else:
                        # Split any oversized continuous vocalization segment cleanly at the right margin
                        chunk = []
                        for ch_cm in chars:
                            test_w = self._measure_run(style, chunk + [ch_cm])
                            if x + test_w > max_x and chunk:
                                current_page.append({
                                    'text': "".join(c['char'] for c in chunk),
                                    'x': x,
                                    'y': y,
                                    'style': style
                                })
                                x, y, current_page = advance_line(y, current_page)
                                chunk = [ch_cm]
                            else:
                                chunk.append(ch_cm)
                        if chunk:
                            cw = self._measure_run(style, chunk)
                            current_page.append({
                                'text': "".join(c['char'] for c in chunk),
                                'x': x,
                                'y': y,
                                'style': style
                            })
                            x += cw

            idx += word_len

        if current_page:
            pages.append(current_page)

        return pages

    def render_page_image(self, page_idx, page, total_pages, start_time):
        prog = (page_idx + 1) / max(1, total_pages)
        elapsed = time.time() - start_time
        rem = ((elapsed / prog) - elapsed) if prog > 0 else 0
        m, s = divmod(int(rem), 60)
        self.callback(
            f"Typesetting PDF (Page {page_idx + 1}/{total_pages})...",
            prog * 100,
            f"ETA: {m}m {s}s"
        )

        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)

        for item in page:
            style = item['style']
            if style == 'space':
                continue
            elif style == 'drop':
                font = self.rewild_drop_font
            elif style == 'rewild':
                font = self.rewild_font
            else:
                font = self.base_font

            baseline_y = item['y'] + 26
            draw.text((item['x'], baseline_y), item['text'], font=font, fill='black', anchor="ls")

        return img

    def render_pdf(self, schematic_pages):
        cover_img = self.generate_cover()
        total_pages = len(schematic_pages)
        start_time = time.time()

        seq = LazyPageSequence(
            cover_img,
            schematic_pages,
            lambda idx, page: self.render_page_image(idx, page, total_pages, start_time)
        )
        seq.save(self.pdf_path, "PDF", resolution=72.0, save_all=True, quality=95)

    def process(self):
        self.callback("Calculating strict geometric map...", 0, "ETA: --")
        schematic_pages = self.layout_pages()

        self.callback("Typesetting print-ready PDF...", 0, "ETA: --")
        self.render_pdf(schematic_pages)
        self.callback(f"PDF output complete! ({self.pdf_path})", 100, "Done")


# ------------------------------------------------------------------------
# Application GUI
# ------------------------------------------------------------------------
class RewildingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NaNoGenMo 2026 - Linguistic Rewilding")
        self.geometry("600x420")

        self.corpus = load_animal_corpus()

        ttk.Label(self, text="Select Source Volume to Process:").pack(pady=(20, 10))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        self.vol1_btn = ttk.Button(btn_frame, text="Zoonomia Volume I", command=lambda: self.run_pipeline(1))
        self.vol1_btn.pack(side=tk.LEFT, padx=10)

        self.vol2_btn = ttk.Button(btn_frame, text="Zoonomia Volume II", command=lambda: self.run_pipeline(2))
        self.vol2_btn.pack(side=tk.LEFT, padx=10)

        self.stats_frame = ttk.Frame(self)
        self.stats_var = tk.StringVar(value="")
        ttk.Label(self.stats_frame, textvariable=self.stats_var, font=("Helvetica", 10, "italic")).pack(pady=10)

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(fill="x", padx=20, side=tk.BOTTOM, pady=20)

        self.status = tk.StringVar(value="Ready to rewild.")
        ttk.Label(self.progress_frame, textvariable=self.status).pack(pady=2)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=2)

        self.eta_var = tk.StringVar(value="")
        ttk.Label(self.progress_frame, textvariable=self.eta_var).pack(pady=2)

    def find_boundary(self, text, hint, start_pos=0):
        if not hint:
            return -1, -1
        pattern = r'\s+'.join(re.escape(word) for word in hint.split())
        match = re.search(pattern, text[start_pos:])
        if match:
            return start_pos + match.start(), start_pos + match.end()
        return -1, -1

    def run_pipeline(self, volume):
        if volume == 1:
            filename = "Zoonomia.txt"
            title_str = "ZOONOMIA\na\n(gesture toward)\nlinguistic rewilding;\nor,\nthe Laws of Organic Life"
            start_str = "*       *       *       *       *\n\nZOONOMIA.\n\n*       *       *       *       *"
            end_str = (
                "*       *       *       *       *\n\n"
                "  Dum, Liber! astra petis volitans trepidantibus alis,\n"
                "    Irruis immemori, parvula gutta, mari.\n"
                "  Me quoque, me currente rotâ revolubilis ætas\n"
                "    Volverit in tenebras,--i, Liber, ipse sequor.\n\n"
                "*       *       *       *       *"
            )
        else:
            filename = "Zoonomia2.txt"
            title_str = "ZOONOMIA VOLUME II\na\n(gesture toward)\nlinguistic rewilding;\nor,\nthe Laws of Organic Life"
            start_str = "CLASS I.\n\nDISEASES OF IRRITATION.\n\nORDO I."
            end_str = (
                "*       *       *       *       *\n\n"
                "  The work is done!--nor Folly's active rage,\n"
                "  Nor Envy's self, shall blot the golden page;\n"
                "  Time shall admire, his mellowing touch employ,\n"
                "  And mend the immortal tablet, not destroy.\n\n"
                "*       *       *       *       *"
            )

        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Cannot find hardcoded file: {filename}")
            return

        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            full_text = f.read()

        start_match_start, _ = self.find_boundary(full_text, start_str)
        if start_match_start == -1:
            print(f"Warning: Start string not strictly found for Volume {volume}. Processing from index 0.")
            start_idx = 0
        else:
            start_idx = start_match_start

        _, end_match_end = self.find_boundary(full_text, end_str, start_pos=start_idx)
        if end_match_end == -1:
            print(f"Warning: End string not strictly found for Volume {volume}. Processing to EOF.")
            end_idx = len(full_text)
        else:
            end_idx = end_match_end

        original_text = full_text[start_idx:end_idx]

        replacements = {'“': '"', '”': '"', '‘': "'", '’': "'", '—': '-', '–': '-', '…': '...'}
        for k, v in replacements.items():
            original_text = original_text.replace(k, v)

        original_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', original_text)

        self.vol1_btn.config(state=tk.DISABLED)
        self.vol2_btn.config(state=tk.DISABLED)
        self.status.set("Calculating dynamic structural averages...")
        self.update()

        base_syl, base_words, base_sents = calculate_dynamic_averages(original_text)

        msg = (
            f"Dynamic Calculation Complete.\n\n"
            f"Max Syllables per Word: {base_syl}\n"
            f"Max Words per Sentence: {base_words}\n"
            f"Max Sentences per Paragraph: {base_sents}\n\n"
            f"Do you want to proceed with these translation thresholds?"
        )

        if not messagebox.askyesno("Confirm Thresholds", msg):
            self.vol1_btn.config(state=tk.NORMAL)
            self.vol2_btn.config(state=tk.NORMAL)
            self.status.set("Ready to rewild.")
            return

        self.stats_var.set(
            f"Active Thresholds:\nMax Syl/Word: {base_syl} | Max Words/Sent: {base_words} | Max Sents/Para: {base_sents}"
        )
        self.stats_frame.pack(before=self.progress_frame)

        threading.Thread(
            target=self.process_threaded,
            args=(filename, original_text, base_syl, base_words, base_sents, title_str),
            daemon=True
        ).start()

    def _safe_update_ui(self, msg, progress, eta):
        self.status.set(msg)
        if progress is not None:
            self.progress_var.set(progress)
        if eta is not None:
            self.eta_var.set(eta)

    def process_threaded(self, filepath, original_text, base_syl, base_words, base_sents, title_str):
        try:
            self.after(0, lambda: self._safe_update_ui("Compiling Z-Axis Deep Map...", 0, ""))
            engine = DeepMapEngine(original_text, self.corpus, base_syl, base_words, base_sents)
            char_map = engine.build()

            rewilded_text = "".join(entry["char"] for entry in char_map)
            base_name = os.path.splitext(filepath)[0]
            txt_path = f"{base_name}_rewilded.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(rewilded_text)

            src_ws = len(original_text.split())
            src_alpha = len(re.findall(r"[a-zA-Z]+", original_text))
            rew_ws = len(rewilded_text.split())
            rew_alpha = len(re.findall(r"[a-zA-Z]+", rewilded_text))

            print(f"Saved rewilded text to: {txt_path}")
            print(f"Source   -> whitespace: {src_ws:,} | [a-zA-Z]+: {src_alpha:,}")
            print(f"Rewilded -> whitespace: {rew_ws:,} | [a-zA-Z]+: {rew_alpha:,}")

            renderer = PDFRenderer(
                char_map,
                f"{base_name}_rewilded.pdf",
                title_str,
                lambda msg, prog=None, eta=None: self.after(
                    0, lambda m=msg, p=prog, e=eta: self._safe_update_ui(m, p, e)
                )
            )
            renderer.process()

        except Exception as e:
            traceback.print_exc()
            error_msg = f"Error: {str(e)}"
            self.after(0, lambda m=error_msg: self._safe_update_ui(m, 0, ""))
        finally:
            self.after(0, lambda: self.vol1_btn.config(state=tk.NORMAL))
            self.after(0, lambda: self.vol2_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    app = RewildingApp()
    app.mainloop()
