# QuranInBangla — Project Context for Claude Code

This file gives Claude Code the full context of this project so it can assist
without needing repeated explanations.

---

## Project Overview

A web application that assists a Quran researcher in translating the entire
Quran into Bangla. The software does NOT auto-translate — the client does all
translation manually. The system stores, organizes, and presents his work.

The client has been researching Bangla Quran translations for 10 years and has
found serious errors in existing translations. He wants to produce his own
correct Bangla translation.

**Current phase:** Private research/translation tool (single user).
**Future phase:** Public website + PDF export of the completed translation.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django + Django REST Framework |
| Database | PostgreSQL |
| Frontend (dashboard) | React + Vite |
| CSS Framework (dashboard) | Tailwind CSS v4 (`@tailwindcss/vite` plugin) |
| Frontend (public site, future) | Next.js |
| Authentication | JWT (`djangorestframework-simplejwt`), single admin user |
| PDF Generation | WeasyPrint |
| Arabic source data | Quran Foundation API (one-time fetch, cached in DB) |

---

## Target Device

The client uses the dashboard on a **laptop only** — not a phone, not an
ultra-wide desktop monitor. Design and test primarily for laptop viewports
(~1366px–1920px wide, the common 13"–15" laptop range). Layouts must not
break/overflow at these sizes. Mobile-first responsiveness is explicitly
NOT a v1 priority — don't spend effort on phone breakpoints for the
dashboard. (The future public site, being public-facing, will need real
responsive design — this constraint applies to the admin dashboard only.)

---

## Authentication

JWT via `djangorestframework-simplejwt` — NOT DRF `TokenAuthentication`.
Client sends the access token as a `Bearer` token in the `Authorization`
header.

```python
# settings — djangorestframework-simplejwt
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

`BLACKLIST_AFTER_ROTATION=True` requires the
`rest_framework_simplejwt.token_blacklist` app enabled with its migrations
run. Single admin user only — see "What NOT to do" below.

---

## Folder Structure

```
QuranInBangla/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── quran/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   ├── migrations/
│   │   │   ├── services/
│   │   │   │   ├── quran_api_client.py
│   │   │   │   └── text_normalizer.py
│   │   │   └── management/commands/
│   │   │       ├── import_surahs.py
│   │   │       ├── import_rukus.py
│   │   │       ├── import_ayahs_and_words.py
│   │   │       ├── audit_word_marks.py
│   │   │       └── verify_data_integrity.py
│   │   └── accounts/
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── manage.py
│   └── .env
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── context/
└── docs/
    ├── feature-list.md
    └── schema.dbml
```

---

## Database Schema

### `surah`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| number | integer unique | 1–114 |
| name_arabic | text | |
| name_bangla | text | |
| name_english | text | |
| total_ayah | integer | |

### `ruku`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| ruku_number | integer unique | Global 1–558 |
| surah_id | FK → surah | |
| surah_ruku_number | integer | Position within surah (R1, R2...) |
| first_verse_id | integer | From API |
| last_verse_id | integer | From API |
| verses_count | integer | |

### `ayah`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| surah_id | FK → surah | |
| ruku_id | FK → ruku | nullable |
| ayah_number | integer | Within surah |
| verse_key | varchar(10) unique | e.g. "2:255" |
| arabic_text | text | Uthmani script, from API, never modified — includes waqf signs etc. as-is |
| translation_text | text | Client's manual Bangla translation |
| notes | text | Per-ayah free note |
| status | varchar(10) | 'draft' or 'final' |
| created_at | timestamp | |
| updated_at | timestamp | |

### `word`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| arabic_text | text unique | **Canonical form**, NOT raw API text. Quranic annotation marks (waqf signs, rub-el-hizb, sajdah marker, silent-letter marks — U+06D6–U+06ED) are stripped, and the result is NFC-normalized. Exact match on this canonical form (e.g. `eat` ≠ `eats` ≠ `eating`, different harakat/case endings ARE different words) — see "Word `arabic_text` canonicalization" below |
| normalized_text | text | Diacritics-stripped (harakat + tashkeel + annotations), auto-generated for search |
| is_meaning_final | boolean | default false — for progress tracking only, not a lock |
| created_at | timestamp | |
| updated_at | timestamp | |

### `word_meaning`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| word_id | FK → word | |
| meaning_text | text | e.g. "আমি" or "মুই" |
| is_default | boolean | First meaning added = true; others = false |

### `word_occurrence`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| ayah_id | FK → ayah | |
| word_id | FK → word | |
| position | integer | Order of word within the ayah |
| raw_text | text | **Exact text as it appears at this specific position** — including any waqf sign, rub-el-hizb marker, or silent-letter mark. `word.arabic_text` is the cleaned canonical form (identity/meaning/note linking); this field is what word-by-word display should render, so nothing is lost visually |
| meaning_id | FK → word_meaning | nullable until client assigns first meaning |

unique_together: (ayah_id, position)

### `word_note`
One-to-one with `word`. All fields are optional text fields.

| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| word_id | FK → word unique | one-to-one |
| root | text | Arabic root |
| meaning_basra | text | Meaning per Basra grammar school |
| meaning_kufa | text | Meaning per Kufa grammar school |
| meaning_baghdad | text | Meaning per Baghdad grammar school |
| pattern | text | Morphological pattern |
| note_for_pattern | text | Free note explaining the pattern |
| grammatical_information | text | Free-text grammatical info (POS, verb form, etc.) |
| derived_forms | jsonb | List of strings, e.g. `["يَكْتُبُ", "كَاتِب"]` |
| notes | text | Large free-text, up to 1–2 pages |
| updated_at | timestamp | |

### `activity_log`
Powers the dashboard's "Recent Activity" feed. NOT a version/content-diff
history — see "No version/edit history" below.

| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| user_id | FK → user | |
| action_type | varchar(30) | `ayah_translated` / `ayah_updated` / `word_meaning_added` / `word_meaning_updated` |
| ayah_id | FK → ayah | nullable — set for ayah-related actions |
| word_id | FK → word | nullable — set for word-related actions, and optionally alongside `ayah_id` when the word action happened in the context of a specific ayah (e.g. editing a word meaning from within an ayah view) |
| created_at | timestamp | |

For `ayah_translated` / `ayah_updated`, only `ayah_id` is set. For
`word_meaning_added` / `word_meaning_updated`, `word_id` is always set, and
`ayah_id` is set too whenever the action happened in the context of a
specific ayah — so both can be non-null together. Not mutually exclusive;
no DB constraint enforces "exactly one."

---

## Key Design Decisions

### Word uniqueness
`eat`, `eats`, `eating` are stored as 3 separate unique `word` rows.
No lemmatization or root-based merging. Different harakat/case endings are
different words on purpose.

### Word `arabic_text` canonicalization
`word.arabic_text` is a **cleaned, canonical** form — not the raw text the
API returns for that word position. Two things happen to the raw API text
before it becomes `word.arabic_text`:

1. **Strip Quranic annotation marks** (`strip_quranic_annotations()` in
   `text_normalizer.py`) — waqf/pause signs, the rub-el-hizb marker, the
   sajdah marker, and silent-letter/madd recitation marks (Unicode
   U+06D6–U+06ED) are removed. These marks are positional/contextual (they
   land on some occurrences of a word but not others), so leaving them in
   `arabic_text` would fork one lexical word into multiple `word` rows and
   break meaning defaulting, `word_note` sharing, and progress tracking.
   Standard harakat/tashkeel (U+064B–U+065F) are NOT touched — they stay,
   since different harakat are meaningfully different words here.
2. **NFC-normalize** (`unicodedata.normalize('NFC', ...)`) — the Quran
   Foundation API doesn't always send the same word in the same Unicode
   normalization form (precomposed vs. decomposed, e.g. `آ` as one
   codepoint vs. `ا` + a combining madda). Without this, the same visual
   word could exist as two different `unique` rows. Normalization MUST
   happen again *after* stripping annotation marks, not only before —
   removing a mark that sits between two combining diacritics can change
   what NFC's canonical ordering considers "adjacent," so a stripped string
   isn't guaranteed to still be in canonical form. `Word.save()` re-applies
   NFC as a safety net on every save regardless of call site.

The **exact original text** (marks included, whatever form the API sent)
is preserved per-occurrence in `word_occurrence.raw_text` — this is what
the frontend renders for word-by-word display, so nothing is lost visually
even though `word.arabic_text` is cleaned.

Two read-only management commands support this: `audit_word_marks` (scans
`word.arabic_text` for any leftover non-standard character) and
`verify_data_integrity` (checks NFC duplicate groups, `raw_text` ↔
`arabic_text` consistency, empty words, and per-ayah position-sequence
gaps). Run both after any fresh import.

### Word meaning: default + override
- First meaning given to a word → `is_default = true` in `word_meaning`.
- All existing `word_occurrence` rows for that word get `meaning_id` set to
  this default meaning immediately on creation.
- If the client later wants a different meaning in a specific ayah,
  he updates that single `word_occurrence.meaning_id` to point to another
  `word_meaning` row.
- No bulk selection or group assignment — always one occurrence at a time.
- `word.is_meaning_final` is a progress flag only. It does NOT lock or prevent
  future overrides.

### normalized_text vs. arabic_text — two different normalizer functions
`apps/quran/services/text_normalizer.py` has two functions, used for two
different purposes — do not conflate them:

- `strip_diacritics()` — full strip: tashkeel/harakat (U+064B–U+065F),
  tatweel, AND Quranic annotation marks (U+06D6–U+06ED). Used ONLY for
  `word.normalized_text`, which powers diacritics-insensitive search.
- `strip_quranic_annotations()` — narrower strip: ONLY Quranic annotation
  marks (U+06D6–U+06ED) and stray control characters (e.g. U+200F).
  Harakat/tashkeel are kept. Used to compute the canonical `word.arabic_text`
  (see above) — harakat differences must be preserved here since they're
  meaningfully different words, unlike for search.

### Ayah arabic_text
Stored as-is from Quran Foundation API (Uthmani script). Never reconstructed
from word occurrences. This is the source of truth for display. Unlike
`word.arabic_text`, this is NEVER cleaned/stripped/normalized.

### No version/edit history
No changelog or content-diff/version history. Overwriting `translation_text`,
`meaning_text`, `word_note` fields etc. is fine — old values are not
retained and cannot be reverted to.

**Exception:** `activity_log` exists to power the dashboard's Recent
Activity feed. It is NOT a version/diff history — it stores only lightweight
action metadata (who, what type of action, when, which ayah/word), never
old/new field values, and offers no revert capability. See "Activity
logging" below.

### Activity logging
- A row is created ONLY on an explicit Save action — never on autosave.
- Created in the DRF view layer (`perform_update()` / `perform_create()`),
  not via model `save()` overrides or signals, because `request.user` is
  needed and isn't reliably available at the model layer.
- Four `action_type` values, one pair per content type, split on
  first-time vs. edited-again:
  - `ayah_translated` — `translation_text`/`notes` went from empty to
    filled for the first time.
  - `ayah_updated` — `translation_text`/`notes` already had content and
    was edited again.
  - `word_meaning_added` — the first `word_meaning` ever created for that
    word (mirrors the `is_first_meaning` check already in
    `WordMeaning.save()`).
  - `word_meaning_updated` — an existing meaning was edited, or an
    additional (non-first) meaning was added to a word that already had one.
- Clicking an activity item in the dashboard navigates to the relevant
  ayah or word page (frontend derives the route from `ayah_id`/`word_id`
  in the API response, e.g. via `ayah.verse_key` or `word.arabic_text`).

### No multi-ayah context notes
Only per-ayah notes (single `ayah.notes` field). No cross-ayah grouping.

---

## Data Import (one-time setup, run in order)

```bash
python manage.py import_surahs        # fetches 114 surahs
python manage.py import_rukus         # fetches 558 rukus (needs surahs first)
python manage.py import_ayahs_and_words  # fetches all ayahs + word-by-word breakdown
```

All import logic lives in:
- `apps/quran/services/quran_api_client.py` — API calls, OAuth token handling
- `apps/quran/management/commands/` — Django management commands

Use `get_or_create()` to make commands safely re-runnable.

`import_ayahs_and_words` computes `word_occurrence.raw_text` (NFC-normalized,
marks intact) and `word.arabic_text` (NFC-normalized, marks stripped) from
the same API segment text — see "Word `arabic_text` canonicalization" above
before touching this command.

After any fresh/re-import, run:
```bash
python manage.py audit_word_marks
python manage.py verify_data_integrity
```
Both are read-only and should report zero issues.

---

## Features (v1)

1. **Surah & Ruku list** — browse by surah or ruku
2. **Ayah view** — arabic text + word-by-word meanings + full translation
3. **Word meaning input** — first meaning = default for all occurrences
4. **Word meaning override** — change meaning for a specific occurrence
5. **Word notes** — grammar fields per word (root, POS, morphology, etc.)
6. **Ayah translation** — manual full Bangla translation with draft autosave
7. **Ayah notes** — free text note per ayah
8. **Final status** — mark ayah or word meaning as final for progress tracking
9. **Search** — surah search + word search (diacritics-insensitive)
10. **Word search result** — list of all ayahs containing a searched word
11. **Progress dashboard** — ayah translation progress + word meaning progress
12. **PDF export** — per-surah PDF (future)
13. **Public website** — read-only view of ayah + word meanings + translation (future)
14. **Recent Activity feed** — dashboard shows a live feed of recent ayah/word
    edits (see `activity_log` and "Activity logging" above); clicking an
    entry navigates to that ayah's or word's page

---

## Quran Foundation API

- Base URL: https://api.quran.foundation
- Auth: OAuth2 client_credentials (token valid 1 hour)
- Credentials stored in `.env` as `QURAN_API_CLIENT_ID` and `QURAN_API_CLIENT_SECRET`
- Key endpoints:
  - `/chapters` — list of 114 surahs
  - `/resources/rukus` — list of 558 rukus
  - `/verses/by_chapter/{chapter_number}` — ayahs with word-by-word data
  - Use `fields=text_uthmani,words` to get arabic text + words in one call
- Recitation/riwayah: **Hafs 'an Asim** (NOT Warsh) — the globally standard
  riwayah (Middle East, South Asia including Bangladesh, Southeast Asia,
  and virtually all major Quran platforms including Quran.com/Quran
  Foundation). Warsh (used mainly in North/West Africa) has a genuinely
  different Rasm/text and would be explicitly labeled as such — this API
  isn't, and `text_uthmani` follows standard Hafs Uthmani orthography.

---

## Fonts

### Arabic / Quranic text — QPC Hafs
- **QPC Hafs** (King Fahd Glorious Quran Printing Complex's official
  Unicode Uthmani Hafs font) — sourced from QUL:
  https://qul.tarteel.ai/resources/font/245
- Unicode-based — matches `ayah.arabic_text` / `word.arabic_text` (from
  Quran Foundation API's `text_uthmani`) directly. No glyph-substitution
  or special codepoint mapping needed.
- Not on Google Fonts — self-host the TTF/WOFF2 files. QUL's download
  button is JS-driven (no static file URL), so it can't be fetched
  headlessly/programmatically — must be downloaded manually via the
  browser.
- Self-hosted at `frontend/public/fonts/UthmanicHafs_V22.{woff2,ttf}`,
  wired up as the `QPC Hafs` font-family in `frontend/src/index.css`
  (Tailwind theme token `--font-arabic`).

### English UI text — Inter
- **Inter** (Google Fonts) — primary font for Latin/English text (brand
  name, labels that mix in English, numerals).

### Bangla UI text — Noto Sans Bengali
- **Noto Sans Bengali** (Google Fonts) — primary font for all Bangla UI
  text (dashboard chrome, buttons, labels) and Bangla translation body
  text. Loads from the Google Fonts CDN — no self-hosting needed.
- Combined stack: `--font-sans: "Inter", "Noto Sans Bengali", "Kalpurush",
  system-ui, sans-serif` in `frontend/src/index.css` — the browser renders
  Latin glyphs in Inter and falls through to Noto Sans Bengali for Bengali
  glyphs automatically, so UI text doesn't need per-element font classing.
- Kalpurush is kept self-hosted at `frontend/public/fonts/kalpurush.ttf`
  as a trailing fallback (in case Noto Sans Bengali is missing a glyph)
  but is no longer the primary Bangla font — an earlier decision (Kalpurush
  primary) was reversed since Noto Sans Bengali reads cleaner in the
  actual UI at dashboard chrome sizes.
- Rejected: Hind Siliguri — on Google Fonts and tagged "Bengali," but
  it's designed for the Indian/Hindi-adjacent market, not a
  Bangladeshi-origin typeface.
- **License note (Kalpurush, fallback only):** CC BY-NC-SA 3.0
  (NonCommercial). Not a concern now since it's not the primary font, but
  worth dropping entirely if it's ever fully unused.

### IndoPak / Nastaleeq script — out of v1 scope
- v1 renders **Uthmani script only** (QPC Hafs above). No IndoPak/
  Nastaleeq font or rendering in v1.
- Reason: IndoPak-style rendering is NOT just a different font over the
  same text — it requires a genuinely different underlying Unicode text
  dataset (confirmed via QUL's own documentation, which repeats "Standard
  Quran fonts require a separate Quran script" on every IndoPak font
  page). Supporting it later means importing a second parallel text
  dataset (e.g. QUL's "Indopak (Word by Word / Ayah by Ayah)" dataset,
  tag `Hafs`) alongside the existing Uthmani data — not just adding a
  font file.
- Revisit only when/if this becomes an explicit requirement (e.g. public
  site phase).

---

## Environment Variables (.env)

```
DEBUG=True
SECRET_KEY=
DATABASE_URL=postgres://user:password@localhost:5432/qurandb
QURAN_API_CLIENT_ID=
QURAN_API_CLIENT_SECRET=
```

---

## What NOT to do

- Do NOT auto-translate any Arabic text
- Do NOT modify `ayah.arabic_text` after import
- Do NOT reconstruct ayah text from word occurrences
- Do NOT add content-diff/version history (`activity_log` is metadata-only,
  not a diff/version history — see "No version/edit history")
- Do NOT add multi-user roles (single admin only for now)
- Do NOT create `activity_log` rows on autosave — only on explicit Save
- Do NOT strip Quranic annotation marks from `ayah.arabic_text` or
  `word_occurrence.raw_text` — only `word.arabic_text` gets cleaned
- Do NOT treat "download an IndoPak font" as sufficient for IndoPak
  script support — it needs a separate IndoPak-encoded text dataset (see
  "Fonts" above)
- Do NOT use DRF `TokenAuthentication` — auth is JWT via
  `djangorestframework-simplejwt` (see "Authentication" above)
- Do NOT use Kalpurush as the primary Bangla font — Noto Sans Bengali is
  primary, Kalpurush is a trailing fallback only (see "Fonts" above)