from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.quran.models import Ayah, Ruku, Surah, Word, WordMeaning, WordOccurrence
from apps.quran.serializers import (
    AyahSerializer,
    RukuSerializer,
    SurahSerializer,
    WordDetailSerializer,
    WordMeaningSerializer,
    WordSerializer,
)
from apps.quran.services.text_normalizer import strip_diacritics


class SurahListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Surah.objects.all()
    serializer_class = SurahSerializer


class SurahDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SurahSerializer
    lookup_field = 'number'
    lookup_url_kwarg = 'surah_number'
    queryset = Surah.objects.all()


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


class WordListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordSerializer

    def get_queryset(self):
        queryset = Word.objects.prefetch_related('meanings', 'note')
        params = self.request.query_params

        search = params.get('search')
        if search:
            queryset = queryset.filter(normalized_text__icontains=strip_diacritics(search))

        is_meaning_final = params.get('is_meaning_final')
        if is_meaning_final is not None:
            queryset = queryset.filter(is_meaning_final=is_meaning_final.lower() in ('true', '1'))

        has_meaning = params.get('has_meaning')
        if has_meaning is not None:
            if has_meaning.lower() in ('true', '1'):
                queryset = queryset.filter(meanings__isnull=False).distinct()
            else:
                queryset = queryset.filter(meanings__isnull=True)

        part_of_speech = params.get('part_of_speech')
        if part_of_speech:
            queryset = queryset.filter(note__part_of_speech=part_of_speech)

        return queryset.order_by('arabic_text')


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
