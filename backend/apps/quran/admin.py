from django.contrib import admin

from apps.quran.models import (
    ActivityLog,
    Ayah,
    Ruku,
    Surah,
    Word,
    WordMeaning,
    WordNote,
    WordOccurrence,
)


@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('id','number', 'name_english', 'name_bangla', 'name_arabic', 'total_ayah')
    search_fields = ('name_english', 'name_bangla', 'name_arabic')
    ordering = ('number',)


@admin.register(Ruku)
class RukuAdmin(admin.ModelAdmin):
    list_display = ('ruku_number', 'surah', 'surah_ruku_number', 'verses_count')
    list_filter = ('surah',)
    ordering = ('ruku_number',)


class WordOccurrenceInline(admin.TabularInline):
    model = WordOccurrence
    extra = 0
    fields = ('position', 'word', 'meaning')
    readonly_fields = ('position', 'word')
    ordering = ('position',)


@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ('verse_key', 'surah', 'ayah_number', 'status', 'updated_at')
    list_filter = ('status', 'surah')
    search_fields = ('verse_key', 'arabic_text', 'translation_text')
    readonly_fields = ('arabic_text', 'created_at', 'updated_at')
    inlines = [WordOccurrenceInline]


class WordMeaningInline(admin.TabularInline):
    model = WordMeaning
    extra = 0
    fields = ('meaning_text', 'is_default')


class WordNoteInline(admin.StackedInline):
    model = WordNote
    extra = 0
    can_delete = False


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('arabic_text', 'normalized_text', 'is_meaning_final', 'updated_at')
    search_fields = ('arabic_text', 'normalized_text')
    readonly_fields = ('normalized_text', 'created_at', 'updated_at')
    inlines = [WordMeaningInline, WordNoteInline]


@admin.register(WordMeaning)
class WordMeaningAdmin(admin.ModelAdmin):
    list_display = ('word', 'meaning_text', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('meaning_text', 'word__arabic_text')


@admin.register(WordOccurrence)
class WordOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('ayah', 'position', 'word', 'raw_text', 'meaning')
    list_filter = ('meaning__is_default',)
    search_fields = ('ayah__verse_key', 'word__arabic_text')


@admin.register(WordNote)
class WordNoteAdmin(admin.ModelAdmin):
    list_display = ('word', 'root', 'updated_at')
    search_fields = ('word__arabic_text', 'root')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action_type', 'ayah', 'word')
    list_filter = ('action_type', 'user')
    search_fields = ('user__username', 'ayah__verse_key', 'word__arabic_text')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
