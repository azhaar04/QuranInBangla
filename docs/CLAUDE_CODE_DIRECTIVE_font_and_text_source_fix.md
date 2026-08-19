# Directive: Switch Arabic text source to `text_qpc_hafs` + fix QPC Hafs font bug

## Context (why this change)

The QPC Hafs font (`UthmanicHafs1Ver18`, self-hosted or CDN) renders a large black
circle instead of a small mark on three Quranic-annotation codepoints
(U+06DF, U+06E3, U+06EB) when paired with the `text_uthmani` field. This was
verified via direct font inspection (fontTools/uharfbuzz) and confirmed by the
QUL/Tarteel maintainer: **QPC Hafs font is only compatible with the QPC Hafs
script (`text_qpc_hafs` field), not the Tanzil Uthmani script (`text_uthmani`
field).** We were pairing the right font with the wrong text field.

**Fix: switch the Arabic text source from `text_uthmani` to `text_qpc_hafs`**
(same Quran Foundation API, just a different field — no new external source,
no new license concern). Font stays QPC Hafs, loaded live from Quran
Foundation's own CDN (not self-hosted).

This project is still in early dev (no production data, no client-entered
word meanings/notes yet), so a full re-import is safe and preferred over any
migration/backfill logic.

---

## Final decisions (do not deviate without asking)

1. **Text source field: `text_qpc_hafs`**, not `text_uthmani`. Applies to
   BOTH ayah-level and word-level text.
2. **Font: QPC Hafs**, loaded live from Quran Foundation's CDN — do NOT
   self-host, do NOT use Scheherazade New (that was an earlier, now-reversed
   decision made before this root cause was found).
3. **Sukun handling — client-confirmed final decision: sukun stays in the
   word, it is NOT stripped.** Concretely: U+06E1 (`ARABIC SMALL HIGH
   DOTLESS HEAD OF KHAH`) is the QPC-typesetting glyph variant of sukun used
   in `text_qpc_hafs`. It numerically falls inside the Quranic-annotation
   strip range (U+06D6–U+06ED) but must be treated as a **harakat-equivalent
   mark and excluded from stripping** in `Word.arabic_text` canonicalization.
   It should still be stripped for `word.normalized_text` (search stays
   fully diacritics-insensitive — no change needed there).
4. Expected result after re-import: **unique word count ≈ 19,400** (up from
   the previous ~18,819 under `text_uthmani`). This increase is expected and
   correct — see verification section below. If the number is wildly
   different (e.g. off by thousands), stop and investigate before proceeding.

---

## File-by-file changes

### 1. `backend/apps/quran/services/text_normalizer.py`

Update `strip_quranic_annotations()` to exclude U+06E1 from the stripped
range — keep it (do not remove it), matching the "sukun stays" decision.
`strip_diacritics()` (used for `normalized_text`/search) is UNCHANGED — it
should still strip U+06E1 along with everything else, since search must stay
fully diacritics-insensitive.

```python
_ANNOTATION_START = 0x06D6
_ANNOTATION_END = 0x06ED

# QPC-typesetting sukun variant. Numerically inside the Quranic-annotation
# block above, but linguistically a harakat (marks "no vowel"), not a
# waqf/pause/rub-el-hizb/sajdah mark. Client decision: sukun must stay in
# Word.arabic_text, so this codepoint is EXCLUDED from stripping in
# strip_quranic_annotations() (kept), while strip_diacritics() (used only
# for the search-oriented normalized_text field) still strips it.
_QPC_SUKUN_VARIANT = 0x06E1

QURANIC_ANNOTATION_RANGE = '[{}-{}]'.format(chr(_ANNOTATION_START), chr(_ANNOTATION_END))
# Same range as above, but as an explicit codepoint set with the sukun
# variant excluded — used only by strip_quranic_annotations().
_ANNOTATION_CODEPOINTS_KEEPING_SUKUN = set(range(_ANNOTATION_START, _ANNOTATION_END + 1)) - {_QPC_SUKUN_VARIANT}

STRAY_CONTROL_CHARS = '[{}{}]'.format(chr(0x200E), chr(0x200F))


def strip_diacritics(text: str) -> str:
    """Full strip for normalized_text/search — UNCHANGED, still strips
    U+06E1 along with everything else in the annotation + harakat ranges."""
    text = araby.strip_tashkeel(text)
    text = araby.strip_tatweel(text)
    text = re.sub(QURANIC_ANNOTATION_RANGE, '', text)
    text = ' '.join(text.split())
    return text


def strip_quranic_annotations(text: str) -> str:
    """Computes canonical Word.arabic_text. Strips waqf/rub-el-hizb/sajdah/
    silent-letter marks, but KEEPS the QPC sukun-variant glyph (U+06E1) per
    client decision — sukun is a harakat, not a positional/contextual mark,
    and must remain part of word identity."""
    text = ''.join(ch for ch in text if ord(ch) not in _ANNOTATION_CODEPOINTS_KEEPING_SUKUN)
    text = re.sub(STRAY_CONTROL_CHARS, '', text)
    text = ' '.join(text.split())
    return text
```

The key behavioral requirement, regardless of exact code style used: strip
everything in U+06D6–U+06ED **except** U+06E1, in `strip_quranic_annotations()`
only. `strip_diacritics()` keeps stripping the full range including U+06E1.

### 2. `backend/apps/quran/services/quran_api_client.py` and
   `backend/apps/quran/management/commands/import_ayahs_and_words.py`

- Change the verse-level API request field from `text_uthmani` to
  `text_qpc_hafs`.
- Change the word-level `word_fields` parameter from `text_uthmani` to
  `text_qpc_hafs`.
- `Ayah.arabic_text` ← `text_qpc_hafs` value (verse-level), stored as-is
  (still never modified after import, per existing rule).
- `WordOccurrence.raw_text` ← `text_qpc_hafs` value (word-level), stored
  as-is.
- `Word.arabic_text` ← computed via `strip_quranic_annotations()` (updated
  version above) applied to the word-level `text_qpc_hafs` text, then NFC
  normalized (existing `Word.save()` safety net handles this already, no
  change needed there).
- **No text reversal logic needed.** (An earlier manual copy-paste from a
  browser dev tool appeared character-reversed due to how that UI copies
  RTL text — that is a UI-copy artifact only. Real API JSON responses
  fetched programmatically are in correct logical order already.)

### 3. Frontend font loading

Remove the Scheherazade New Google Fonts `<link>` and `@theme` token
(reverse the earlier change). Load QPC Hafs live from Quran Foundation's CDN
instead of self-hosting:

```css
@font-face {
  font-family: 'QPCHafs';
  src: url('https://verses.quran.foundation/fonts/quran/hafs/uthmanic_hafs/UthmanicHafs1Ver18.woff2') format('woff2'),
       url('https://verses.quran.foundation/fonts/quran/hafs/uthmanic_hafs/UthmanicHafs1Ver18.ttf') format('truetype');
  font-display: swap;
}
```

```css
@theme {
  --font-arabic: "QPCHafs", serif;
}
```

Do not self-host this font file — Quran Foundation pushes corrections to it
over time; load it live from their CDN as shown above.

### 4. Documentation

Update `CLAUDE.md` (Fonts section, Arabic subsection) and
`docs/frontend_development_plan.md` to reflect:
- Arabic font is QPC Hafs again (reverse the earlier "switch to Scheherazade
  New" edit — keep that as historical/reference context, same pattern as
  before, don't delete it).
- Arabic text source is `text_qpc_hafs`, not `text_uthmani` — update the
  "Quran Foundation API" section's field list and the "Data Import" section.
- Add a note under "Word `arabic_text` canonicalization" documenting the
  U+06E1 exception and why (sukun is a harakat, must stay; see decision #3
  above).

---

## Execution order

1. Update `text_normalizer.py` (the U+06E1 exclusion).
2. Update `quran_api_client.py` / `import_ayahs_and_words.py` (switch fields
   to `text_qpc_hafs`).
3. Wipe and re-run the full import (`import_surahs`, `import_rukus`,
   `import_ayahs_and_words`) against a dev DB — this is a fresh full
   re-import, not a migration, since no client data exists yet.
4. Run `python manage.py audit_word_marks` and
   `python manage.py verify_data_integrity` — both must report zero issues.
5. Check the resulting unique `Word` count is **≈19,400** (±small margin).
   If it's off by more than a few hundred from that, stop and report back
   before continuing — don't silently proceed on an unexpected number.
6. Update frontend font loading (CDN `@font-face`, remove Scheherazade New).
7. Manually spot-check Ayah 2:5 in the running app — the two occurrences of
   "أُوْلَٰٓئِكَ" must render with a small mark, not a black circle.
8. Update `CLAUDE.md` and `docs/frontend_development_plan.md` per the
   Documentation section above.

## Do NOT

- Do not use QUL (qul.tarteel.ai) as a data source — Quran Foundation's own
  `text_qpc_hafs` field is equivalent and is already the project's approved
  source (confirmed character-for-character identical for the ayahs
  checked).
- Do not self-host the QPC Hafs font file — load it live from Quran
  Foundation's CDN.
- Do not strip U+06E1 in `strip_quranic_annotations()` — this is the one
  explicit exception, confirmed by the client.
- Do not add any manual text-reversal/byte-order workaround in the import
  code — that issue was specific to a UI copy-paste, not the real API.
