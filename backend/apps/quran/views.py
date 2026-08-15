from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.quran.models import ActivityLog, Ayah, Ruku, Surah, Word, WordMeaning, WordOccurrence
from apps.quran.serializers import (
    AyahSerializer,
    RukuSerializer,
    SurahSerializer,
    WordDetailSerializer,
    WordListSerializer,
    WordMeaningSerializer,
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


class RukuListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Ruku.objects.all()
    serializer_class = RukuSerializer


class RukuDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RukuSerializer
    lookup_field = 'ruku_number'
    queryset = Ruku.objects.all()


class SurahRukuListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RukuSerializer

    def get_queryset(self):
        return Ruku.objects.filter(surah__number=self.kwargs['surah_number'])


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

        ayah = serializer.save()

        if ayah.translation_text == old_translation_text and ayah.notes == old_notes:
            return

        ActivityLog.objects.create(
            user=self.request.user,
            action_type=(
                ActivityLog.ActionType.AYAH_UPDATED
                if had_content_before
                else ActivityLog.ActionType.AYAH_TRANSLATED
            ),
            ayah=ayah,
        )


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
