from django.urls import path

from apps.quran.views import (
    ActivityLogListView,
    AyahDetailView,
    DashboardSummaryView,
    RukuDetailView,
    RukuListView,
    SearchAyahView,
    SurahAyahListView,
    SurahDetailView,
    SurahListView,
    SurahRukuListView,
    WordDetailView,
    WordListView,
    WordMeaningDetailView,
    WordMeaningListView,
    WordMeaningSetDefaultView,
    WordNoteView,
    WordOccurrenceAnalysisView,
)

app_name = 'quran'

urlpatterns = [
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('dashboard/activity/', ActivityLogListView.as_view(), name='dashboard_activity'),
    path('surahs/', SurahListView.as_view(), name='surah_list'),
    path('surahs/<int:surah_number>/', SurahDetailView.as_view(), name='surah_detail'),
    path('surahs/<int:surah_number>/rukus/', SurahRukuListView.as_view(), name='surah_ruku_list'),
    path('surahs/<int:surah_number>/ayahs/', SurahAyahListView.as_view(), name='surah_ayah_list'),
    path('rukus/', RukuListView.as_view(), name='ruku_list'),
    path('rukus/<int:ruku_number>/', RukuDetailView.as_view(), name='ruku_detail'),
    path('search/', SearchAyahView.as_view(), name='ayah_search'),
    path('ayahs/<str:verse_key>/', AyahDetailView.as_view(), name='ayah_detail'),
    path('words/', WordListView.as_view(), name='word_list'),
    path('words/<int:pk>/', WordDetailView.as_view(), name='word_detail'),
    path('words/<int:word_id>/note/', WordNoteView.as_view(), name='word_note'),
    path('words/<int:word_id>/meanings/', WordMeaningListView.as_view(), name='word_meaning_list'),
    path('word-meanings/<int:pk>/', WordMeaningDetailView.as_view(), name='word_meaning_detail'),
    path(
        'word-meanings/<int:pk>/set-default/',
        WordMeaningSetDefaultView.as_view(),
        name='word_meaning_set_default',
    ),
    path(
        'word-occurrences/<int:pk>/analysis/',
        WordOccurrenceAnalysisView.as_view(),
        name='word_occurrence_analysis',
    ),
]
