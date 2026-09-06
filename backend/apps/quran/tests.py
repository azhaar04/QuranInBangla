from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
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

    def test_ayah_detail_exposes_word_is_meaning_final_per_occurrence(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        occurrence_data = response.data['word_occurrences'][0]
        self.assertFalse(occurrence_data['word_is_meaning_final'])

        self.word.is_meaning_final = True
        self.word.save(update_fields=['is_meaning_final'])

        response = self.client.get(self.url)
        occurrence_data = response.data['word_occurrences'][0]
        self.assertTrue(occurrence_data['word_is_meaning_final'])

    def test_finalizing_without_translation_change_logs_finalized_only(self):
        self.ayah.translation_text = 'পরীক্ষা অনুবাদ'
        self.ayah.save(update_fields=['translation_text'])
        WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        self.assertEqual(ActivityLog.objects.count(), 0)

        response = self.client.patch(self.url, {'status': 'final'}, format='json')
        self.assertEqual(response.status_code, 200)

        log = ActivityLog.objects.get()
        self.assertEqual(log.action_type, ActivityLog.ActionType.AYAH_UPDATED)
        self.assertEqual(log.ayah_id, self.ayah.id)
        self.assertFalse(log.content_changed)
        self.assertTrue(log.finalized)

    def test_translating_and_finalizing_together_logs_both_flags(self):
        WordMeaning.objects.create(word=self.word, meaning_text='আমি')
        self.assertEqual(ActivityLog.objects.count(), 0)

        response = self.client.patch(
            self.url, {'translation_text': 'নতুন অনুবাদ', 'status': 'final'}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        log = ActivityLog.objects.get()
        self.assertEqual(log.action_type, ActivityLog.ActionType.AYAH_TRANSLATED)
        self.assertTrue(log.content_changed)
        self.assertTrue(log.finalized)

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


class WordOccurrenceAnalysisTests(APITestCase):
    """Covers the Word Grammatical Analysis modal's combined Save endpoint —
    meaning override, word note, and is_meaning_final all in one PATCH,
    collapsing into at most one ActivityLog row per save (client-requested:
    editing note fields AND marking Final in the same save should show as
    ONE activity, not two)."""

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
        return reverse('quran:word_occurrence_analysis', kwargs={'pk': occurrence.id})

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

    def test_override_with_new_text_creates_non_default_meaning_and_logs_updated(self):
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

    def test_blank_meaning_text_is_simply_skipped_not_rejected(self):
        response = self.client.patch(self._url(self.occurrence), {'meaning_text': '  '}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActivityLog.objects.count(), 0)

    def test_note_only_change_logs_content_changed_not_finalized(self):
        response = self.client.patch(
            self._url(self.occurrence), {'note': {'root': 'ب س م'}}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        note = WordNote.objects.get(word=self.word)
        self.assertEqual(note.root, 'ب س م')

        log = ActivityLog.objects.get()
        self.assertEqual(log.action_type, ActivityLog.ActionType.WORD_MEANING_UPDATED)
        self.assertEqual(log.ayah_id, self.ayah.id)
        self.assertEqual(log.word_id, self.word.id)
        self.assertTrue(log.content_changed)
        self.assertFalse(log.finalized)

    def test_is_meaning_final_only_change_logs_finalized_not_content_changed(self):
        response = self.client.patch(
            self._url(self.occurrence), {'is_meaning_final': True}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        self.word.refresh_from_db()
        self.assertTrue(self.word.is_meaning_final)

        log = ActivityLog.objects.get()
        self.assertEqual(log.action_type, ActivityLog.ActionType.WORD_MEANING_UPDATED)
        self.assertFalse(log.content_changed)
        self.assertTrue(log.finalized)

    def test_response_reflects_updated_is_meaning_final_immediately(self):
        response = self.client.patch(
            self._url(self.occurrence), {'is_meaning_final': True}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['word_is_meaning_final'])

    def test_unfinalizing_logs_as_content_changed_not_finalized(self):
        self.word.is_meaning_final = True
        self.word.save(update_fields=['is_meaning_final'])

        response = self.client.patch(
            self._url(self.occurrence), {'is_meaning_final': False}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        log = ActivityLog.objects.get()
        self.assertTrue(log.content_changed)
        self.assertFalse(log.finalized)

    def test_note_and_final_change_together_create_exactly_one_log_with_both_flags(self):
        response = self.client.patch(
            self._url(self.occurrence),
            {'note': {'root': 'ب س م'}, 'is_meaning_final': True},
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        self.word.refresh_from_db()
        self.assertTrue(self.word.is_meaning_final)
        self.assertEqual(WordNote.objects.get(word=self.word).root, 'ب س م')
        self.assertEqual(ActivityLog.objects.count(), 1)

        log = ActivityLog.objects.get()
        self.assertTrue(log.content_changed)
        self.assertTrue(log.finalized)

    def test_nothing_changed_creates_no_log(self):
        WordNote.objects.create(word=self.word, root='ب س م')
        self.word.is_meaning_final = True
        self.word.save(update_fields=['is_meaning_final'])

        response = self.client.patch(
            self._url(self.occurrence),
            {'note': {'root': 'ب س م'}, 'is_meaning_final': True},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActivityLog.objects.count(), 0)


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


class SearchAyahViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('quran:ayah_search')

        self.surah = Surah.objects.create(
            number=1, name_arabic='الفاتحة', name_bangla='আল ফাতিহা',
            meaning_bangla='সূচনা', name_english='Al-Fatihah', total_ayah=7,
        )
        self.other_surah = Surah.objects.create(
            number=2, name_arabic='البقرة', name_bangla='আল বাকারা',
            meaning_bangla='গাভী', name_english='Al-Baqarah', total_ayah=286,
        )

        self.match_word = Word.objects.create(arabic_text='بِسْمِ')

    def _make_ayah(self, surah, ayah_number, word_texts, match_positions=()):
        verse_key = f'{surah.number}:{ayah_number}'
        ayah = Ayah.objects.create(
            surah=surah, ayah_number=ayah_number, verse_key=verse_key,
            arabic_text=' '.join(word_texts),
        )
        for position, text in enumerate(word_texts, start=1):
            word = self.match_word if position in match_positions else Word.objects.create(
                arabic_text=f'{text}-{verse_key}-{position}'
            )
            WordOccurrence.objects.create(ayah=ayah, word=word, position=position, raw_text=text)
        return ayah

    def _search(self, query):
        return self.client.get(self.url, {'q': query})

    def test_matches_via_normalized_text_ignoring_diacritics(self):
        self._make_ayah(self.surah, 1, ['بِسْمِ', 'اللَّهِ'], match_positions=[1])

        response = self._search('بسم')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['verse_key'], '1:1')

    def test_matches_via_exact_arabic_text_substring(self):
        self._make_ayah(self.surah, 1, ['بِسْمِ', 'اللَّهِ'], match_positions=[1])

        response = self._search('بِسْمِ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_empty_query_returns_no_results(self):
        self._make_ayah(self.surah, 1, ['بِسْمِ', 'اللَّهِ'], match_positions=[1])

        response = self._search('')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_ayah_within_word_limit_returns_full_ayah(self):
        words = [f'word{i}' for i in range(1, 4)]
        self._make_ayah(self.surah, 1, words, match_positions=[2])

        response = self._search('بسم')
        result = response.data['results'][0]
        self.assertTrue(result['is_full_ayah'])
        self.assertEqual(len(result['portion']), 3)
        self.assertEqual([p['is_match'] for p in result['portion']], [False, True, False])

    def test_long_ayah_windows_around_centered_match(self):
        words = [f'word{i}' for i in range(1, 16)]  # 15 words
        self._make_ayah(self.surah, 1, words, match_positions=[8])  # index 7

        response = self._search('بسم')
        result = response.data['results'][0]
        self.assertFalse(result['is_full_ayah'])
        portion = result['portion']
        self.assertEqual(len(portion), 10)
        # 5 words before the match, 4 after, within the window
        matches = [i for i, p in enumerate(portion) if p['is_match']]
        self.assertEqual(matches, [5])
        self.assertEqual(portion[5]['text'], 'word8')
        self.assertEqual(portion[0]['text'], 'word3')
        self.assertEqual(portion[-1]['text'], 'word12')

    def test_long_ayah_windows_fill_from_other_side_near_start(self):
        words = [f'word{i}' for i in range(1, 16)]  # 15 words
        self._make_ayah(self.surah, 1, words, match_positions=[2])  # index 1

        response = self._search('بسم')
        portion = response.data['results'][0]['portion']
        self.assertEqual(len(portion), 10)
        self.assertEqual(portion[0]['text'], 'word1')
        self.assertEqual(portion[-1]['text'], 'word10')

    def test_long_ayah_windows_fill_from_other_side_near_end(self):
        words = [f'word{i}' for i in range(1, 16)]  # 15 words
        self._make_ayah(self.surah, 1, words, match_positions=[14])  # index 13

        response = self._search('بسم')
        portion = response.data['results'][0]['portion']
        self.assertEqual(len(portion), 10)
        self.assertEqual(portion[0]['text'], 'word6')
        self.assertEqual(portion[-1]['text'], 'word15')

    def test_results_ordered_by_surah_then_ayah_number(self):
        self._make_ayah(self.other_surah, 5, ['x', 'بِسْمِ'], match_positions=[2])
        self._make_ayah(self.surah, 3, ['x', 'بِسْمِ'], match_positions=[2])
        self._make_ayah(self.surah, 1, ['x', 'بِسْمِ'], match_positions=[2])

        response = self._search('بسم')
        verse_keys = [r['verse_key'] for r in response.data['results']]
        self.assertEqual(verse_keys, ['1:1', '1:3', '2:5'])

    def test_ayah_with_repeated_match_appears_once(self):
        self._make_ayah(self.surah, 1, ['بِسْمِ', 'x', 'بِسْمِ'], match_positions=[1, 3])

        response = self._search('بسم')
        self.assertEqual(response.data['count'], 1)
        matches = [p['is_match'] for p in response.data['results'][0]['portion']]
        self.assertEqual(matches, [True, False, True])


class DashboardSummaryViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('quran:dashboard_summary')

        self.surah1 = Surah.objects.create(
            number=1, name_arabic='الفاتحة', name_bangla='আল ফাতিহা',
            meaning_bangla='সূচনা', name_english='Al-Fatihah', total_ayah=2,
        )
        self.surah2 = Surah.objects.create(
            number=2, name_arabic='البقرة', name_bangla='আল বাকারা',
            meaning_bangla='গাভী', name_english='Al-Baqarah', total_ayah=1,
        )
        # surah1 has one Final ayah -> counts as "started"; surah2 has none -> not started
        self.ayah1 = Ayah.objects.create(
            surah=self.surah1, ayah_number=1, verse_key='1:1', arabic_text='بِسْمِ',
            status=Ayah.Status.FINAL,
        )
        self.ayah2 = Ayah.objects.create(
            surah=self.surah1, ayah_number=2, verse_key='1:2', arabic_text='اللَّهِ',
        )
        self.ayah3 = Ayah.objects.create(
            surah=self.surah2, ayah_number=1, verse_key='2:1', arabic_text='الرَّحْمَٰنِ',
        )

        self.final_word = Word.objects.create(arabic_text='بِسْمِ', is_meaning_final=True)
        self.draft_word = Word.objects.create(arabic_text='اللَّهِ')
        # ayah1: its only word is is_meaning_final -> per-ayah complete
        WordOccurrence.objects.create(ayah=self.ayah1, word=self.final_word, position=1, raw_text='بِسْمِ')
        # ayah2: its only word is not is_meaning_final -> per-ayah incomplete
        WordOccurrence.objects.create(ayah=self.ayah2, word=self.draft_word, position=1, raw_text='اللَّهِ')
        # ayah3 has no words at all -> must not trivially count as complete

    def test_summary_counts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['surahs_started'], 1)
        self.assertEqual(data['surahs_total'], 2)
        self.assertEqual(data['ayahs_final'], 1)
        self.assertEqual(data['ayahs_total'], 3)
        self.assertEqual(data['word_meaning_final'], 1)
        self.assertEqual(data['word_meaning_total'], 2)
        self.assertEqual(data['per_ayah_word_final'], 1)
        self.assertEqual(data['per_ayah_word_total'], 3)


class ActivityLogListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('quran:dashboard_activity')

        self.surah = Surah.objects.create(
            number=1, name_arabic='الفاتحة', name_bangla='আল ফাতিহা',
            meaning_bangla='সূচনা', name_english='Al-Fatihah', total_ayah=1,
        )
        self.ayah = Ayah.objects.create(
            surah=self.surah, ayah_number=1, verse_key='1:1', arabic_text='بِسْمِ',
        )
        self.word = Word.objects.create(arabic_text='بِسْمِ')

        self.recent_log = ActivityLog.objects.create(
            user=self.user, action_type=ActivityLog.ActionType.AYAH_TRANSLATED, ayah=self.ayah,
        )
        self.old_log = ActivityLog.objects.create(
            user=self.user, action_type=ActivityLog.ActionType.WORD_MEANING_ADDED,
            ayah=self.ayah, word=self.word,
        )
        # auto_now_add ignores an explicit value at create() time, so backdate
        # via a queryset UPDATE (bypasses save()) to simulate an old entry.
        ActivityLog.objects.filter(pk=self.old_log.pk).update(
            created_at=timezone.now() - timedelta(days=40)
        )

    def test_default_returns_all_unfiltered(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_range_filters_out_older_entries(self):
        response = self.client.get(self.url, {'range': '7d'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.recent_log.id)

    def test_unknown_range_is_ignored(self):
        response = self.client.get(self.url, {'range': 'bogus'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_serializer_exposes_ayah_and_word_context(self):
        response = self.client.get(self.url)
        results = {r['id']: r for r in response.data['results']}

        word_row = results[self.old_log.id]
        self.assertEqual(word_row['surah_number'], 1)
        self.assertEqual(word_row['surah_name_bangla'], 'আল ফাতিহা')
        self.assertEqual(word_row['ayah_number'], 1)
        self.assertEqual(word_row['verse_key'], '1:1')
        self.assertEqual(word_row['word_arabic_text'], 'بِسْمِ')

        translated_row = results[self.recent_log.id]
        self.assertIsNone(translated_row['word_arabic_text'])
        self.assertIsNone(translated_row['word_occurrence_id'])


class ActivityLogWordOccurrenceResolutionTests(APITestCase):
    """A word can appear in many ayahs/surahs — proves that's not actually
    ambiguous for the Recent Activity feed: each log's ayah_id already pins
    down which specific ayah the edit happened in, so word_occurrence_id
    must resolve to the occurrence IN THAT AYAH, not some other ayah where
    the same word also happens to appear."""

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('quran:dashboard_activity')

        self.surah1 = Surah.objects.create(
            number=1, name_arabic='الفاتحة', name_bangla='আল ফাতিহা',
            meaning_bangla='সূচনা', name_english='Al-Fatihah', total_ayah=1,
        )
        self.surah2 = Surah.objects.create(
            number=2, name_arabic='البقرة', name_bangla='আল বাকারা',
            meaning_bangla='গাভী', name_english='Al-Baqarah', total_ayah=1,
        )
        self.ayah1 = Ayah.objects.create(
            surah=self.surah1, ayah_number=1, verse_key='1:1', arabic_text='بِسْمِ',
        )
        self.ayah2 = Ayah.objects.create(
            surah=self.surah2, ayah_number=1, verse_key='2:1', arabic_text='بِسْمِ',
        )
        # Same word appears in both ayahs (different surahs).
        self.word = Word.objects.create(arabic_text='بِسْمِ')
        self.occurrence1 = WordOccurrence.objects.create(
            ayah=self.ayah1, word=self.word, position=1, raw_text='بِسْمِ',
        )
        self.occurrence2 = WordOccurrence.objects.create(
            ayah=self.ayah2, word=self.word, position=1, raw_text='بِسْمِ',
        )

        self.log_surah1 = ActivityLog.objects.create(
            user=self.user, action_type=ActivityLog.ActionType.WORD_MEANING_ADDED,
            ayah=self.ayah1, word=self.word,
        )
        self.log_surah2 = ActivityLog.objects.create(
            user=self.user, action_type=ActivityLog.ActionType.WORD_MEANING_UPDATED,
            ayah=self.ayah2, word=self.word,
        )

    def test_each_log_resolves_to_its_own_ayahs_occurrence(self):
        response = self.client.get(self.url)
        results = {r['id']: r for r in response.data['results']}

        self.assertEqual(results[self.log_surah1.id]['word_occurrence_id'], self.occurrence1.id)
        self.assertEqual(results[self.log_surah1.id]['surah_number'], 1)

        self.assertEqual(results[self.log_surah2.id]['word_occurrence_id'], self.occurrence2.id)
        self.assertEqual(results[self.log_surah2.id]['surah_number'], 2)
