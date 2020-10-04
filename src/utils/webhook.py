#!/usr/bin/env python
# coding: utf-8

import json
import logging
import time

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

    def set_parameter(self, username, avatar_url, webhook_url, root_url):
        self.USERNAME = username
        self.AVATOR_URL = avatar_url
        self.WEBHOOK_URL = webhook_url
        self.ROOT_URL = root_url

    def gen_webhook_msg(self, content):
        title = content['title']
        url = f"{content['url']}"
        created_by = content['created_by']
        created_at = content['created_at']
        updated_at = content['updated_at']

        msg_ = {"username": self.USERNAME,
                "avatar_url": self.AVATOR_URL,
                "embeds": [{"title": f"{title}",
                            "url": f"{self.ROOT_URL}{url}",
                            "fields": [{"name": "作成者",
                                        "value": f"{created_by}",
                                        "inline": True},
                                       {"name": "作成日時",
                                        "value": f"{created_at}",
                                        "inline": True},
                                       {"name": "更新日時",
                                        "value": f"{updated_at}"},
                                       ],
                            }]}
        return msg_

    def send_webhook(self, msg):
        msg = msg or None

        if msg is None or "":
            logging.error("can't send blank msg")
            return -1

        main_content = self.gen_webhook_msg(msg)

        while True:
            response = requests.post(
                self.WEBHOOK_URL, json.dumps(main_content), headers={
                    'Content-Type': 'application/json'})

            if response.status_code == 204:
                break
            else:
                err_data = response.json()
                retry_after = int(err_data["retry_after"]) / 1000 + 0.1
                logging.error(response.text)
                logging.error(main_content)
                time.sleep(retry_after)

        time.sleep(0.5)


if __name__ == "__main__":
    Webhook().send_webhook('test')
