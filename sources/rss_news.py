from datetime import datetime, timezone
from typing import List
import feedparser

from .base import SignalSource, SignalDoc

class RssNewsSource(SignalSource):
    name = "rss_news"

    def __init__(self, feeds: List[str]):
        self.feeds = feeds

    def fetch(self, queries: List[str], recency_days: int) -> List[SignalDoc]:
        docs: List[SignalDoc] = []
        for feed_url in self.feeds:
            d = feedparser.parse(feed_url)
            for e in d.entries[:300]:
                title = getattr(e, "title", "")
                link = getattr(e, "link", "")
                summary = getattr(e, "summary", "") or getattr(e, "description", "")
                published = None
                if getattr(e, "published_parsed", None):
                    published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc).astimezone()

                docs.append(SignalDoc(
                    source=self.name,
                    title=title,
                    text=f"{title}\n{summary}",
                    url=link,
                    published_at=published,
                    meta={"feed": feed_url}
                ))
        return docs
