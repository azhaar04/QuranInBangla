from django.core.management.base import BaseCommand, CommandError

from apps.quran.models import Ayah, Ruku, Surah, Word, WordOccurrence
from apps.quran.services.quran_api_client import QuranAPIClient


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

                    word, word_created = Word.objects.get_or_create(
                        arabic_text=word_data['text_uthmani'],
                    )
                    words_created += word_created

                    _, occurrence_created = WordOccurrence.objects.get_or_create(
                        ayah=ayah,
                        position=word_data['position'],
                        defaults={'word': word},
                    )
                    occurrences_created += occurrence_created

            self.stdout.write(f'  {surah.number}. {surah.name_english}: {len(verses)} ayahs')

        self.stdout.write(self.style.SUCCESS(
            f'Ayahs created: {ayahs_created}. Words created: {words_created}. '
            f'Word occurrences created: {occurrences_created}.'
        ))
