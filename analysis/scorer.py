from dataclasses import dataclass
from typing import List, Dict

from sources.base import SignalDoc
from .taxonomy import classify
from .normalize import normalize_kw

NEGATIVE_PHRASES = [
    "고양이", "강아지", "신생아", "성인", "군대", "연애", "직장",
    "영어로", "영어 로"
]

@dataclass
class IssueItem:
    phrase: str
    category: str
    score: float
    evidence: List[str]  # URL 또는 타이틀(중복 제거됨)

def build_issues_from_docs(
    docs: List[SignalDoc],
    taxonomy_boost: Dict[str, float],
    source_weights: Dict[str, float]
) -> List[IssueItem]:
    bucket: Dict[str, IssueItem] = {}

    for d in docs:
        # 문서에서 “관심사 후보 phrase”를 뽑는 규칙:
        # - RSS: title
        # - Trends: text(키워드)
        # - Naver: title 우선(없으면 text)
        if d.source == "rss_news":
            text = d.title
        elif d.source == "google_trends":
            text = d.text
        else:
            text = d.title or d.text

        text = normalize_kw(text)

        if not text:
            continue
        if any(n in text for n in NEGATIVE_PHRASES):
            continue

        cat, raw = classify(text)
        boost = taxonomy_boost.get(cat, 1.0)
        sw = source_weights.get(d.source, 1.0)

        trend_bonus = 1.0

        # Trends는 rising/value 반영
        if d.source == "google_trends":
            kind = d.meta.get("kind")
            val = d.meta.get("value")
            if kind == "rising":
                trend_bonus *= 1.35
            elif kind == "top":
                trend_bonus *= 1.05
            if isinstance(val, (int, float)):
                trend_bonus *= (1.0 + min(float(val), 100.0) / 600.0)

        # Naver는 최신 정렬(date)을 쓰므로 약간 가산
        if d.source in ("naver_cafearticle", "naver_blog", "naver_news"):
            trend_bonus *= 1.10

        base_score = (raw if raw > 0 else 0.6) * boost * sw * trend_bonus

        key = text
        if key not in bucket:
            bucket[key] = IssueItem(
                phrase=key,
                category=cat,
                score=base_score,
                evidence=[]
            )
        else:
            bucket[key].score += base_score

        # ✅ evidence는 중복 제거해서 저장
        ev = d.url or d.title
        if ev and ev not in bucket[key].evidence:
            bucket[key].evidence.append(ev)

    return sorted(bucket.values(), key=lambda x: x.score, reverse=True)
