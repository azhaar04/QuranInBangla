from django.urls import path

from apps.quran.views import SurahDetailView, SurahListView

app_name = 'quran'

urlpatterns = [
    path('surahs/', SurahListView.as_view(), name='surah_list'),
    path('surahs/<int:number>/', SurahDetailView.as_view(), name='surah_detail'),
]
