#!/usr/bin/env python
# coding: utf-8


import json
import os
import pathlib
import pprint
import sys

from soupsieve import select


from src.common import BaseUtilities
from src.listpages import ListpagesUtil
from src.RSS_parse import RSSPerse
from src.webhook import Webhook


class NewPagesAndCriticismIn():
    def __init__(self) -> None:
        self.com = BaseUtilities()
        self.hook = Webhook()
        self.lu = ListpagesUtil()

        data_path = pathlib.Path(__file__)
        data_path /= '../data'
        data_path = data_path.resolve()
        self.config_path = data_path
        self.config_path /= './NewAndCriticism.json'

        if not self.config_path.exists():
            raise FileNotFoundError
        else:
            self.listpages_dict = self.com.load_json(self.config_path)

    def get_listpages_and_send_webhook(self):
        for vals in self.listpages_dict.values():
            url = vals["target_url"]
            username = vals["username"]
            avatar_url = vals["avatar_url"]
            webhook_url = vals["webhook_url"]
            root_url = vals["root_url"]
            last_url = vals["last_url"]
            param_dict = vals["params"]  # dict

            result = self.lu.LIST_PAGES(
                url=url, limit="50", param_dict=param_dict)

            url_list = [i['fullname'] for i in result]

            index = 100
            if last_url in url_list:
                index = url_list.index(last_url)
            result = result[:index]

            for i in reversed(result):
                send_dict = self.lu.return_data_strip(i)
                self.hook.set_parameter(
                    username=username,
                    avatar_url=avatar_url,
                    webhook_url=webhook_url,
                    root_url=root_url)

                last_url = send_dict['url']

                # hook.send_webhook_article(send_dict, 'article')

            vals['last_url'] = last_url
            self.com.dump_json(self.config_path, self.listpages_dict)


class NewThreads():
    def __init__(self) -> None:
        self.com = BaseUtilities()
        self.hook = Webhook()
        self.rss = RSSPerse()

        data_path = pathlib.Path(__file__)
        data_path /= '../data'
        data_path = data_path.resolve()
        self.config_path = data_path
        self.config_path /= './NewThreads.json'

        if not self.config_path.exists():
            raise FileNotFoundError
        else:
            self.RSS_dict = self.com.load_json(self.config_path)

    def get_rss_and_send_webhook(self) -> None:
        avatar_url = self.RSS_dict["setting"]["avatar_url"]
        webhook_url = self.RSS_dict["setting"]["webhook_url"]

        for key, vals in self.RSS_dict.items():
            if key == "setting":
                continue

            username = vals["username"]
            url = vals["url"]
            last_url = vals["last_url"]
            categoryid = vals["categoryid"]
            last_url = vals["last_url"]

            result = self.rss.getnewpostspercategory(
                url=url, categoryid=categoryid)

            url_list = [i['threadid'] for i in result]

            index = 100
            if last_url in url_list:
                index = url_list.index(last_url)
            result = result[:index]

            for i in reversed(result):
                send_dict = self.rss.return_data_strip(i)
                self.hook.set_parameter(
                    username=username,
                    avatar_url=avatar_url,
                    webhook_url=webhook_url,
                    root_url=url)

                last_url = send_dict['url']

                self.hook.send_webhook(send_dict, 'RSS')

            vals['last_url'] = last_url
            self.com.dump_json(self.config_path, self.RSS_dict)


def arc():
    rss_dict = rss.ReturnRSSList()

    for key, val in rss_dict.items():
        rss_data = rss.getnewpostspercategory(val['url'], val['categoryid'])

        last_url = val['last_url']

        url_list = [i['threadid'] for i in rss_data]

        index = 100
        if last_url in url_list:
            index = url_list.index(last_url)
        rss_data = rss_data[:index]

        # ここまでできた

        print(rss_data)

        hook.gen_webhook_msg_RSS(rss_data)


if __name__ == "__main__":
    # NewPagesAndCriticismIn().get_listpages_and_send_webhook()
    NewThreads().get_rss_and_send_webhook()
