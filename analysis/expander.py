from typing import List

TEMPLATES = [
    "{base} 왜",
    "{base} 원인",
    "{base} 해결",
    "{base} 방법",
    "{base} 증상",
    "{base} 검사",
    "{base} 테스트",
    "{base} 체크리스트",
    "{base} 병원",
    "{base} 상담",
    "{base} 훈육",
    "{base} 루틴",
]

BASE_TOPICS = [
    "5세 산만",
    "6세 산만",
    "7세 산만",
    "초등 1학년 집중",
    "초등 입학 준비",
    "유치원 적응",
    "유치원 등원 거부",
    "분리불안 밤잠",
    "아이 예민 짜증",
    "감정조절 안됨",
    "틱 증상",
    "스마트폰 집착",
    "유튜브 끊기",
    "게임 집착",
    "학습지 하기 싫어",
    "글씨 쓰기 싫어",
    "한글 떼기 스트레스",
]

NEGATIVE = ["신생아", "고양이", "강아지", "성인", "군대", "연애", "직장"]

def expand_queries(seed_queries: List[str], max_out: int = 80) -> List[str]:
    out = []
    out.extend(seed_queries[:15])

    for base in BASE_TOPICS:
        for t in TEMPLATES:
            out.append(t.format(base=base).strip())

    uniq, seen = [], set()
    for q in out:
        if any(n in q for n in NEGATIVE):
            continue
        if q not in seen:
            seen.add(q)
            uniq.append(q)

    return uniq[:max_out]
