import unicodedata

from django.core.management.base import BaseCommand, CommandError

from apps.quran.models import Ayah, Ruku, Surah, Word, WordOccurrence
from apps.quran.services.quran_api_client import QuranAPIClient
from apps.quran.services.text_normalizer import strip_quranic_annotations


class Command(BaseCommand):
    help = (
        'Import all ayahs and their word-by-word breakdown from the Quran '
        'Foundation API. Requires import_surahs and import_rukus to have run first.'
    )

    def handle(self, *args, **options):
        if not Surah.objects.exists():
            raise CommandError('No surahs found. Run `import_surahs` first.')
        if not Ruku.objects.exists():
            raise CommandError('No rukus found. Run `import_rukus` first.')

        client = QuranAPIClient()
        ayahs_created = 0
        words_created = 0
        occurrences_created = 0

        for surah in Surah.objects.order_by('number'):
            verses = client.get_verses_by_chapter(surah.number, with_words=True)
            rukus_by_number = {r.ruku_number: r for r in Ruku.objects.filter(surah=surah)}

            for verse in verses:
                ayah, ayah_created = Ayah.objects.get_or_create(
                    verse_key=verse['verse_key'],
                    defaults={
                        'surah': surah,
                        'ruku': rukus_by_number.get(verse['ruku_number']),
                        'ayah_number': verse['verse_number'],
                        'arabic_text': verse['text_uthmani'],
                    },
                )
                ayahs_created += ayah_created

                for word_data in verse['words']:
                    if word_data['char_type_name'] != 'word':
                        continue

                    # 1) NFC-normalize first, so the same visual word is
                    #    never split into two `word` rows just because the
                    #    API sent a precomposed vs. decomposed form.
                    # 2) Strip positional marks (waqf signs, rub-el-hizb,
                    #    silent-letter marks) to get the canonical form used
                    #    for word identity/meaning/note linking.
                    # The raw (NFC-normalized but un-stripped) text is kept
                    # on the occurrence so nothing is lost for display.
                    raw_text = unicodedata.normalize('NFC', word_data['text_uthmani'])
                    canonical_text = strip_quranic_annotations(raw_text)

                    word, word_created = Word.objects.get_or_create(
                        arabic_text=canonical_text,
                    )
                    words_created += word_created

                    _, occurrence_created = WordOccurrence.objects.get_or_create(
                        ayah=ayah,
                        position=word_data['position'],
                        defaults={'word': word, 'raw_text': raw_text},
                    )
                    occurrences_created += occurrence_created

            self.stdout.write(f'  {surah.number}. {surah.name_english}: {len(verses)} ayahs')

        self.stdout.write(self.style.SUCCESS(
            f'Ayahs created: {ayahs_created}. Words created: {words_created}. '
            f'Word occurrences created: {occurrences_created}.'
        ))