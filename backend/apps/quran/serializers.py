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
    first_ayah_number = serializers.SerializerMethodField()
    last_ayah_number = serializers.SerializerMethodField()

    class Meta:
        model = Ruku
        fields = [
            'id', 'ruku_number', 'surah', 'surah_ruku_number',
            'first_verse_id', 'last_verse_id', 'verses_count',
            'first_ayah_number', 'last_ayah_number',
        ]

    def get_first_ayah_number(self, obj):
        return self.context.get('ayah_numbers_by_id', {}).get(obj.first_verse_id)

    def get_last_ayah_number(self, obj):
        return self.context.get('ayah_numbers_by_id', {}).get(obj.last_verse_id)


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
        fields = ['id', 'position', 'word', 'word_arabic_text', 'raw_text', 'meaning', 'meaning_text']
        read_only_fields = ['word', 'raw_text']


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

    def validate(self, attrs):
        instance = self.instance
        target_status = attrs.get('status', instance.status if instance else Ayah.Status.DRAFT)

        if target_status == Ayah.Status.FINAL:
            translation_text = attrs.get(
                'translation_text', instance.translation_text if instance else ''
            )
            if not translation_text.strip():
                raise serializers.ValidationError(
                    {'status': 'পূর্ণ অনুবাদ ছাড়া আয়াত Final করা যাবে না।'}
                )
            if instance is not None and instance.word_occurrences.filter(meaning__isnull=True).exists():
                raise serializers.ValidationError(
                    {'status': 'প্রতিটি শব্দের অর্থ না থাকলে আয়াত Final করা যাবে না।'}
                )

        return attrs
