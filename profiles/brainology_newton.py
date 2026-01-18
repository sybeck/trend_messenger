from dataclasses import dataclass
from typing import List, Dict

@dataclass
class BrandProfile:
    brand: str
    product: str
    target: str
    age_range: str
    seed_queries: List[str]
    taxonomy_boost: Dict[str, float]

PROFILE = BrandProfile(
    brand="브레인올로지",
    product="뉴턴젤리",
    target="30-40대 엄마",
    age_range="5세 이상 자녀",
    seed_queries=[
        "아이 예민", "아이 짜증", "분리불안", "감정조절", "떼쓰기",
        "주의력", "집중력", "산만", "ADHD 의심", "유치원 적응", "초등 입학",
        "아이 잠", "잠투정", "밤에 자주 깨", "수면 루틴",
        "스마트폰 중독", "유튜브", "게임 집착",
        "한글 떼기", "수학", "또래관계", "친구 문제",
        "감기 자주", "면역", "비염",
    ],
    taxonomy_boost={
        "집중/주의": 1.35,
        "정서/예민": 1.30,
        "수면/루틴": 1.20,
        "디지털/스크린": 1.15,
        "학습/학교적응": 1.10,
        "또래/사회성": 1.05,
        "건강/면역": 0.95,
    }
)
