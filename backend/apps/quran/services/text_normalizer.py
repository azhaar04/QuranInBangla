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

# QPC-typesetting sukun variant (used in text_qpc_hafs). Numerically inside
# the Quranic-annotation block above, but linguistically a harakat (marks
# "no vowel"), not a waqf/pause/rub-el-hizb/sajdah mark. Client decision:
# sukun must stay in Word.arabic_text, so this codepoint is EXCLUDED from
# stripping in strip_quranic_annotations() (kept), while strip_diacritics()
# (used only for the search-oriented normalized_text field) still strips it.
_QPC_SUKUN_VARIANT = 0x06E1

# Same range as above, but as an explicit codepoint set with the sukun
# variant excluded — used only by strip_quranic_annotations().
_ANNOTATION_CODEPOINTS_KEEPING_SUKUN = (
    set(range(_ANNOTATION_START, _ANNOTATION_END + 1)) - {_QPC_SUKUN_VARIANT}
)

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
    characters — keeps harakat/tashkeel intact. KEEPS the QPC sukun-variant
    glyph (U+06E1) per client decision — sukun is a harakat, not a
    positional/contextual mark, and must remain part of word identity.

    Use this to compute the canonical `Word.arabic_text` so the same
    lexical word never forks into multiple rows just because a mark
    happened to land on one occurrence of it (e.g. a waqf sign attached
    to a word at one position in the Quran, but not at another).
    """
    text = ''.join(ch for ch in text if ord(ch) not in _ANNOTATION_CODEPOINTS_KEEPING_SUKUN)
    text = re.sub(STRAY_CONTROL_CHARS, '', text)
    text = ' '.join(text.split())
    return text