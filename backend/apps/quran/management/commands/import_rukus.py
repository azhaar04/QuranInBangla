from django.core.management.base import BaseCommand, CommandError

from apps.quran.models import Ruku, Surah
from apps.quran.services.quran_api_client import QuranAPIClient


class Command(BaseCommand):
    help = 'Import all rukus from the Quran Foundation API. Requires import_surahs to have run first.'

    def handle(self, *args, **options):
        if not Surah.objects.exists():
            raise CommandError('No surahs found. Run `import_surahs` first.')

        client = QuranAPIClient()
        total = 0
        created = 0

        for surah in Surah.objects.order_by('number'):
            verses = client.get_verses_by_chapter(surah.number)

            groups = {}
            for verse in verses:
                groups.setdefault(verse['ruku_number'], []).append(verse)

            for surah_ruku_number, ruku_number in enumerate(sorted(groups), start=1):
                group_verses = groups[ruku_number]
                total += 1
                _, was_created = Ruku.objects.get_or_create(
                    ruku_number=ruku_number,
                    defaults={
                        'surah': surah,
                        'surah_ruku_number': surah_ruku_number,
                        'first_verse_id': group_verses[0]['id'],
                        'last_verse_id': group_verses[-1]['id'],
                        'verses_count': len(group_verses),
                    },
                )
                created += was_created

            self.stdout.write(f'  {surah.number}. {surah.name_english}: {len(groups)} rukus')

        self.stdout.write(self.style.SUCCESS(
            f'Rukus: {total} total, {created} created, {total - created} already existed.'
        ))
