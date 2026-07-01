import pyarabic.araby as araby


def strip_diacritics(text: str) -> str:
    """Strip Arabic diacritics (harakat/tashkeel) for diacritics-insensitive search."""
    return araby.strip_tashkeel(text)
