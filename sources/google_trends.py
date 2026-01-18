from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict, Any

from pytrends.request import TrendReq
from pytrends import exceptions as pytrends_ex

from .base import SignalSource, SignalDoc


class GoogleTrendsSource(SignalSource):
    name = "google_trends"

    def __init__(self, hl: str = "ko-KR", tz: int = 540, cache_dir: str = ".cache"):
        self.hl = hl
        self.tz = tz
        self.pytrends = TrendReq(hl=hl, tz=tz)
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_path(self, timeframe: str) -> str:
        day = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.cache_dir, f"trends_related_{day}_{timeframe}.json")

    def _load_cache(self, timeframe: str) -> Dict[str, Any] | None:
        p = self._cache_path(timeframe)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_cache(self, timeframe: str, data: Dict[str, Any]) -> None:
        p = self._cache_path(timeframe)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _docs_from_cached(self, cached: Dict[str, Any], timeframe: str) -> List[SignalDoc]:
        docs: List[SignalDoc] = []
        for seed, out in cached.items():
            for kind in ("top", "rising"):
                for item in out.get(kind, []):
                    kw = str(item.get("query", "")).strip()
                    if not kw:
                        continue
                    docs.append(SignalDoc(
                        source=self.name,
                        title=f"[{seed}] related_{kind}: {kw}",
                        text=kw,
                        url="",
                        published_at=None,
                        meta={"seed": seed, "kind": kind, "value": item.get("value"), "timeframe": timeframe}
                    ))
        return docs

    def fetch(self, queries: List[str], recency_days: int) -> List[SignalDoc]:
        timeframe = "today 1-m" if recency_days <= 30 else "today 3-m"

        cached = self._load_cache(timeframe)
        if cached is not None:
            return self._docs_from_cached(cached, timeframe)

        docs: List[SignalDoc] = []
        collected: Dict[str, Any] = {}

        safe_queries = queries[:40]
        batch_size = 1

        for i in range(0, len(safe_queries), batch_size):
            batch = safe_queries[i:i + batch_size]

            max_retry = 5
            for attempt in range(max_retry):
                try:
                    self.pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo="KR", gprop="")
                    related = self.pytrends.related_queries()

                    for q in batch:
                        pack = related.get(q, {})
                        out = {"top": [], "rising": []}
                        for kind in ("top", "rising"):
                            df = pack.get(kind)
                            if df is None or df.empty:
                                continue
                            for _, row in df.head(10).iterrows():
                                kw = str(row.get("query", "")).strip()
                                val = row.get("value", None)
                                if kw:
                                    out[kind].append({"query": kw, "value": val})
                        collected[q] = out

                        for kind in ("top", "rising"):
                            for item in out[kind]:
                                docs.append(SignalDoc(
                                    source=self.name,
                                    title=f"[{q}] related_{kind}: {item['query']}",
                                    text=item["query"],
                                    url="",
                                    published_at=None,
                                    meta={"seed": q, "kind": kind, "value": item.get("value"), "timeframe": timeframe}
                                ))

                    break

                except pytrends_ex.TooManyRequestsError:
                    sleep_s = (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(sleep_s)
                    if attempt == max_retry - 1:
                        return []
                except Exception:
                    return []

            time.sleep(random.uniform(1.0, 2.0))

        self._save_cache(timeframe, collected)
        return docs
