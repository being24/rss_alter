#!/usr/bin/env python
# coding: utf-8

import json
import logging
import time
from typing import NamedTuple

import requests


class Webhook():
    """
    Webhookを扱うclass
    """

    def __init__(self):
        self.USERNAME = 'hoge'
        self.AVATOR_URL = "fuga"
        self.WEBHOOK_URL = 'hoo'
        self.ROOT_URL = 'bar'

    def set_parameter(self, webhook_url, root_url):
        self.WEBHOOK_URL = webhook_url
        self.ROOT_URL = root_url

    def gen_msg_listpages(self, content):
        title = content.title
        url = content.url
        created_by = content.created_by
        created_at = content.created_at
        updated_at = content.updated_at
        tags = content.tags

        tags = tags or None
        updated_at = updated_at or None

        if tags is None or "":
            tags = "None"

        if updated_at is None or "":
            updated_at = "None"

        msg_ = {"embeds": [{"title": f"{title}",
                            "url": f"{self.ROOT_URL}{url}",
                            "fields": [{"name": "作成者",
                                        "value": f"{created_by}",
                                        "inline": True},
                                       {"name": "作成日時",
                                        "value": f"{created_at}",
                                        "inline": True},
                                       {"name": "更新日時",
                                        "value": f"{updated_at}"},
                                       {"name": "タグ",
                                        "value": f"{tags}"},
                                       ],
                            }]}
        return msg_

    def gen_msg_age(self, notnotified, databased):
        notified_title = notnotified.title
        notified_url = notnotified.url
        notified_created_by = notnotified.created_by

        databased_title = databased.title
        databased_url = databased.url

        msg_ = {"embeds": [{"title": "タイトルの類似度が高い下書きを検出しました",
                            "color": 16711680,
                            "fields": [{"name": "作成者",
                                        "value": f"{notified_created_by}",
                                        "inline": False},
                                       {"name": "新規ページタイトル",
                                        "value": f"[{notified_title}]({self.ROOT_URL}{notified_url})",
                                        "inline": False},
                                       {"name": "元ページタイトル",
                                        "value": f"[{databased_title}]({self.ROOT_URL}{databased_url})",
                                        "inline": False},
                                       ],
                            }]}
        return msg_

    def gen_msg_RSS(self, content):
        title = content['title']
        url = f"{content['url']}"
        created_by = content['author']
        created_at = content['created_at']

        msg_ = {"embeds": [{"title": f"{title}",
                            "url": f"{url}",
                            "fields": [{"name": "作成者",
                                        "value": f"{created_by}",
                                        "inline": True},
                                       {"name": "作成日時",
                                        "value": f"{created_at}",
                                        "inline": True},
                                       ],
                            }]}
        return msg_

    def gen_msg(self, content):
        msg = {"content": content}
        return msg

    def return_msg(self, msg, msg_type):
        if msg_type == 'RSS':
            return self.gen_msg_RSS(msg)
        elif msg_type == 'LISTPAGES':
            return self.gen_msg_listpages(msg)
        else:
            return self.gen_msg(msg)

    def send(self, content):
        while True:
            response = requests.post(
                self.WEBHOOK_URL, json.dumps(content), headers={
                    'Content-Type': 'application/json'})

            if response.status_code == 204:
                break
            else:
                err_data = response.json()
                logging.error(response.text)
                logging.error(content)
                if 'embeds' in err_data:
                    break
                elif 'retry_after' in err_data:
                    retry_after = int(err_data["retry_after"]) / 1000 + 0.1
                    time.sleep(retry_after)

        time.sleep(0.5)

    def send_webhook(self, msg, msg_type):
        msg = msg or None

        if msg is None or "":
            logging.error("can't send blank msg")
            return -1

        main_content = self.return_msg(msg, msg_type)
        self.send(main_content)

        # loggingをもうちょっと拡充させる

    def send_age(self, notnotified, databased):
        main_content = self.gen_msg_age(notnotified, databased)
        self.send(main_content)


if __name__ == "__main__":
    Webhook().send_webhook('test', 'def')
