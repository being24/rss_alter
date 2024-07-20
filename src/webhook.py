import json
import time

import requests
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
        self.user_name = username
        self.avatar_url = avatar_url
        self.webhook_url = webhook_url

    def generate_embed(self, page: Page) -> dict:
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

    def send(self, page: Page):
        content = self.generate_embed(page)
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
