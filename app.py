from config import AppConfig
from profiles.brainology_newton import PROFILE

from sources.google_trends import GoogleTrendsSource
from sources.rss_news import RssNewsSource
from sources.naver_search import NaverSearchSource

from analysis.expander import expand_queries
from analysis.taxonomy import TAXONOMY_RULES
from analysis.scorer import build_issues_from_docs

import requests


def build_slack_message_top7(profile, issues, top_n: int = 7, link_n: int = 5) -> str:
    """
    Slack에는 '상위 7개 이슈 + 관련 링크'만 보내기.
    """
    lines = []
    lines.append(f"✅ *{profile.product}*와 관련된 최근 이슈입니다! 콘텐츠 기획에 참고하셔도 좋습니다!")
    lines.append(f"*상위 {top_n}개 이슈 + 관련 링크(최대 {link_n}개)*")
    lines.append("")

    top_items = issues[:top_n]
    for i, it in enumerate(top_items, 1):
        lines.append(f"*[{i}]* ({it.category}) {it.phrase}  | score={it.score:.2f}")

        links = []
        for ev in it.evidence:
            if isinstance(ev, str) and ev.startswith("http"):
                links.append(ev)

        if links:
            for url in links[:link_n]:
                lines.append(f"   • {url}")
        else:
            # 링크가 없으면(예: Trends) 근거 텍스트 일부
            for ev in it.evidence[:link_n]:
                lines.append(f"   • {ev}")

        lines.append("")

    return "\n".join(lines)


def post_to_slack(webhook_url: str, text: str) -> bool:
    payload = {"text": text}
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        return 200 <= r.status_code < 300
    except requests.RequestException:
        return False


def main():
    cfg = AppConfig()

    # 1) 쿼리 확장(롱테일)
    expanded = expand_queries(PROFILE.seed_queries, max_out=80)

    # 2) 소스 초기화
    sources = []

    if cfg.naver_client_id and cfg.naver_client_secret:
        sources.append(NaverSearchSource(
            client_id=cfg.naver_client_id,
            client_secret=cfg.naver_client_secret,
            display=cfg.naver_display,
            max_queries=cfg.naver_max_queries
        ))
    else:
        print("[WARN] NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 없어 네이버 검색 API를 스킵합니다.")

    sources.append(GoogleTrendsSource())
    sources.append(RssNewsSource(feeds=cfg.rss_feeds))

    # 3) 수집
    docs = []
    for src in sources:
        try:
            docs.extend(src.fetch(expanded, cfg.recency_days))
        except Exception as e:
            print(f"[WARN] source failed: {getattr(src, 'name', 'unknown')} -> {e}")

    # 4) RSS gate (노이즈 줄이기)
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

    # 콘솔에는 TOP 30 유지
    for i, it in enumerate(issues[:30], 1):
        print(f"{i:02d}. ({it.category}) {it.phrase}  | score={it.score:.2f}")

    # 콘솔에는 상위 7개 링크도 출력
    print("\n상위 7개 이슈 + 관련 링크(중복 제거)\n")
    top7 = issues[:7]
    for i, it in enumerate(top7, 1):
        print(f"[{i}] ({it.category}) {it.phrase}  | score={it.score:.2f}")
        links = [ev for ev in it.evidence if isinstance(ev, str) and ev.startswith("http")]
        if links:
            for j, url in enumerate(links[:5], 1):
                print(f"   - {j}. {url}")
        else:
            for j, ev in enumerate(it.evidence[:5], 1):
                print(f"   - {j}. {ev}")
        print()

    # ✅ Slack에는 TOP 7만 전송
    if cfg.slack_webhook_url:
        slack_text = build_slack_message_top7(PROFILE, issues, top_n=7, link_n=5)
        ok = post_to_slack(cfg.slack_webhook_url, slack_text)
        if ok:
            print("[INFO] Slack 전송 완료 (상위 7개만)")
        else:
            print("[WARN] Slack 전송 실패(웹훅 URL/네트워크/권한 확인 필요)")
    else:
        print("[INFO] SLACK_WEBHOOK_URL 환경변수가 없어 Slack 전송을 스킵합니다.")


if __name__ == "__main__":
    main()
