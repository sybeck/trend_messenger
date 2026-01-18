import re

def normalize_kw(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = s.replace("영어 로", "영어로")
    return s
