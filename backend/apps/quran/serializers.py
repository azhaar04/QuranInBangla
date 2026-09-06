from rest_framework import serializers

from apps.quran.models import ActivityLog, Ayah, Ruku, Surah, Word, WordMeaning, WordNote, WordOccurrence


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
        read_only_fields = ['updated_at']


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
    word_is_meaning_final = serializers.BooleanField(source='word.is_meaning_final', read_only=True)

    class Meta:
        model = WordOccurrence
        fields = [
            'id', 'position', 'word', 'word_arabic_text', 'raw_text', 'meaning', 'meaning_text',
            'word_is_meaning_final',
        ]
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


class ActivityLogSerializer(serializers.ModelSerializer):
    """Recent Activity feed row (Dashboard). Both `ayah`/`word` context fields
    on ActivityLog are nullable at the model level, but in practice every row
    created so far (AyahDetailView, WordOccurrenceAnalysisView) always sets
    `ayah` — this serializer stays defensive with `default=None` regardless,
    since ActivityLog itself doesn't enforce that at the DB layer."""

    surah_number = serializers.IntegerField(source='ayah.surah.number', read_only=True, default=None)
    surah_name_bangla = serializers.CharField(source='ayah.surah.name_bangla', read_only=True, default=None)
    ayah_number = serializers.IntegerField(source='ayah.ayah_number', read_only=True, default=None)
    verse_key = serializers.CharField(source='ayah.verse_key', read_only=True, default=None)
    word_arabic_text = serializers.CharField(source='word.arabic_text', read_only=True, default=None)
    word_occurrence_id = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'action_type', 'created_at', 'content_changed', 'finalized',
            'surah_number', 'surah_name_bangla', 'ayah_number', 'verse_key',
            'word_arabic_text', 'word_occurrence_id',
        ]

    def get_word_occurrence_id(self, obj):
        """The exact word_occurrence this log entry's edit happened on — lets
        the frontend reopen the Word Grammar modal on the right occurrence
        rather than just navigating to the ayah. A word can appear in many
        ayahs/surahs, but that's not actually ambiguous here: `ayah_id` on
        the log already pins down which specific ayah the edit happened in.
        The only real ambiguity is the same word repeating twice within that
        SAME ayah — this resolves it precisely instead of guessing "first
        occurrence". Bulk-resolved by the view into `occurrence_map` (same
        pattern as RukuAyahNumberContextMixin) to avoid N+1 queries."""

        return self.context.get('occurrence_map', {}).get((obj.ayah_id, obj.word_id))


class SearchResultSerializer(serializers.ModelSerializer):
    """One matched ayah for the word search page. `portion` is the full ayah
    (word-occurrence list) when it fits within `portion_word_limit`
    (context), otherwise a window of that size centered on the matched
    word — see SearchAyahView.get_queryset for how the match is found and
    _windowed_occurrences below for how the window is picked when the match
    sits too close to one edge of the ayah to center evenly."""

    surah_number = serializers.IntegerField(source='surah.number', read_only=True)
    surah_name_bangla = serializers.CharField(source='surah.name_bangla', read_only=True)
    is_full_ayah = serializers.SerializerMethodField()
    portion = serializers.SerializerMethodField()

    class Meta:
        model = Ayah
        fields = ['verse_key', 'surah_number', 'surah_name_bangla', 'ayah_number', 'is_full_ayah', 'portion']

    def _windowed_occurrences(self, obj):
        if not hasattr(obj, '_search_window'):
            matched_word_ids = self.context['matched_word_ids']
            limit = self.context['portion_word_limit']
            occurrences = list(obj.word_occurrences.all())
            total = len(occurrences)
            match_index = next(
                (i for i, occ in enumerate(occurrences) if occ.word_id in matched_word_ids), 0
            )

            if total <= limit:
                obj._search_window = (occurrences, True)
            else:
                left_avail = match_index
                right_avail = total - match_index - 1

                before = min(limit // 2, left_avail)
                after_needed = limit - 1 - before
                after = min(after_needed, right_avail)
                leftover = after_needed - after
                if leftover > 0:
                    before = min(before + leftover, left_avail)

                start = match_index - before
                end = match_index + after + 1
                obj._search_window = (occurrences[start:end], False)

        return obj._search_window

    def get_is_full_ayah(self, obj):
        return self._windowed_occurrences(obj)[1]

    def get_portion(self, obj):
        matched_word_ids = self.context['matched_word_ids']
        window, _ = self._windowed_occurrences(obj)
        return [
            {'text': occurrence.raw_text, 'is_match': occurrence.word_id in matched_word_ids}
            for occurrence in window
        ]
