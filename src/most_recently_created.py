import os
import pathlib
from datetime import datetime

import wikidot
from db import Article, engine
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from webhook import Webhook
from wikidot.module.page import PageCollection


class MostRecentlyCreated:
    def __init__(self) -> None:
        self.session = sessionmaker(engine)
        self.webhook = Webhook()

        dotenv_path = pathlib.Path(__file__).parents[1] / ".env"

        load_dotenv(dotenv_path)

        webhook_url = os.getenv("NEW_PAGE")
        assert webhook_url is not None

        self.webhook.set_parameter(
            webhook_url=webhook_url,
        )

    def get_created_datetime(self) -> datetime:
        with self.session() as session:
            stmt = (
                select(Article)
                .where(Article.type == "recently_created")
                .order_by(Article.created_at.desc())
                .limit(1)
            )
            most_recently_created = session.execute(stmt).scalar_one_or_none()

        assert most_recently_created is not None

        return most_recently_created.created_at

    def is_exist(self, url: str) -> bool:
        with self.session() as session:
            stmt = (
                select(Article)
                .where(Article.type == "recently_created")
                .where(Article.url == url)
            )
            result = session.execute(stmt).scalar_one_or_none()

        return result is not None

    def get_unpost(self) -> PageCollection:
        with wikidot.Client() as client:
            site = client.site.get("scp-jp")

            recently_created = site.pages.search(
                category="_default",
                order="created_at desc",
                limit=100,
                created_at="last 1 hours",
            )

            not_exist_pages = []

            for page in recently_created:
                page_url = page.get_url()

                if not self.is_exist(page_url):
                    not_exist_pages.append(page)

        return PageCollection(site, not_exist_pages)

    def send_webhook(self, pages: PageCollection):
        for page in pages:
            self.webhook.rss_send(page)

    def insert2db(self, pages: PageCollection):
        with self.session() as session:
            for page in pages:
                tags = ",".join(page.tags)
                article = Article(
                    url=page.get_url(),
                    title=page.title,
                    tags=tags,
                    created_by=page.created_by.name,
                    created_at=page.created_at,
                    updated_at=page.updated_at,
                    type="recently_created",
                )
                session.add(article)

            session.commit()

    def main(self):
        unpost = self.get_unpost()
        self.send_webhook(unpost)
        self.insert2db(unpost)


if __name__ == "__main__":
    mrc = MostRecentlyCreated()
    mrc.main()
