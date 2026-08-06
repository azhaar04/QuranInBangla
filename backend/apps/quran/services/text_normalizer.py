import re

import pyarabic.araby as araby

# Quranic annotation block (U+06D6-U+06ED): waqf/pause signs, rub-el-hizb
# marker, sajdah marker, silent-letter/madd recitation marks.
# Built with chr()/hex codepoints (not literal characters or \u escapes in
# the source) so the codepoints stay unambiguous no matter what font/editor
# opens this file.
_ANNOTATION_START = 0x06D6
_ANNOTATION_END = 0x06ED
QURANIC_ANNOTATION_RANGE = '[{}-{}]'.format(chr(_ANNOTATION_START), chr(_ANNOTATION_END))

# Stray non-Arabic control characters occasionally leaking in from import
# (LEFT-TO-RIGHT MARK U+200E, RIGHT-TO-LEFT MARK U+200F) — invisible,
# not part of the Quran text at all.
STRAY_CONTROL_CHARS = '[{}{}]'.format(chr(0x200E), chr(0x200F))


def strip_diacritics(text: str) -> str:
    """
    Full diacritics strip — tashkeel, tatweel, and Quranic annotation
    marks all removed. Used for `word.normalized_text`, which powers
    diacritics-insensitive search. NOT used for word identity/dedup,
    because it also strips harakat, and two words differing only in
    harakat ARE meaningfully different words in this project.
    """
    text = araby.strip_tashkeel(text)
    text = araby.strip_tatweel(text)
    text = re.sub(QURANIC_ANNOTATION_RANGE, '', text)
    text = ' '.join(text.split())
    return text


def strip_quranic_annotations(text: str) -> str:
    """
    Removes ONLY positional/contextual Quranic marks (waqf signs,
    rub-el-hizb, sajdah marker, silent-letter marks) and stray control
    characters — keeps harakat/tashkeel intact.

    Use this to compute the canonical `Word.arabic_text` so the same
    lexical word never forks into multiple rows just because a mark
    happened to land on one occurrence of it (e.g. a waqf sign attached
    to a word at one position in the Quran, but not at another).
    """
    text = re.sub(QURANIC_ANNOTATION_RANGE, '', text)
    text = re.sub(STRAY_CONTROL_CHARS, '', text)
    text = ' '.join(text.split())
    return text