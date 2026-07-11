from rest_framework import serializers

from apps.quran.models import Ayah, Ruku, Surah, Word, WordMeaning, WordNote, WordOccurrence


class SurahSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surah
        fields = ['id', 'number', 'name_arabic', 'name_bangla', 'name_english', 'total_ayah']


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
        read_only_fields = ['is_default']


class WordNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordNote
        fields = [
            'meaning_basra', 'meaning_kufa', 'root', 'part_of_speech',
            'verb_form', 'morphology', 'derived_forms', 'lemma', 'note', 'updated_at',
        ]


class WordSerializer(serializers.ModelSerializer):
    meanings = WordMeaningSerializer(many=True, read_only=True)
    note = WordNoteSerializer(read_only=True)

    class Meta:
        model = Word
        fields = ['id', 'arabic_text', 'normalized_text', 'is_meaning_final', 'meanings', 'note']
        read_only_fields = ['normalized_text']


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
