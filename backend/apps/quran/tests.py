from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.quran.models import ActivityLog, Ayah, Surah, Word, WordMeaning, WordNote, WordOccurrence

User = get_user_model()


class AyahFinalStatusTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)

        self.surah = Surah.objects.create(
            number=1, name_arabic='الفاتحة', name_bangla='আল ফাতিহা',
            meaning_bangla='সূচনা', name_english='Al-Fatihah', total_ayah=7,
        )
        self.ayah = Ayah.objects.create(
            surah=self.surah, ayah_number=1, verse_key='1:1', arabic_text='بِسْمِ اللَّهِ',
        )
        self.word = Word.objects.create(arabic_text='بِسْمِ')
        self.occurrence = WordOccurrence.objects.create(
            ayah=self.ayah, word=self.word, position=1, raw_text='بِسْمِ',
        )
        self.url = reverse('quran:ayah_detail', kwargs={'verse_key': self.ayah.verse_key})

    def test_cannot_finalize_without_translation(self):
        response = self.client.patch(self.url, {'status': 'final'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.ayah.refresh_from_db()
        self.assertEqual(self.ayah.status, Ayah.Status.DRAFT)

    def test_cannot_finalize_with_unassigned_word_meaning(self):
        self.ayah.translation_text = 'পরীক্ষা অনুবাদ'
        self.ayah.save(update_fields=['translation_text'])

        response = self.client.patch(self.url, {'status': 'final'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_can_finalize_when_translation_and_meanings_present(self):
        self.ayah.translation_text = 'পরীক্ষা অনুবাদ'
        self.ayah.save(update_fields=['translation_text'])
        meaning = WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        self.occurrence.refresh_from_db()
        self.assertEqual(self.occurrence.meaning_id, meaning.id)

        response = self.client.patch(self.url, {'status': 'final'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.ayah.refresh_from_db()
        self.assertEqual(self.ayah.status, Ayah.Status.FINAL)

    def test_editing_translation_reverts_final_to_draft(self):
        WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        self.ayah.translation_text = 'প্রথম অনুবাদ'
        self.ayah.status = Ayah.Status.FINAL
        self.ayah.save(update_fields=['translation_text', 'status'])

        response = self.client.patch(
            self.url, {'translation_text': 'পরিবর্তিত অনুবাদ'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.ayah.refresh_from_db()
        self.assertEqual(self.ayah.status, Ayah.Status.DRAFT)
        self.assertEqual(self.ayah.translation_text, 'পরিবর্তিত অনুবাদ')

    def test_editing_notes_only_does_not_revert_final(self):
        WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        self.ayah.translation_text = 'প্রথম অনুবাদ'
        self.ayah.status = Ayah.Status.FINAL
        self.ayah.save(update_fields=['translation_text', 'status'])

        response = self.client.patch(self.url, {'notes': 'একটা নোট'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.ayah.refresh_from_db()
        self.assertEqual(self.ayah.status, Ayah.Status.FINAL)

    def test_activity_log_created_on_translation_update(self):
        self.assertEqual(ActivityLog.objects.count(), 0)
        response = self.client.patch(
            self.url, {'translation_text': 'নতুন অনুবাদ'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActivityLog.objects.count(), 1)
        log = ActivityLog.objects.first()
        self.assertEqual(log.action_type, ActivityLog.ActionType.AYAH_TRANSLATED)
        self.assertEqual(log.ayah_id, self.ayah.id)

        response = self.client.patch(
            self.url, {'translation_text': 'আবার নতুন অনুবাদ'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActivityLog.objects.count(), 2)
        self.assertEqual(
            ActivityLog.objects.order_by('-created_at').first().action_type,
            ActivityLog.ActionType.AYAH_UPDATED,
        )


class WordOccurrenceMeaningTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)

        self.surah = Surah.objects.create(
            number=1, name_arabic='الفاتحة', name_bangla='আল ফাতিহা',
            meaning_bangla='সূচনা', name_english='Al-Fatihah', total_ayah=7,
        )
        self.ayah = Ayah.objects.create(
            surah=self.surah, ayah_number=1, verse_key='1:1', arabic_text='بِسْمِ اللَّهِ',
        )
        self.other_ayah = Ayah.objects.create(
            surah=self.surah, ayah_number=2, verse_key='1:2', arabic_text='بِسْمِ',
        )
        self.word = Word.objects.create(arabic_text='بِسْمِ')
        self.occurrence = WordOccurrence.objects.create(
            ayah=self.ayah, word=self.word, position=1, raw_text='بِسْمِ',
        )
        self.other_occurrence = WordOccurrence.objects.create(
            ayah=self.other_ayah, word=self.word, position=1, raw_text='بِسْمِ',
        )

    def _url(self, occurrence):
        return reverse('quran:word_occurrence_meaning', kwargs={'pk': occurrence.id})

    def test_first_meaning_ever_becomes_default_and_logs_added(self):
        response = self.client.patch(self._url(self.occurrence), {'meaning_text': 'আমি'}, format='json')
        self.assertEqual(response.status_code, 200)

        meaning = WordMeaning.objects.get(word=self.word)
        self.assertTrue(meaning.is_default)
        self.assertEqual(meaning.meaning_text, 'আমি')

        self.occurrence.refresh_from_db()
        self.other_occurrence.refresh_from_db()
        self.assertEqual(self.occurrence.meaning_id, meaning.id)
        self.assertEqual(self.other_occurrence.meaning_id, meaning.id)

        log = ActivityLog.objects.get()
        self.assertEqual(log.action_type, ActivityLog.ActionType.WORD_MEANING_ADDED)
        self.assertEqual(log.ayah_id, self.ayah.id)
        self.assertEqual(log.word_id, self.word.id)

    def test_override_reuses_existing_matching_meaning_text(self):
        default = WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        alt = WordMeaning.objects.create(word=self.word, meaning_text='মুই')

        response = self.client.patch(self._url(self.occurrence), {'meaning_text': 'মুই'}, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(WordMeaning.objects.filter(word=self.word).count(), 2)
        self.occurrence.refresh_from_db()
        self.assertEqual(self.occurrence.meaning_id, alt.id)

        self.other_occurrence.refresh_from_db()
        self.assertEqual(self.other_occurrence.meaning_id, default.id)

    def test_override_with_new_text_creates_non_default_meaning(self):
        WordMeaning.objects.create(word=self.word, meaning_text='আমি')

        response = self.client.patch(self._url(self.occurrence), {'meaning_text': 'নতুন অর্থ'}, format='json')
        self.assertEqual(response.status_code, 200)

        self.occurrence.refresh_from_db()
        self.assertEqual(self.occurrence.meaning.meaning_text, 'নতুন অর্থ')
        self.assertFalse(self.occurrence.meaning.is_default)

        log = ActivityLog.objects.get()
        self.assertEqual(log.action_type, ActivityLog.ActionType.WORD_MEANING_UPDATED)

    def test_no_op_when_text_matches_current_meaning_skips_log(self):
        WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        self.assertEqual(ActivityLog.objects.count(), 0)

        response = self.client.patch(self._url(self.occurrence), {'meaning_text': 'আমি'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActivityLog.objects.count(), 0)

    def test_blank_text_rejected(self):
        response = self.client.patch(self._url(self.occurrence), {'meaning_text': '  '}, format='json')
        self.assertEqual(response.status_code, 400)


class WordNoteViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.word = Word.objects.create(arabic_text='بِسْمِ')
        self.url = reverse('quran:word_note', kwargs={'word_id': self.word.id})

    def test_get_creates_note_on_first_access(self):
        self.assertFalse(WordNote.objects.filter(word=self.word).exists())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(WordNote.objects.filter(word=self.word).exists())

    def test_patch_updates_note_fields(self):
        response = self.client.patch(
            self.url,
            {'root': 'ب س م', 'derived_forms': ['بِاسْمِ', 'بِأَسْمَاءِ']},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        note = WordNote.objects.get(word=self.word)
        self.assertEqual(note.root, 'ب س م')
        self.assertEqual(note.derived_forms, ['بِاسْمِ', 'بِأَسْمَاءِ'])

    def test_patch_does_not_create_activity_log(self):
        self.client.patch(self.url, {'root': 'ب س م'}, format='json')
        self.assertEqual(ActivityLog.objects.count(), 0)
