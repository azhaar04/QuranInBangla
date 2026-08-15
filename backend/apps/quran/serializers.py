from rest_framework import serializers

from apps.quran.models import Ayah, Ruku, Surah, Word, WordMeaning, WordNote, WordOccurrence


class SurahSerializer(serializers.ModelSerializer):
    final_ayah_count = serializers.IntegerField(read_only=True)
    progress_percent = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Surah
        fields = [
            'id', 'number', 'name_arabic', 'name_bangla', 'name_english', 'total_ayah',
            'revelation_place', 'final_ayah_count', 'progress_percent', 'status',
        ]

    def get_progress_percent(self, obj):
        if not obj.total_ayah:
            return 0
        return round(obj.final_ayah_count / obj.total_ayah * 100)

    def get_status(self, obj):
        if obj.final_ayah_count == 0:
            return 'not_started'
        if obj.final_ayah_count == obj.total_ayah:
            return 'complete'
        return 'in_progress'


class RukuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruku
        fields = [
            'id', 'ruku_number', 'surah', 'surah_ruku_number',
            'first_verse_id', 'last_verse_id', 'verses_count',
        ]


class WordMeaningSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordMeaning
        fields = ['id', 'word', 'meaning_text', 'is_default']
        read_only_fields = ['word', 'is_default']


class WordNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordNote
        fields = [
            'root', 'meaning_basra', 'meaning_kufa', 'meaning_baghdad',
            'pattern', 'note_for_pattern', 'grammatical_information',
            'derived_forms', 'notes', 'updated_at',
        ]


class WordSerializer(serializers.ModelSerializer):
    meanings = WordMeaningSerializer(many=True, read_only=True)
    note = WordNoteSerializer(read_only=True)

    class Meta:
        model = Word
        fields = ['id', 'arabic_text', 'normalized_text', 'is_meaning_final', 'meanings', 'note']
        read_only_fields = ['normalized_text']


class WordListSerializer(serializers.ModelSerializer):
    root = serializers.CharField(source='note.root', read_only=True, default='')
    grammatical_information = serializers.CharField(
        source='note.grammatical_information', read_only=True, default=''
    )
    default_meaning = serializers.SerializerMethodField()
    occurrence_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Word
        fields = [
            'id', 'arabic_text', 'root', 'default_meaning',
            'grammatical_information', 'occurrence_count', 'is_meaning_final',
        ]

    def get_default_meaning(self, obj):
        default = next((meaning for meaning in obj.meanings.all() if meaning.is_default), None)
        return default.meaning_text if default else None


class WordOccurrenceForWordSerializer(serializers.ModelSerializer):
    ayah_verse_key = serializers.CharField(source='ayah.verse_key', read_only=True)
    meaning_text = serializers.CharField(
        source='meaning.meaning_text', read_only=True, default=None
    )

    class Meta:
        model = WordOccurrence
        fields = ['id', 'ayah', 'ayah_verse_key', 'position', 'meaning', 'meaning_text']
        read_only_fields = ['ayah', 'position']


class WordDetailSerializer(serializers.ModelSerializer):
    meanings = WordMeaningSerializer(many=True, read_only=True)
    note = WordNoteSerializer(read_only=True)
    occurrences = WordOccurrenceForWordSerializer(many=True, read_only=True)

    class Meta:
        model = Word
        fields = [
            'id', 'arabic_text', 'normalized_text', 'is_meaning_final',
            'meanings', 'note', 'occurrences',
        ]
        read_only_fields = ['arabic_text', 'normalized_text']


class WordOccurrenceSerializer(serializers.ModelSerializer):
    word_arabic_text = serializers.CharField(source='word.arabic_text', read_only=True)
    meaning_text = serializers.CharField(
        source='meaning.meaning_text', read_only=True, default=None
    )

    class Meta:
        model = WordOccurrence
        fields = ['id', 'position', 'word', 'word_arabic_text', 'meaning', 'meaning_text']
        read_only_fields = ['word']


class AyahSerializer(serializers.ModelSerializer):
    word_occurrences = WordOccurrenceSerializer(many=True, read_only=True)

    class Meta:
        model = Ayah
        fields = [
            'id', 'surah', 'ruku', 'ayah_number', 'verse_key', 'arabic_text',
            'translation_text', 'notes', 'status', 'word_occurrences',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['surah', 'ruku', 'ayah_number', 'verse_key', 'arabic_text']
