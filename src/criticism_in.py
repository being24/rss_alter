import os
import pathlib
from datetime import datetime

import wikidot
from age_flyer import AgeFlyer
from db import Article, engine
from dotenv import load_dotenv
from models import ArticleInfo, convert_datetime
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from webhook import Webhook
from wikidot.module.page import PageCollection


class CriticismIn:
    def __init__(self) -> None:
        self.session = sessionmaker(engine)
        self.webhook = Webhook()
        self.age_flyer = AgeFlyer()

        dotenv_path = pathlib.Path(__file__).parents[1] / ".env"

        load_dotenv(dotenv_path)

        self.webhook_url = os.getenv("CRITICISM_IN")
        assert self.webhook_url is not None

        self.age_webhook_url = os.getenv("AGE")
        assert self.age_webhook_url is not None

    def get_created_datetime(self) -> datetime:
        with self.session() as session:
            stmt = (
                select(Article)
                .where(Article.type == "criticism_in")
                .order_by(Article.created_at.desc())
                .limit(1)
            )
            criticism_in_created = session.execute(stmt).scalar_one_or_none()

        assert criticism_in_created is not None

        return criticism_in_created.created_at

    def is_exist(self, url: str) -> bool:
        with self.session() as session:
            stmt = (
                select(Article)
                .where(Article.type == "criticism_in")
                .where(Article.url == url)
            )
            result = session.execute(stmt).scalar_one_or_none()

        return result is not None

    def get_same_author(self, created_by: str) -> list[ArticleInfo]:
        with self.session() as session:
            stmt = (
                select(Article)
                .where(Article.type == "criticism_in")
                .where(Article.created_by == created_by)
            )
            same_author = session.execute(stmt).scalars().all()

            # 内包表記でArticleInfoに変換する
            same_author = [
                ArticleInfo(
                    url=article.url,
                    title=article.title,
                    tags=article.tags,
                    created_by=article.created_by,
                    created_at=article.created_at,
                    updated_at=article.updated_at,
                )
                for article in same_author
            ]

        return same_author

    def get_unpost(self) -> PageCollection:
        with wikidot.Client() as client:
            site = client.site.get("scp-jp-sandbox3")

            recently_created = site.pages.search(
                tags="_criticism-in",
                order="created_at desc",
                limit=100,
                updated_at="last 24 hours",
            )

            not_exist_pages = []

            for page in recently_created:
                page_url = page.get_url()

                if not self.is_exist(page_url):
                    not_exist_pages.append(page)

        return PageCollection(site, not_exist_pages)

    def send_webhook(self, pages: PageCollection):
        self.webhook.set_parameter(
            webhook_url=self.webhook_url,
        )
        for page in pages:
            self.webhook.rss_send(page)

    def insert2db(self, pages: PageCollection):
        with self.session() as session:
            for page in pages:
                tags = ",".join(page.tags)
                if page.title is None:
                    page.title = "No title"
                article = Article(
                    url=page.get_url(),
                    title=page.title,
                    tags=tags,
                    created_by=page.created_by.name,
                    created_at=page.created_at,
                    updated_at=page.updated_at,
                    type="criticism_in",
                )
                session.add(article)

            session.commit()

    def age(self, pages: PageCollection):
        self.webhook.set_parameter(
            webhook_url=self.age_webhook_url,
        )
        for page in pages:
            assert page.created_by.name is not None
            same_author = self.get_same_author(page.created_by.name)

            for article in same_author:
                if self.age_flyer.fry(page.title, article.title) > 0.5:
                    self.webhook.send_age(page, article)

    def main(self):
        unpost = self.get_unpost()
        self.send_webhook(unpost)
        self.age(unpost)
        self.insert2db(unpost)


if __name__ == "__main__":
    mrc = CriticismIn()
    mrc.main()
