from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.quran.models import Surah
from apps.quran.serializers import SurahSerializer


class SurahListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Surah.objects.all()
    serializer_class = SurahSerializer


class SurahDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SurahSerializer
    lookup_field = 'number'
    queryset = Surah.objects.all()
    
