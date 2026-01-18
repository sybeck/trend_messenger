from __future__ import annotations

import json
import os
import random
import re
import time
from datetime import datetime
from html import unescape
from typing import List, Dict, Any, Optional

import requests

from .base import SignalSource, SignalDoc


def _strip_tags(s: str) -> str:
    if not s:
        return ""
    s = unescape(s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_naver_pubdate(s: str) -> Optional[datetime]:
    # 예: "Tue, 03 Dec 2019 16:08:41 +0900"
    if not s:
        return None
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z").astimezone()
    except Exception:
        return None


class NaverSearchSource(SignalSource):
    """
    네이버 검색 API 기반 (비로그인)
    - 카페글: /v1/search/cafearticle.json
    - 뉴스:   /v1/search/news.json
    - 블로그: /v1/search/blog.json
    """
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        display: int = 10,
        cache_dir: str = ".cache",
        max_queries: int = 25,
        sleep_range: tuple[float, float] = (0.25, 0.55),
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.display = max(1, min(display, 100))
        self.cache_dir = cache_dir
        self.max_queries = max_queries
        self.sleep_range = sleep_range
        os.makedirs(self.cache_dir, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "trend-messenger/1.0"
        })

    def _cache_path(self, kind: str, recency_days: int) -> str:
        day = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.cache_dir, f"naver_{kind}_{day}_{recency_days}.json")

    def _load_cache(self, kind: str, recency_days: int) -> Any | None:
        p = self._cache_path(kind, recency_days)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_cache(self, kind: str, recency_days: int, data: Any) -> None:
        p = self._cache_path(kind, recency_days)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _call(self, endpoint: str, query: str, sort: str = "date") -> Dict[str, Any] | None:
        url = f"https://openapi.naver.com/v1/search/{endpoint}.json"
        params = {
            "query": query,
            "display": self.display,
            "start": 1,
            "sort": sort,  # date|sim
        }

        max_retry = 5
        for attempt in range(max_retry):
            try:
                r = self.session.get(url, params=params, timeout=10)
                if r.status_code == 200:
                    return r.json()

                # 과호출/서버오류 대응
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep((2 ** attempt) + random.uniform(0.2, 0.8))
                    continue

                # 그 외는 실패로 처리
                return None

            except requests.RequestException:
                time.sleep((2 ** attempt) + random.uniform(0.2, 0.8))
        return None

    def fetch(self, queries: List[str], recency_days: int) -> List[SignalDoc]:
        """
        여기서는 'queries'를 그대로 다 때리지 않고,
        최대 max_queries개만 최신성 높은 롱테일부터 쓰는 걸 권장.
        """
        # 단순히 앞에서부터 자르되, 너무 짧은 쿼리는 뒤로 밀기
        qs = sorted(queries, key=lambda x: (len(x) < 6, -len(x)))
        qs = qs[: self.max_queries]

        docs: List[SignalDoc] = []

        # 카페글 / 뉴스 / 블로그 각각 캐시 사용
        for endpoint, source_name in [
            ("cafearticle", "naver_cafearticle"),
            ("news", "naver_news"),
            ("blog", "naver_blog"),
        ]:
            cached = self._load_cache(source_name, recency_days)
            if cached is not None:
                docs.extend(self._docs_from_cached(source_name, cached))
                continue

            collected = []
            for q in qs:
                data = self._call(endpoint, q, sort="date")
                time.sleep(random.uniform(*self.sleep_range))

                if not data or "items" not in data:
                    continue

                for it in data.get("items", []):
                    title = _strip_tags(it.get("title", ""))
                    desc = _strip_tags(it.get("description", ""))
                    link = it.get("link", "") or it.get("originallink", "")
                    pub = _parse_naver_pubdate(it.get("pubDate", ""))

                    if not title and not desc:
                        continue

                    collected.append({
                        "query": q,
                        "title": title,
                        "description": desc,
                        "link": link,
                        "pubDate": it.get("pubDate", ""),
                    })

                    docs.append(SignalDoc(
                        source=source_name,
                        title=title or q,
                        text=(title + " " + desc).strip(),
                        url=link,
                        published_at=pub,
                        meta={"query": q, "endpoint": endpoint}
                    ))

            self._save_cache(source_name, recency_days, collected)

        return docs

    def _docs_from_cached(self, source_name: str, cached_items: List[Dict[str, Any]]) -> List[SignalDoc]:
        docs: List[SignalDoc] = []
        for it in cached_items:
            q = it.get("query", "")
            title = it.get("title", "") or q
            desc = it.get("description", "")
            link = it.get("link", "")
            pub = _parse_naver_pubdate(it.get("pubDate", ""))

            docs.append(SignalDoc(
                source=source_name,
                title=title,
                text=(title + " " + desc).strip(),
                url=link,
                published_at=pub,
                meta={"query": q, "endpoint": it.get("endpoint", "")}
            ))
        return docs
