import json
import os
import pathlib
from collections.abc import Callable
from datetime import datetime

import feedparser
from db import Thread, engine
from dotenv import load_dotenv
from models import Feed, ThreadsConfig
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from webhook import Webhook


class NewThreads:
    def __init__(self):
        root_path = pathlib.Path(__file__).parents[1]
        dotenv_path = root_path / ".env"
        load_dotenv(dotenv_path)

        self.session = sessionmaker(engine)

        self.webhook_url = os.getenv("NEW_THREAD")
        assert self.webhook_url is not None

        config_path = root_path / "data" / "NewThreads.json"

        self.configs: list[ThreadsConfig] = []

        self.webhook = Webhook()
        self.webhook.set_parameter(
            webhook_url=self.webhook_url,
        )

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for key, c in config.items():
            info = ThreadsConfig(
                display_name=c["display_name"],
                category_id=c["category_id"],
                type=key,
            )

            self.configs.append(info)

    def is_exist(self, url: str) -> bool:
        normalized_url = url.replace("https://", "http://", 1)

        with self.session() as session:
            stmt = select(Thread).where(
                func.replace(Thread.url, "https://", "http://") == normalized_url
            )
            result = session.execute(stmt).fetchall()

        if len(result) == 0:
            return False

        return True

    def get_feed(self, url: str) -> list[Feed]:
        feeds = feedparser.parse(url)

        parsed_feed = []

        for entry in feeds["entries"]:
            published = datetime.strptime(
                entry["published"], "%a, %d %b %Y %H:%M:%S %z"
            )
            link = entry["link"].split("/")
            link = f"http://scp-jp.wikidot.com/forum/{link[4]}"
            feed = Feed(
                link=link,
                published=published,
                summary=entry["summary"],
                title=entry["title"],
                wikidot_author_name=entry.get("wikidot_authorname") or "不明",
                wikidot_author_id=entry["wikidot_authoruserid"],
            )

            parsed_feed.append(feed)

        return parsed_feed

    @staticmethod
    def dedupe_new_feeds(
        configs_with_feeds: list[tuple[ThreadsConfig, list[Feed]]],
        is_exist: Callable[[str], bool],
    ) -> list[Feed]:
        """同一スレッドが複数カテゴリのフィードに掲載されている場合に備え、
        1回の実行内で既に採用したURLを追跡して二重登録を防ぐ。

        is_exist(DB問い合わせ)だけでは、insert2dbが全config処理後に
        まとめて実行されるため実行内の重複を検出できない
        """
        not_exist_feeds = []
        seen_urls: set[str] = set()

        for config, feeds in configs_with_feeds:
            for feed in feeds:
                normalized_link = feed.link.replace("https://", "http://", 1)
                if normalized_link in seen_urls:
                    continue
                if not is_exist(feed.link):
                    feed.type = config.type
                    not_exist_feeds.append(feed)
                    seen_urls.add(normalized_link)

        return not_exist_feeds

    def get_new_threads(self) -> list[Feed]:
        configs_with_feeds = []

        for config in self.configs:
            url = f"http://scp-jp.wikidot.com/feed/forum/ct-{config.category_id}.xml"

            feeds = self.get_feed(url)
            feeds = sorted(feeds, key=lambda x: x.published)

            # feedsのdisplay_nameを設定
            for feed in feeds:
                feed.display_name = config.display_name

            configs_with_feeds.append((config, feeds))

        return self.dedupe_new_feeds(configs_with_feeds, self.is_exist)

    def send_webhook(self, feeds: list[Feed]):
        for feed in feeds:
            self.webhook.feeds_send(feed)

    def insert2db(self, feeds: list[Feed]):
        with self.session() as session:
            for feed in feeds:
                thread = Thread(
                    url=feed.link,
                    title=feed.title,
                    author=feed.wikidot_author_name,
                    datetime=feed.published,
                    type=feed.type,
                )
                session.add(thread)

            session.commit()

    def main(self):
        feeds = self.get_new_threads()
        self.send_webhook(feeds)
        self.insert2db(feeds)


if __name__ == "__main__":
    nt = NewThreads()
    nt.main()
