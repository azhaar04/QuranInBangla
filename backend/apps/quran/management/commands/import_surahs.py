from django.core.management.base import BaseCommand

from apps.quran.models import Surah
from apps.quran.services.quran_api_client import QuranAPIClient


class Command(BaseCommand):
    help = 'Import all 114 surahs from the Quran Foundation API.'

    def handle(self, *args, **options):
        chapters = QuranAPIClient().get_chapters()

        created = 0
        for chapter in chapters:
            _, was_created = Surah.objects.get_or_create(
                number=chapter['id'],
                defaults={
                    'name_arabic': chapter['name_arabic'],
                    'name_bangla': chapter['translated_name']['name'],
                    'name_english': chapter['name_simple'],
                    'total_ayah': chapter['verses_count'],
                },
            )
            created += was_created

        self.stdout.write(self.style.SUCCESS(
            f'Surahs: {len(chapters)} total, {created} created, '
            f'{len(chapters) - created} already existed.'
        ))
