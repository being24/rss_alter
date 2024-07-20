import json
import time

import requests
from models import ArticleInfo, Feed
from wikidot.module.page import Page


class Webhook:
    """
    Webhookを扱うclass
    """

    def __init__(self):
        self.user_name = None
        self.avatar_url = None
        self.webhook_url = ""

    def set_parameter(
        self,
        webhook_url: str,
        avatar_url: str | None = None,
        username: str | None = None,
    ):
        """webhookのパラメータを設定する

        Args:
            webhook_url (str): webhookのURL
            avatar_url (str | None, optional): avatarのurl. Defaults to None.
            username (str | None, optional): username. Defaults to None.
        """
        self.user_name = username
        self.avatar_url = avatar_url
        self.webhook_url = webhook_url

    def generate_article_embed(self, page: Page) -> dict:
        """embedを生成する

        Args:
            page (Page): page object

        Returns:
            dict: embedの情報
        """
        title = page.title
        url = page.get_url()
        created_at = f"<t:{int(page.created_at.timestamp())}:f>"
        updated_at = f"<t:{int(page.updated_at.timestamp())}:f>"
        tags = ",".join(page.tags)

        msg = {
            "embeds": [
                {
                    "title": title,
                    "url": url,
                    "author": {
                        "name": f"{page.created_by.name}",
                        "url": f"https://www.wikidot.com/user:info/{page.created_by.unix_name}",
                        "icon_url": f"{page.created_by.avatar_url}",
                    },
                    "fields": [
                        {"name": "作成日時", "value": created_at, "inline": True},
                        {"name": "更新日時", "value": updated_at, "inline": True},
                        {"name": "タグ", "value": tags[:1024]},
                    ],
                }
            ]
        }

        return msg

    def send(self, content):
        while True:
            response = requests.post(
                self.webhook_url,
                json.dumps(content),
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 204:
                break
            else:
                print(response.text)
                err_data = response.json()
                if "embeds" in err_data:
                    break
                elif "retry_after" in err_data:
                    retry_after = int(err_data["retry_after"]) / 1000 + 0.1
                    time.sleep(retry_after)

        time.sleep(0.5)

    def rss_send(self, page: Page) -> None:
        content = self.generate_article_embed(page)
        self.send(content)

    def generate_feed_embed(self, feed: Feed) -> dict:
        """embedを生成する

        Args:
            feed (Feed): feed object

        Returns:
            dict: embedの情報
        """
        title = feed.title
        url = feed.link
        published = f"<t:{int(feed.published.timestamp())}:f>"
        author = feed.wikidot_author_name

        msg = {
            "embeds": [
                {
                    "title": title,
                    "url": url,
                    "fields": [
                        {"name": "投稿者", "value": author, "inline": True},
                        {"name": "公開日時", "value": published, "inline": True},
                    ],
                }
            ]
        }

        return msg

    def feeds_send(self, feed: Feed):
        content = self.generate_feed_embed(feed)
        self.send(content)

    def gen_msg_age(self, new: Page, database: ArticleInfo) -> dict:
        msg = {
            "embeds": [
                {
                    "title": "タイトルの類似度が高い下書きを検出しました",
                    "color": 16711680,
                    "author": {
                        "name": f"{new.created_by.name}",
                        "url": f"https://www.wikidot.com/user:info/{new.created_by.unix_name}",
                        "icon_url": f"{new.created_by.avatar_url}",
                    },
                    "fields": [
                        {
                            "name": "新規ページタイトル",
                            "value": f"[{new.title}]({new.get_url()})",
                            "inline": False,
                        },
                        {
                            "name": "元ページタイトル",
                            "value": f"[{database.title}]({database.url})",
                            "inline": False,
                        },
                    ],
                }
            ]
        }
        return msg

    def send_age(self, new: Page, database: ArticleInfo) -> None:
        content = self.gen_msg_age(new, database)
        self.send(content)
