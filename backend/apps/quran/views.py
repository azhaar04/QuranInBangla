from datetime import timedelta

from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.quran.models import ActivityLog, Ayah, Ruku, Surah, Word, WordMeaning, WordNote, WordOccurrence
from apps.quran.serializers import (
    ActivityLogSerializer,
    AyahSerializer,
    RukuSerializer,
    SearchResultSerializer,
    SurahSerializer,
    WordDetailSerializer,
    WordListSerializer,
    WordMeaningSerializer,
    WordNoteSerializer,
    WordOccurrenceSerializer,
)
from apps.quran.services.text_normalizer import strip_diacritics


def _surah_queryset():
    return Surah.objects.annotate(
        final_ayah_count=Count('ayahs', filter=Q(ayahs__status=Ayah.Status.FINAL))
    ).order_by('number')


class SurahListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = _surah_queryset()
    serializer_class = SurahSerializer


class SurahDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SurahSerializer
    lookup_field = 'number'
    lookup_url_kwarg = 'surah_number'
    queryset = _surah_queryset()


class RukuAyahNumberContextMixin:
    """Resolves first_verse_id/last_verse_id (raw Ayah PKs, not FKs) to their
    ayah_number in one bulk query, for RukuSerializer's first_ayah_number/
    last_ayah_number fields."""

    def get_serializer_context(self):
        context = super().get_serializer_context()
        rukus = list(self.get_queryset())
        verse_ids = {vid for r in rukus for vid in (r.first_verse_id, r.last_verse_id)}
        context['ayah_numbers_by_id'] = dict(
            Ayah.objects.filter(id__in=verse_ids).values_list('id', 'ayah_number')
        )
        return context


class RukuListView(RukuAyahNumberContextMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Ruku.objects.select_related('surah').order_by('surah__number', 'surah_ruku_number')
    serializer_class = RukuSerializer


class RukuDetailView(RukuAyahNumberContextMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RukuSerializer
    lookup_field = 'ruku_number'
    queryset = Ruku.objects.all()


class SurahRukuListView(RukuAyahNumberContextMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RukuSerializer

    def get_queryset(self):
        return Ruku.objects.filter(surah__number=self.kwargs['surah_number']).order_by('surah_ruku_number')


def _ayah_queryset():
    return Ayah.objects.select_related('surah', 'ruku').prefetch_related(
        'word_occurrences__word', 'word_occurrences__meaning'
    )


class SurahAyahListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AyahSerializer

    def get_queryset(self):
        return _ayah_queryset().filter(surah__number=self.kwargs['surah_number'])


class AyahDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AyahSerializer
    lookup_field = 'verse_key'
    queryset = _ayah_queryset()
    http_method_names = ['get', 'patch', 'head', 'options']

    def perform_update(self, serializer):
        instance = serializer.instance
        had_content_before = bool(instance.translation_text or instance.notes)
        old_translation_text = instance.translation_text
        old_notes = instance.notes
        old_status = instance.status

        ayah = serializer.save()

        # Editing the translation of an already-Final ayah drops it back to
        # Draft, unless this same request is the one explicitly setting the
        # status (i.e. the client's own status choice wins).
        if (
            old_status == Ayah.Status.FINAL
            and ayah.status == Ayah.Status.FINAL
            and ayah.translation_text != old_translation_text
            and 'status' not in serializer.validated_data
        ):
            ayah.status = Ayah.Status.DRAFT
            ayah.save(update_fields=['status'])

        content_changed = ayah.translation_text != old_translation_text or ayah.notes != old_notes
        became_final = old_status != Ayah.Status.FINAL and ayah.status == Ayah.Status.FINAL
        if not content_changed and not became_final:
            return

        ActivityLog.objects.create(
            user=self.request.user,
            action_type=(
                ActivityLog.ActionType.AYAH_UPDATED
                if had_content_before
                else ActivityLog.ActionType.AYAH_TRANSLATED
            ),
            ayah=ayah,
            content_changed=content_changed,
            finalized=became_final,
        )


SEARCH_PORTION_WORD_LIMIT = 10


class SearchPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50


class SearchAyahView(generics.ListAPIView):
    """Word search: finds ayahs containing a Word whose arabic_text or
    normalized_text matches the query, one result row per ayah (see
    SearchResultSerializer for how the shown portion is windowed)."""

    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultSerializer
    pagination_class = SearchPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        self.matched_word_ids = set()
        if not query:
            return Ayah.objects.none()

        self.matched_word_ids = set(
            Word.objects.filter(
                Q(normalized_text__icontains=strip_diacritics(query)) | Q(arabic_text__icontains=query)
            ).values_list('id', flat=True)
        )
        if not self.matched_word_ids:
            return Ayah.objects.none()

        ayah_ids = WordOccurrence.objects.filter(
            word_id__in=self.matched_word_ids
        ).values_list('ayah_id', flat=True).distinct()

        return Ayah.objects.filter(id__in=ayah_ids).select_related('surah').prefetch_related(
            Prefetch('word_occurrences', queryset=WordOccurrence.objects.order_by('position'))
        ).order_by('surah__number', 'ayah_number')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['matched_word_ids'] = getattr(self, 'matched_word_ids', set())
        context['portion_word_limit'] = SEARCH_PORTION_WORD_LIMIT
        return context


class WordPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


def _word_queryset():
    return Word.objects.select_related('note').prefetch_related('meanings').annotate(
        occurrence_count=Count('occurrences', distinct=True)
    )


class WordListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordListSerializer
    pagination_class = WordPagination
    ALLOWED_ORDERINGS = {'arabic_text', '-arabic_text', 'occurrence_count', '-occurrence_count'}

    def _search_filtered_queryset(self):
        queryset = _word_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(normalized_text__icontains=strip_diacritics(search)) | Q(note__root__icontains=search)
            ).distinct()
        return queryset

    def get_queryset(self):
        queryset = self._search_filtered_queryset()
        params = self.request.query_params

        is_meaning_final = params.get('is_meaning_final')
        if is_meaning_final is not None:
            queryset = queryset.filter(is_meaning_final=is_meaning_final.lower() in ('true', '1'))

        has_meaning = params.get('has_meaning')
        if has_meaning is not None:
            if has_meaning.lower() in ('true', '1'):
                queryset = queryset.filter(meanings__isnull=False).distinct()
            else:
                queryset = queryset.filter(meanings__isnull=True)

        ordering = params.get('ordering', 'arabic_text')
        if ordering not in self.ALLOWED_ORDERINGS:
            ordering = 'arabic_text'

        return queryset.order_by(ordering)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        base = self._search_filtered_queryset()
        response.data['counts'] = {
            'all': base.count(),
            'complete': base.filter(is_meaning_final=True).count(),
            'incomplete': base.filter(is_meaning_final=False).count(),
        }
        return response


class WordDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordDetailSerializer
    queryset = Word.objects.prefetch_related(
        'meanings', 'note', 'occurrences__ayah', 'occurrences__meaning'
    )
    http_method_names = ['get', 'patch', 'head', 'options']


class WordNoteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordNoteSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        word = get_object_or_404(Word, pk=self.kwargs['word_id'])
        note, _ = WordNote.objects.get_or_create(word=word)
        return note


class WordOccurrenceAnalysisView(generics.GenericAPIView):
    """Backs the Word Grammatical Analysis modal's single Save button, which
    edits three different things at once: the occurrence's meaning override
    (per-ayah override path from CLAUDE.md's "Word meaning: default +
    override" design — matching text on the same word is reused so repeated
    overrides don't fork duplicate WordMeaning rows), the word's shared note/
    grammar fields, and the word's is_meaning_final flag. These used to be
    three independent endpoints/requests, each deciding on its own whether
    to log an ActivityLog row — so a save that touched more than one of them
    produced multiple rows for what the client experienced as one action.
    Consolidated here: exactly one ActivityLog row per Save click, however
    many of the three things actually changed (client-requested)."""

    permission_classes = [IsAuthenticated]
    queryset = WordOccurrence.objects.select_related('word', 'ayah', 'meaning')
    http_method_names = ['patch', 'head', 'options']

    def patch(self, request, *args, **kwargs):
        occurrence = self.get_object()
        word = occurrence.word
        content_changed = False
        finalized = False
        is_first_meaning_added = False

        meaning_text = (request.data.get('meaning_text') or '').strip()
        if meaning_text:
            current_text = occurrence.meaning.meaning_text if occurrence.meaning_id else None
            if meaning_text != current_text:
                is_first_meaning_added = not WordMeaning.objects.filter(word=word).exists()
                meaning = WordMeaning.objects.filter(word=word, meaning_text=meaning_text).first()
                if meaning is None:
                    meaning = WordMeaning.objects.create(word=word, meaning_text=meaning_text)
                occurrence.meaning = meaning
                occurrence.save(update_fields=['meaning'])
                content_changed = True

        note_data = request.data.get('note')
        if note_data is not None:
            note, _ = WordNote.objects.get_or_create(word=word)
            note_serializer = WordNoteSerializer(note, data=note_data, partial=True)
            note_serializer.is_valid(raise_exception=True)
            if any(
                getattr(note, field) != value for field, value in note_serializer.validated_data.items()
            ):
                note_serializer.save()
                content_changed = True

        if 'is_meaning_final' in request.data:
            new_final = bool(request.data['is_meaning_final'])
            if new_final != word.is_meaning_final:
                word.is_meaning_final = new_final
                word.save(update_fields=['is_meaning_final'])
                # Only False->True reads as "finalized" — reverting Final
                # back off is just a generic content-ish change.
                if new_final:
                    finalized = True
                else:
                    content_changed = True

        if content_changed or finalized:
            ActivityLog.objects.create(
                user=request.user,
                action_type=(
                    ActivityLog.ActionType.WORD_MEANING_ADDED
                    if is_first_meaning_added
                    else ActivityLog.ActionType.WORD_MEANING_UPDATED
                ),
                ayah=occurrence.ayah,
                word=word,
                content_changed=content_changed,
                finalized=finalized,
            )

        return Response(WordOccurrenceSerializer(occurrence).data)


class WordMeaningListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordMeaningSerializer

    def get_queryset(self):
        return WordMeaning.objects.filter(word_id=self.kwargs['word_id'])

    def perform_create(self, serializer):
        word = get_object_or_404(Word, pk=self.kwargs['word_id'])
        serializer.save(word=word)


class WordMeaningDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordMeaningSerializer
    queryset = WordMeaning.objects.all()
    http_method_names = ['patch', 'delete', 'head', 'options']

    def perform_destroy(self, instance):
        if not instance.is_default:
            default_meaning = WordMeaning.objects.filter(
                word=instance.word, is_default=True
            ).first()
            WordOccurrence.objects.filter(meaning=instance).update(meaning=default_meaning)
        instance.delete()


class WordMeaningSetDefaultView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordMeaningSerializer
    queryset = WordMeaning.objects.all()
    http_method_names = ['patch', 'head', 'options']

    def patch(self, request, *args, **kwargs):
        meaning = self.get_object()

        old_default = WordMeaning.objects.filter(
            word=meaning.word, is_default=True
        ).exclude(pk=meaning.pk).first()
        if old_default:
            WordOccurrence.objects.filter(word=meaning.word, meaning=old_default).update(
                meaning=meaning
            )
            old_default.is_default = False
            old_default.save(update_fields=['is_default'])

        meaning.is_default = True
        meaning.save(update_fields=['is_default'])

        return Response(self.get_serializer(meaning).data)


class DashboardSummaryView(generics.GenericAPIView):
    """Aggregate counts for the Dashboard's stat/progress cards. See
    CLAUDE.md's "Data/semantic note" for the surah-started definition (union
    of in-progress + Final surahs, matching SurahSerializer.get_status)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        surahs_total = Surah.objects.count()
        surahs_not_started = Surah.objects.annotate(
            final_ayah_count=Count('ayahs', filter=Q(ayahs__status=Ayah.Status.FINAL))
        ).filter(final_ayah_count=0).count()

        ayahs_total = Ayah.objects.count()
        ayahs_final = Ayah.objects.filter(status=Ayah.Status.FINAL).count()

        words_total = Word.objects.count()
        words_final = Word.objects.filter(is_meaning_final=True).count()

        # Per-ayah word-entry progress: an ayah counts as complete only when
        # EVERY one of its words has been marked is_meaning_final=True (the
        # client-driven "final" flag) — not merely that every occurrence has
        # some meaning assigned. word_count__gt=0 guards against a hypothetical
        # zero-word ayah trivially matching word_count == final_word_count.
        per_ayah_word_final = Ayah.objects.annotate(
            word_count=Count('word_occurrences'),
            final_word_count=Count(
                'word_occurrences', filter=Q(word_occurrences__word__is_meaning_final=True)
            ),
        ).filter(word_count__gt=0, word_count=F('final_word_count')).count()

        return Response({
            'surahs_started': surahs_total - surahs_not_started,
            'surahs_total': surahs_total,
            'ayahs_final': ayahs_final,
            'ayahs_total': ayahs_total,
            'word_meaning_final': words_final,
            'word_meaning_total': words_total,
            'per_ayah_word_final': per_ayah_word_final,
            'per_ayah_word_total': ayahs_total,
        })


class ActivityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


ACTIVITY_RANGE_DAYS = {'7d': 7, '1m': 30, '6m': 180, '1y': 365}


class ActivityLogListView(generics.ListAPIView):
    """Dashboard Recent Activity feed. With no `range` param, returns the
    full unfiltered list (paginated) — the time-range pills narrow it down
    only once the client picks one, they don't apply a default filter."""

    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer
    pagination_class = ActivityPagination

    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('ayah__surah', 'word').order_by('-created_at')
        days = ACTIVITY_RANGE_DAYS.get(self.request.query_params.get('range'))
        if days is not None:
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=days))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        entries = page if page is not None else list(queryset)

        pairs = {(entry.ayah_id, entry.word_id) for entry in entries if entry.ayah_id and entry.word_id}
        occurrence_map = {}
        if pairs:
            ayah_ids, word_ids = zip(*pairs)
            for occurrence in WordOccurrence.objects.filter(
                ayah_id__in=set(ayah_ids), word_id__in=set(word_ids)
            ):
                key = (occurrence.ayah_id, occurrence.word_id)
                occurrence_map.setdefault(key, occurrence.id)

        serializer = self.get_serializer(entries, many=True, context={
            **self.get_serializer_context(), 'occurrence_map': occurrence_map,
        })
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
