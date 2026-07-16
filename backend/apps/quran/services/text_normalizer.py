import re
import pyarabic.araby as araby


def strip_diacritics(text: str) -> str:
    text = araby.strip_tashkeel(text)
    text = araby.strip_tatweel(text)  # ـ (tatweel) ও strip করবে
    text = re.sub(r'[\u06D6-\u06ED]', '', text)
    text = ' '.join(text.split())
    return text