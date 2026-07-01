from django.db import models

from apps.quran.services.text_normalizer import strip_diacritics


class Surah(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    name_arabic = models.TextField()
    name_bangla = models.TextField()
    name_english = models.TextField()
    total_ayah = models.PositiveIntegerField()

    class Meta:
        db_table = 'surah'
        ordering = ['number']

    def __str__(self):
        return f'{self.number}. {self.name_english}'


class Ruku(models.Model):
    ruku_number = models.PositiveSmallIntegerField(unique=True)
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='rukus')
    surah_ruku_number = models.PositiveSmallIntegerField()
    first_verse_id = models.PositiveIntegerField()
    last_verse_id = models.PositiveIntegerField()
    verses_count = models.PositiveIntegerField()

    class Meta:
        db_table = 'ruku'
        ordering = ['ruku_number']

    def __str__(self):
        return f'Ruku {self.ruku_number} ({self.surah.name_english} R{self.surah_ruku_number})'


class Ayah(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        FINAL = 'final', 'Final'

    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='ayahs')
    ruku = models.ForeignKey(
        Ruku, on_delete=models.SET_NULL, null=True, blank=True, related_name='ayahs'
    )
    ayah_number = models.PositiveIntegerField()
    verse_key = models.CharField(max_length=10, unique=True)
    arabic_text = models.TextField()
    translation_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ayah'
        ordering = ['surah__number', 'ayah_number']

    def __str__(self):
        return self.verse_key


class Word(models.Model):
    arabic_text = models.TextField(unique=True)
    normalized_text = models.TextField(blank=True, editable=False)
    is_meaning_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'word'

    def __str__(self):
        return self.arabic_text

    def save(self, *args, **kwargs):
        self.normalized_text = strip_diacritics(self.arabic_text)
        super().save(*args, **kwargs)


class WordMeaning(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')
    meaning_text = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'word_meaning'

    def __str__(self):
        return self.meaning_text

    def save(self, *args, **kwargs):
        # First meaning ever added to a word becomes the default, and every
        # existing occurrence of that word (all unassigned at this point)
        # is backfilled to point at it.
        is_first_meaning = self._state.adding and not WordMeaning.objects.filter(
            word=self.word
        ).exists()
        if is_first_meaning:
            self.is_default = True

        super().save(*args, **kwargs)

        if is_first_meaning:
            WordOccurrence.objects.filter(word=self.word).update(meaning=self)


class WordOccurrence(models.Model):
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name='word_occurrences')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='occurrences')
    position = models.PositiveIntegerField()
    meaning = models.ForeignKey(
        WordMeaning,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='occurrences',
    )

    class Meta:
        db_table = 'word_occurrence'
        ordering = ['ayah', 'position']
        constraints = [
            models.UniqueConstraint(fields=['ayah', 'position'], name='unique_ayah_position'),
        ]

    def __str__(self):
        return f'{self.ayah.verse_key} #{self.position}'


class WordNote(models.Model):
    class PartOfSpeech(models.TextChoices):
        NOUN = 'noun', 'Noun'
        VERB = 'verb', 'Verb'
        PARTICLE = 'particle', 'Particle'
        OTHER = 'other', 'Other'

    word = models.OneToOneField(Word, on_delete=models.CASCADE, related_name='note')
    meaning_basra = models.TextField(blank=True)
    meaning_kufa = models.TextField(blank=True)
    root = models.CharField(max_length=100, blank=True)
    part_of_speech = models.CharField(
        max_length=20, choices=PartOfSpeech.choices, blank=True
    )
    verb_form = models.CharField(max_length=50, blank=True)
    morphology = models.CharField(max_length=255, blank=True)
    derived_forms = models.TextField(blank=True)
    lemma = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'word_note'

    def __str__(self):
        return f'Note for {self.word.arabic_text}'
