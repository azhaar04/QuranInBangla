from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.quran.models import Ruku, Surah
from apps.quran.serializers import RukuSerializer, SurahSerializer


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
