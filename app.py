from config import AppConfig
from profiles.brainology_newton import PROFILE

from sources.google_trends import GoogleTrendsSource
from sources.rss_news import RssNewsSource
from sources.naver_search import NaverSearchSource

from analysis.expander import expand_queries
from analysis.taxonomy import TAXONOMY_RULES
from analysis.scorer import build_issues_from_docs


def main():
    cfg = AppConfig()

    # 1) 쿼리 확장(롱테일)
    expanded = expand_queries(PROFILE.seed_queries, max_out=80)

    # 2) 소스 초기화
    sources = []

    # (A) 네이버 검색 API (가장 추천)
    if cfg.naver_client_id and cfg.naver_client_secret:
        sources.append(NaverSearchSource(
            client_id=cfg.naver_client_id,
            client_secret=cfg.naver_client_secret,
            display=cfg.naver_display,
            max_queries=cfg.naver_max_queries
        ))
    else:
        print("[WARN] NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 없어 네이버 검색 API를 스킵합니다.")

    # (B) Google Trends (되면 쓰고, 막히면 캐시/백오프로 완화)
    sources.append(GoogleTrendsSource())

    # (C) RSS (육아/교육 특화 피드 여러 개)
    sources.append(RssNewsSource(feeds=cfg.rss_feeds))

    # 3) 수집
    docs = []
    for src in sources:
        try:
            docs.extend(src.fetch(expanded, cfg.recency_days))
        except Exception as e:
            print(f"[WARN] source failed: {getattr(src, 'name', 'unknown')} -> {e}")

    # 4) RSS는 게이트 키워드로 완화 필터
    rss_gate_words = set()
    for kws in TAXONOMY_RULES.values():
        for kw in kws:
            rss_gate_words.add(kw)

    filtered_docs = []
    for d in docs:
        if d.source == "rss_news":
            joined = (d.title + " " + d.text)
            if any(w in joined for w in rss_gate_words):
                filtered_docs.append(d)
        else:
            filtered_docs.append(d)

    if cfg.debug:
        by_src = {}
        for d in docs:
            by_src[d.source] = by_src.get(d.source, 0) + 1
        print(f"[DEBUG] expanded_queries={len(expanded)}")
        print(f"[DEBUG] docs_total={len(docs)} | docs_after_filter={len(filtered_docs)}")
        print(f"[DEBUG] docs_by_source={by_src}")
        print("[DEBUG] sample_titles:", [x.title for x in filtered_docs[:8]])

    # 5) 이슈 생성
    issues = build_issues_from_docs(filtered_docs, PROFILE.taxonomy_boost, cfg.source_weights)

    print(f"\n[{PROFILE.brand} - {PROFILE.product}] {PROFILE.target} / {PROFILE.age_range}")
    print("최근 관심사/걱정/문제 후보 TOP 30\n")

    if not issues:
        print("[WARN] 추출된 이슈가 0개입니다.")
        print("- 네이버 API 키가 없거나, 네트워크/요청 제한일 수 있어요.")
        print("- RSS 피드가 일시적으로 비었을 수 있어요.")
        return

    # TOP 30 키워드 출력
    for i, it in enumerate(issues[:30], 1):
        print(f"{i:02d}. ({it.category}) {it.phrase}  | score={it.score:.2f}")

    # ✅ 상위 5개 이슈 + 관련 링크(중복 제거된 evidence에서 링크만 추출)
    print("\n상위 5개 이슈 + 관련 링크(중복 제거)\n")

    top5 = issues[:5]
    for i, it in enumerate(top5, 1):
        print(f"[{i}] ({it.category}) {it.phrase}  | score={it.score:.2f}")

        links = []
        for ev in it.evidence:
            if isinstance(ev, str) and ev.startswith("http"):
                links.append(ev)

        if links:
            for j, url in enumerate(links[:5], 1):
                print(f"   - {j}. {url}")
        else:
            # 링크가 없으면(예: Trends) 타이틀/키워드를 근거로 표시
            for j, ev in enumerate(it.evidence[:5], 1):
                print(f"   - {j}. {ev}")

        print()  # 줄바꿈

    # 상위 1개 근거 링크 샘플(디버그)
    if cfg.debug and issues:
        top = issues[0]
        print("\n[DEBUG] Top issue evidence samples:")
        for ev in top.evidence[:5]:
            print("-", ev)


if __name__ == "__main__":
    main()
