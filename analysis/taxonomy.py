import re
from typing import Dict, List, Tuple

TAXONOMY_RULES: Dict[str, List[str]] = {
    "집중/주의": ["집중", "산만", "주의력", "ADHD", "충동", "과잉행동"],
    "정서/예민": ["예민", "짜증", "분노", "불안", "감정조절", "떼쓰기", "분리불안"],
    "수면/루틴": ["잠", "수면", "밤에", "새벽", "루틴", "등원", "등교", "야뇨"],
    "디지털/스크린": ["스마트폰", "유튜브", "게임", "영상", "스크린", "중독"],
    "학습/학교적응": ["한글", "수학", "입학", "초등", "유치원", "학교", "숙제", "학습지"],
    "또래/사회성": ["친구", "왕따", "관계", "사회성", "놀이"],
    "건강/면역": ["감기", "면역", "비염", "알레르기", "아토피", "기침"],
}

def classify(text: str) -> Tuple[str, float]:
    t = (text or "").lower()
    best_cat, best_score = "기타", 0.0
    for cat, kws in TAXONOMY_RULES.items():
        score = 0
        for kw in kws:
            if re.search(re.escape(kw.lower()), t):
                score += 1
        if score > best_score:
            best_cat, best_score = cat, float(score)
    return best_cat, best_score
