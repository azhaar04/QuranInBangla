"""
Management command: audit `word.arabic_text` for embedded Quranic
annotation marks (waqf signs, hizb/juz markers, madd/silent-letter marks,
etc.) that fall outside normal Arabic letters + tashkeel.

Why this matters
-----------------
These marks (waqf pause signs, the rub-el-hizb "۞" structural marker,
small waw/yeh/madda recitation marks, ...) are context-dependent — they
only show up in certain occurrences of a word, not every occurrence.
When they get baked directly into `word.arabic_text`, the same lexical
word can silently fork into multiple `word` rows (e.g. "رَيْبَ" vs.
"رَيْبَ ۛ"), which breaks:
  - default meaning propagation (word_meaning is keyed by word_id)
  - word_note sharing (root / pattern / grammatical_information etc.)
  - is_meaning_final / progress-dashboard accuracy

This command does NOT modify any data. It only reports where these
marks currently exist, grouped by mark type, with example ayah
references, so you can see the real scope before deciding how to fix
the import pipeline.

Usage
-----
    python manage.py audit_word_marks
    python manage.py audit_word_marks --limit-examples 5
    python manage.py audit_word_marks --csv word_marks_report.csv

Place this file at:
    apps/quran/management/commands/audit_word_marks.py

Note: adjust the `from apps.quran.models import ...` line below if your
Word / WordOccurrence models live somewhere else.
"""
import csv
import unicodedata
from collections import defaultdict

from django.core.management.base import BaseCommand

from apps.quran.models import Word, WordOccurrence


# --- What counts as "normal" text for a canonical Quranic word ------------
# Base Arabic letters (hamza .. yeh) used in Uthmani Quran text.
NORMAL_RANGES = [
    (0x0621, 0x064A),
]
# Individually normal codepoints outside the range above.
NORMAL_SINGLES = {
    0x0640,  # ARABIC TATWEEL
    0x0670,  # ARABIC LETTER SUPERSCRIPT ALEF (dagger alif) — e.g. رَحْمَـٰن
    0x0671,  # ARABIC LETTER ALEF WASLA — e.g. ٱ
    0x0020,  # space
}
# Standard tashkeel/harakat (fatha, damma, kasra, sukun, shadda, tanwin...)
# — this is the same U+064B–U+065F range your normalized_text already strips.
NORMAL_SINGLES |= set(range(0x064B, 0x0660))

# Friendly labels for marks we've already identified. Anything not in this
# dict will still be reported, just without the extra context.
KNOWN_MARKS = {
    0x06D6: "waqf sign: Sila / Al-Wasl Awla — continuing preferred",
    0x06D7: "waqf sign: Qila / Al-Waqf Awla — stopping preferred",
    0x06D8: "waqf sign: small high meem (initial form)",
    0x06D9: "waqf sign: La — forbidden stop (waqf mamnu')",
    0x06DA: "waqf sign: Ja'iz — permissible stop",
    0x06DB: "waqf sign: Mu'anaqah — pause at one of a pair",
    0x06DC: "waqf sign: Sakta — brief silent pause",
    0x06DD: "end-of-ayah marker",
    0x06DE: "Rub el-Hizb marker — structural (hizb/juz division), NOT a pause sign",
    0x06E2: "waqf sign: Lazim — mandatory stop (meem, isolated form)",
    0x06E5: "small waw — recitation / silent-letter mark",
    0x06E6: "small yeh — recitation / silent-letter mark",
    0x06E9: "place-of-sajdah marker",
    0x06ED: "waqf sign: Lazim variant (meem, low form)",
}


def is_normal(ch: str) -> bool:
    cp = ord(ch)
    if cp in NORMAL_SINGLES:
        return True
    return any(lo <= cp <= hi for lo, hi in NORMAL_RANGES)


def char_label(ch: str) -> str:
    cp = ord(ch)
    try:
        name = unicodedata.name(ch)
    except ValueError:
        name = "UNNAMED"
    base = f"U+{cp:04X} {name}"
    friendly = KNOWN_MARKS.get(cp)
    return f"{base}  →  {friendly}" if friendly else base


class Command(BaseCommand):
    help = (
        "Scan word.arabic_text for embedded Quranic annotation marks "
        "(waqf signs, hizb markers, madd/silent-letter marks, etc.) that "
        "fall outside normal Arabic letters + tashkeel. Read-only report."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit-examples",
            type=int,
            default=3,
            help="How many example words to print per mark type (default: 3)",
        )
        parser.add_argument(
            "--csv",
            type=str,
            default=None,
            help="Optional path to also write the full per-word findings as CSV",
        )

    def handle(self, *args, **options):
        limit_examples = options["limit_examples"]
        csv_path = options["csv"]

        by_mark = defaultdict(list)   # mark label -> [(word_id, arabic_text), ...]
        flagged_words = []

        total_words = Word.objects.count()
        self.stdout.write(f"Scanning {total_words} word rows...")

        for word in Word.objects.all().only("id", "arabic_text"):
            extras = {ch for ch in word.arabic_text if not is_normal(ch)}
            if not extras:
                continue
            flagged_words.append(word)
            for ch in extras:
                by_mark[char_label(ch)].append((word.id, word.arabic_text))

        if not flagged_words:
            self.stdout.write(self.style.SUCCESS(
                "\nNo non-standard characters found in word.arabic_text. Clean."
            ))
            return

        self.stdout.write(self.style.WARNING(
            f"\n{len(flagged_words)} / {total_words} word rows contain a "
            f"non-standard character.\n"
        ))

        for mark, entries in sorted(by_mark.items(), key=lambda kv: -len(kv[1])):
            self.stdout.write(self.style.HTTP_INFO(f"\n{mark}  —  {len(entries)} word row(s)"))
            for word_id, text in entries[:limit_examples]:
                occ = (
                    WordOccurrence.objects
                    .filter(word_id=word_id)
                    .select_related("ayah")
                    .first()
                )
                ref = occ.ayah.verse_key if occ and occ.ayah_id else "no occurrence found"
                self.stdout.write(f"    word_id={word_id:<6} \"{text}\"   (e.g. {ref})")
            if len(entries) > limit_examples:
                self.stdout.write(f"    ... and {len(entries) - limit_examples} more")

        if csv_path:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["word_id", "arabic_text", "flagged_chars", "example_verse_key"])
                for word in flagged_words:
                    extras = sorted({char_label(ch) for ch in word.arabic_text if not is_normal(ch)})
                    occ = (
                        WordOccurrence.objects
                        .filter(word_id=word.id)
                        .select_related("ayah")
                        .first()
                    )
                    ref = occ.ayah.verse_key if occ and occ.ayah_id else ""
                    writer.writerow([word.id, word.arabic_text, "; ".join(extras), ref])
            self.stdout.write(self.style.SUCCESS(f"\nFull report written to {csv_path}"))

        self.stdout.write(self.style.SUCCESS("\nDone."))