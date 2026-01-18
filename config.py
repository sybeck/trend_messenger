from dataclasses import dataclass, field
from typing import Dict, List
import os

from dotenv import load_dotenv

# =====================================
# .env 파일 로드 (프로젝트 루트 기준)
# =====================================
load_dotenv()


@dataclass
class AppConfig:
    # -----------------
    # 기본 설정
    # -----------------
    locale: str = "KR"
    language: str = "ko"
    recency_days: int = 30
    active_profile: str = "brainology_newton"
    debug: bool = True

    # -----------------
    # Naver Open API (from .env)
    # -----------------
    naver_client_id: str | None = field(
        default_factory=lambda: os.getenv("NAVER_CLIENT_ID")
    )
    naver_client_secret: str | None = field(
        default_factory=lambda: os.getenv("NAVER_CLIENT_SECRET")
    )

    # -----------------
    # Slack Incoming Webhook (from .env)
    # -----------------
    slack_webhook_url: str | None = field(
        default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL")
    )

    # -----------------
    # 소스 가중치
    # -----------------
    source_weights: Dict[str, float] = field(default_factory=lambda: {
        "naver_cafearticle": 1.35,
        "naver_blog": 1.10,
        "naver_news": 1.05,
        "google_trends": 0.85,
        "rss_news": 0.70,
    })

    # -----------------
    # RSS 피드 (육아/교육/정책)
    # -----------------
    rss_feeds: List[str] = field(default_factory=lambda: [
        # 베이비뉴스
        "https://www.ibabynews.com/rss/allArticle.xml",
        "https://www.ibabynews.com/rss/clickTop.xml",
        "https://www.ibabynews.com/rss/S1N1.xml",
        "https://www.ibabynews.com/rss/S1N2.xml",
        "https://www.ibabynews.com/rss/S1N3.xml",
        "https://www.ibabynews.com/rss/S1N4.xml",
        "https://www.ibabynews.com/rss/S1N5.xml",
        "https://www.ibabynews.com/rss/S1N6.xml",
        "https://www.ibabynews.com/rss/S2N36.xml",
        "https://www.ibabynews.com/rss/S2N37.xml",

        # 한국교육개발원(KEDI)
        "https://www.kedi.re.kr/khome/main/announce/rssAnnounceData.do?board_sq_no=1",
        "https://www.kedi.re.kr/khome/main/announce/rssAnnounceData.do?board_sq_no=2",
        "https://www.kedi.re.kr/khome/main/announce/rssSeminarData.do",
        "https://www.kedi.re.kr/khome/main/announce/rssAnnounceData.do?board_sq_no=3",
        "https://www.kedi.re.kr/khome/main/research/rssPubData.do",
        "https://www.kedi.re.kr/khome/main/journal/rssMZJournalData.do",
        "https://www.kedi.re.kr/khome/main/journal/rssEDJournalData.do",
        "https://www.kedi.re.kr/khome/main/journal/rssKDJournalData.do",
        "https://www.kedi.re.kr/khome/main/journal/rssEJJournalData.do",

        # 정책브리핑
        "https://www.korea.kr/rss/policy.xml",
        "https://www.korea.kr/rss/reporter.xml",
        "https://www.korea.kr/rss/insight.xml",
        "https://www.korea.kr/rss/fact.xml",
        "https://www.korea.kr/rss/pressrelease.xml",
        "https://www.korea.kr/rss/dept_moe.xml",
        "https://www.korea.kr/rss/dept_mw.xml",
        "https://www.korea.kr/rss/dept_mogef.xml",
    ])

    # -----------------
    # Naver API 호출 옵션
    # -----------------
    naver_max_queries: int = 25
    naver_display: int = 10
