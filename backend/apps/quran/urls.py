from django.urls import path

from apps.quran.views import (
    RukuDetailView,
    RukuListView,
    SurahDetailView,
    SurahListView,
    SurahRukuListView,
)

app_name = 'quran'

urlpatterns = [
    path('surahs/', SurahListView.as_view(), name='surah_list'),
    path('surahs/<int:surah_number>/', SurahDetailView.as_view(), name='surah_detail'),
    path('surahs/<int:surah_number>/rukus/', SurahRukuListView.as_view(), name='surah_ruku_list'),
    path('rukus/', RukuListView.as_view(), name='ruku_list'),
    path('rukus/<int:ruku_number>/', RukuDetailView.as_view(), name='ruku_detail'),
]
