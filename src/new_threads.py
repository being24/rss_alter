import json
import os
import pathlib
from datetime import datetime

import feedparser
from db import Thread, engine
from dotenv import load_dotenv
from models import Feed, ThreadsConfig
from sqlalchemy import select
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
        with self.session() as session:
            stmt = select(Thread).where(Thread.url == url)
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
                wikidot_author_name=entry["wikidot_authorname"],
                wikidot_author_id=entry["wikidot_authoruserid"],
            )

            parsed_feed.append(feed)

        return parsed_feed

    def get_new_threads(self) -> list[Feed]:
        not_exist_feeds = []

        for config in self.configs:
            url = f"http://scp-jp.wikidot.com/feed/forum/ct-{config.category_id}.xml"

            feeds = self.get_feed(url)
            feeds = sorted(feeds, key=lambda x: x.published)

            # feedsのdisplay_nameを設定
            for feed in feeds:
                feed.display_name = config.display_name

            for feed in feeds:
                if not self.is_exist(feed.link):
                    feed.type = config.type
                    not_exist_feeds.append(feed)

        return not_exist_feeds

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
