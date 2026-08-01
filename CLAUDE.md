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
| Frontend (public site, future) | Next.js |
| Authentication | Django default auth (single admin user) |
| PDF Generation | WeasyPrint |
| Arabic source data | Quran Foundation API (one-time fetch, cached in DB) |

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
│   │   │       └── import_ayahs_and_words.py
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
| arabic_text | text | Uthmani script, from API, never modified |
| translation_text | text | Client's manual Bangla translation |
| notes | text | Per-ayah free note |
| status | varchar(10) | 'draft' or 'final' |
| created_at | timestamp | |
| updated_at | timestamp | |

### `word`
| Column | Type | Notes |
|---|---|---|
| id | integer PK | |
| arabic_text | text unique | Exact match (eat ≠ eats ≠ eating) |
| normalized_text | text | Diacritics-stripped, auto-generated for search |
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

---

## Key Design Decisions

### Word uniqueness
`eat`, `eats`, `eating` are stored as 3 separate unique `word` rows.
No lemmatization or root-based merging.

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

### normalized_text
Auto-generated from `arabic_text` by stripping Arabic diacritics (harakat/
tashkeel, Unicode range U+064B–U+065F and related). Use the `pyarabic`
library for reliable stripping. Stored in `word.normalized_text` to enable
fast diacritics-insensitive search without runtime computation.

### Ayah arabic_text
Stored as-is from Quran Foundation API (Uthmani script). Never reconstructed
from word occurrences. This is the source of truth for display.

### No version/edit history
No changelog or history table needed. Overwriting is fine.

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
- Do NOT add version/history tracking
- Do NOT add multi-user roles (single admin only for now)
