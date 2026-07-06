from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.quran.models import Ayah, Ruku, Surah
from apps.quran.serializers import AyahSerializer, RukuSerializer, SurahSerializer


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
