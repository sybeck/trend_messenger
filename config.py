from dataclasses import dataclass, field
from typing import Dict, List
import os

@dataclass
class AppConfig:
    locale: str = "KR"
    language: str = "ko"
    recency_days: int = 30
    active_profile: str = "brainology_newton"
    debug: bool = True

    # 네이버 Open API 키는 환경변수로 받는 방식(코드에 박지 않기)
    naver_client_id: str | None = field(default_factory=lambda: os.getenv("NAVER_CLIENT_ID"))
    naver_client_secret: str | None = field(default_factory=lambda: os.getenv("NAVER_CLIENT_SECRET"))

    # 소스 가중치(튜닝 포인트)
    source_weights: Dict[str, float] = field(default_factory=lambda: {
        "naver_cafearticle": 1.35,  # 엄마 관심사에 매우 직접적
        "naver_news": 1.05,
        "naver_blog": 1.10,
        "google_trends": 0.85,      # 429/변동성 때문에 살짝 낮춤
        "rss_news": 0.70,
    })

    # RSS 피드(육아/교육 특화 위주로 3~5개)
    rss_feeds = [
        # -------------------------
        # 베이비뉴스 (육아/교육 특화 + 인기/전체로 안정성 확보)
        # -------------------------
        "https://www.ibabynews.com/rss/allArticle.xml",
        "https://www.ibabynews.com/rss/clickTop.xml",
        "https://www.ibabynews.com/rss/S1N1.xml",  # 사회/정책
        "https://www.ibabynews.com/rss/S1N2.xml",  # 임신/출산
        "https://www.ibabynews.com/rss/S1N3.xml",  # 생활/건강
        "https://www.ibabynews.com/rss/S1N4.xml",  # 육아/교육
        "https://www.ibabynews.com/rss/S1N5.xml",  # 놀이/문화
        "https://www.ibabynews.com/rss/S1N6.xml",  # 오피니언
        "https://www.ibabynews.com/rss/S2N36.xml",  # 1분육아
        "https://www.ibabynews.com/rss/S2N37.xml",  # 종합
        # (원하면) "https://www.ibabynews.com/rss/S2N31.xml",  # 1터뷰
        # (원하면) "https://www.ibabynews.com/rss/S2N38.xml",  # 재테크칼럼 (육아비용/가계 관련)

        # -------------------------
        # 한국교육개발원(KEDI) - 교육정책/연구/포럼(‘요즘 교육 이슈’에 강함)
        # -------------------------
        "https://www.kedi.re.kr/khome/main/announce/rssAnnounceData.do?board_sq_no=1",  # 공지사항
        "https://www.kedi.re.kr/khome/main/announce/rssAnnounceData.do?board_sq_no=2",  # 입찰공고
        "https://www.kedi.re.kr/khome/main/announce/rssSeminarData.do",  # 행사·세미나
        "https://www.kedi.re.kr/khome/main/announce/rssAnnounceData.do?board_sq_no=3",  # 보도자료
        "https://www.kedi.re.kr/khome/main/research/rssPubData.do",  # 연구보고서
        "https://www.kedi.re.kr/khome/main/journal/rssMZJournalData.do",  # 교육정책포럼
        "https://www.kedi.re.kr/khome/main/journal/rssEDJournalData.do",  # 교육개발
        "https://www.kedi.re.kr/khome/main/journal/rssKDJournalData.do",  # 한국교육
        "https://www.kedi.re.kr/khome/main/journal/rssEJJournalData.do",  # KEDI Journal of Educational Policy

        # -------------------------
        # 보건복지부(MOHW) - 아이 건강/복지/지원정책 신호 잡기
        # -------------------------
        "http://www.mohw.go.kr/rss/board.es?mid=a10501010000&bid=0003&cg_code=C01",  # 공지사항
        "http://www.mohw.go.kr/rss/board.es?mid=a10501040000&bid=0003&cg_code=C03",  # 채용공고(필요없으면 삭제)
        "http://www.mohw.go.kr/rss/board.es?mid=a10502000000&bid=0025",  # 입찰안내(필요없으면 삭제)
        "http://www.mohw.go.kr/rss/board.es?mid=a10503000000&bid=0027",  # 보도자료
        "http://www.mohw.go.kr/rss/board.es?mid=a10409020000&bid=0026",  # 훈령/예규/고시/지침

        # -------------------------
        # 정책브리핑(korea.kr) - “교육부/복지부/가족부” 중심으로 부모 관심사 큰 흐름 잡기
        # -------------------------
        "https://www.korea.kr/rss/policy.xml",  # 정책뉴스
        "https://www.korea.kr/rss/reporter.xml",  # 국민이 말하는 정책
        "https://www.korea.kr/rss/insight.xml",  # 이슈인사이트
        "https://www.korea.kr/rss/fact.xml",  # 사실은 이렇습니다(이슈 반박/정정)
        "https://www.korea.kr/rss/pressrelease.xml",  # 보도자료
        "https://www.korea.kr/rss/dept_moe.xml",  # 교육부
        "https://www.korea.kr/rss/dept_mw.xml",  # 보건복지부
        "https://www.korea.kr/rss/dept_mogef.xml",  # 성평등가족부
    ]

    # 네이버 검색 API 호출량 제어(쿼리 너무 많이 쏘면 비효율)
    naver_max_queries: int = 25
    naver_display: int = 10  # 한 쿼리당 결과 개수(최대 100 가능)
