"""
Management command: verify_data_integrity

Read-only health checks on the Quran data, meant to run right after
import_ayahs_and_words. Covers:

  1. Unicode normalization (NFC) — catches words that are visually
     identical but stored as different codepoint sequences, which would
     hide as separate `word` rows despite being "the same" word.
  2. raw_text <-> arabic_text consistency — for every word_occurrence,
     stripping annotations from raw_text should reproduce exactly the
     linked word's arabic_text. A mismatch means some character class
     slipped past strip_quranic_annotations().
  3. Empty/invalid word rows — a `word` row whose arabic_text became
     blank after stripping (e.g. a mis-tagged annotation-only segment).
  4. Position-sequence integrity — every ayah's word_occurrence positions
     should be exactly 1..N with no gaps or duplicates.

This command makes NO changes to the database — read-only, like
audit_word_marks.

Usage:
    python manage.py verify_data_integrity

Place at:
    apps/quran/management/commands/verify_data_integrity.py
"""
import unicodedata
from collections import defaultdict
from itertools import groupby

from django.core.management.base import BaseCommand

from apps.quran.models import Ayah, Word, WordOccurrence
from apps.quran.services.text_normalizer import strip_quranic_annotations


class Command(BaseCommand):
    help = "Read-only integrity checks on Quran data after import. Makes no changes."

    def handle(self, *args, **options):
        problems_found = False

        problems_found |= self.check_nfc_duplicates()
        problems_found |= self.check_raw_text_consistency()
        problems_found |= self.check_empty_words()
        problems_found |= self.check_position_sequences()

        self.print_summary()

        if not problems_found:
            self.stdout.write(self.style.SUCCESS("\nAll checks passed. No issues found."))

    # ------------------------------------------------------------------
    def check_nfc_duplicates(self):
        self.stdout.write(self.style.HTTP_INFO("\n[1/4] Unicode normalization (NFC) check..."))

        by_nfc = defaultdict(list)  # nfc_form -> [(word_id, arabic_text), ...]
        non_nfc_count = 0

        for word in Word.objects.all().only("id", "arabic_text"):
            nfc = unicodedata.normalize("NFC", word.arabic_text)
            by_nfc[nfc].append((word.id, word.arabic_text))
            if nfc != word.arabic_text:
                non_nfc_count += 1

        collisions = {k: v for k, v in by_nfc.items() if len(v) > 1}

        if non_nfc_count:
            self.stdout.write(self.style.WARNING(
                f"    {non_nfc_count} word row(s) are not already in NFC form "
                f"(informational only — not necessarily a problem by itself)."
            ))

        if not collisions:
            self.stdout.write(self.style.SUCCESS(
                "    No hidden duplicates caused by normalization-form differences."
            ))
            return False

        self.stdout.write(self.style.ERROR(
            f"    {len(collisions)} group(s) of words are DUPLICATES that differ "
            f"only in Unicode normalization form:"
        ))
        for nfc_form, entries in list(collisions.items())[:10]:
            ids = ", ".join(f'id={wid} "{txt}"' for wid, txt in entries)
            self.stdout.write(f"      {ids}")
        if len(collisions) > 10:
            self.stdout.write(f"      ... and {len(collisions) - 10} more group(s)")
        return True

    # ------------------------------------------------------------------
    def check_raw_text_consistency(self):
        self.stdout.write(self.style.HTTP_INFO("\n[2/4] raw_text <-> arabic_text consistency check..."))

        mismatches = []
        blanks = []

        qs = WordOccurrence.objects.select_related("word", "ayah")
        for occ in qs.iterator():
            if not occ.raw_text:
                blanks.append(occ)
                continue
            # Match Word.save()'s behavior exactly: it re-normalizes to NFC
            # AFTER the text is set, so the comparison must do the same —
            # stripping a mark from between two combining diacritics can
            # change their canonical order (see import command for details).
            expected = unicodedata.normalize(
                'NFC', strip_quranic_annotations(occ.raw_text)
            )
            if expected != occ.word.arabic_text:
                mismatches.append(occ)

        if blanks:
            self.stdout.write(self.style.WARNING(f"    {len(blanks)} occurrence(s) have an empty raw_text."))
            for occ in blanks[:5]:
                self.stdout.write(f"      {occ.ayah.verse_key} #{occ.position} (word_id={occ.word_id})")

        if not mismatches:
            self.stdout.write(self.style.SUCCESS(
                "    All occurrences are consistent with their word's arabic_text."
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"    {len(mismatches)} occurrence(s) DON'T match their word's arabic_text "
                f"after stripping — likely an uncaught character class:"
            ))
            for occ in mismatches[:10]:
                self.stdout.write(
                    f'      {occ.ayah.verse_key} #{occ.position}  raw="{occ.raw_text}"  '
                    f'word.arabic_text="{occ.word.arabic_text}"'
                )
            if len(mismatches) > 10:
                self.stdout.write(f"      ... and {len(mismatches) - 10} more")

        return bool(mismatches)

    # ------------------------------------------------------------------
    def check_empty_words(self):
        self.stdout.write(self.style.HTTP_INFO("\n[3/4] Empty/invalid word row check..."))

        empties = set(Word.objects.filter(arabic_text="").values_list("id", flat=True))
        for word in Word.objects.all().only("id", "arabic_text"):
            if word.arabic_text.strip() == "":
                empties.add(word.id)

        if not empties:
            self.stdout.write(self.style.SUCCESS("    No empty/blank word rows."))
            return False

        self.stdout.write(self.style.ERROR(f"    {len(empties)} word row(s) have empty/blank arabic_text:"))
        for word_id in list(empties)[:10]:
            occ = WordOccurrence.objects.filter(word_id=word_id).select_related("ayah").first()
            ref = occ.ayah.verse_key if occ else "no occurrence found"
            self.stdout.write(f"      word_id={word_id} (e.g. {ref})")
        return True

    # ------------------------------------------------------------------
    def check_position_sequences(self):
        self.stdout.write(self.style.HTTP_INFO("\n[4/4] Position-sequence integrity per ayah..."))

        rows = (
            WordOccurrence.objects
            .order_by("ayah_id", "position")
            .values_list("ayah_id", "ayah__verse_key", "position")
        )

        broken = []
        for ayah_id, group in groupby(rows, key=lambda r: r[0]):
            group = list(group)
            verse_key = group[0][1]
            positions = [g[2] for g in group]
            expected = list(range(1, len(positions) + 1))
            if positions != expected:
                broken.append((verse_key, positions))

        if not broken:
            self.stdout.write(self.style.SUCCESS("    All ayahs have clean, gap-free position sequences."))
            return False

        self.stdout.write(self.style.ERROR(f"    {len(broken)} ayah(s) have broken position sequences:"))
        for verse_key, positions in broken[:10]:
            self.stdout.write(f"      {verse_key}: positions = {positions}")
        if len(broken) > 10:
            self.stdout.write(f"      ... and {len(broken) - 10} more")
        return True

    # ------------------------------------------------------------------
    def print_summary(self):
        self.stdout.write(self.style.HTTP_INFO("\n--- Summary ---"))
        self.stdout.write(f"Ayahs: {Ayah.objects.count()}")
        self.stdout.write(f"Words: {Word.objects.count()}")
        self.stdout.write(f"Word occurrences: {WordOccurrence.objects.count()}")
        self.stdout.write(
            "(Traditionally cited total Quran word count is ~77,430 — compare "
            "against the occurrence count above; small differences usually come "
            "from word-segmentation convention, not necessarily a bug.)"
        )