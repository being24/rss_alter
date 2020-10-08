#!/usr/bin/env python
# coding: utf-8

import json
import os
import pathlib

from utils.listpages import ListpagesUtil
from utils.webhook import Webhook
from utils.RSS_parse import RSSPerse


def load_json(json_path) -> dict:
    if not os.path.isfile(json_path):
        raise FileNotFoundError

    with open(json_path, encoding='utf-8') as f:
        json_dict = json.load(f)
    return json_dict


def dump_json(json_path, data) -> None:
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False)


if __name__ == "__main__":

    data_path = pathlib.Path(__file__).parent
    data_path /= '../data'
    data_path = data_path.resolve()
    config_path = data_path
    config_path /= './config.json'

    lu = ListpagesUtil()
    hook = Webhook()

    rss = RSSPerse()

    setting_dict = load_json(config_path)

    '''
    url = setting_dict["criticism-in"]["target_url"]
    username = setting_dict["criticism-in"]["username"]
    avatar_url = setting_dict["criticism-in"]["avatar_url"]
    webhook_url = setting_dict["criticism-in"]["webhook_url"]
    root_url = setting_dict["criticism-in"]["root_url"]
    last_url = setting_dict["criticism-in"]["last_url"]

    criticism_in_pages = lu.LIST_PAGES(
        url=url,
        limit='50',
        tags='_criticism-in',
        category='draft',
    )

    url_list = [i['fullname'] for i in criticism_in_pages]

    index = 100
    if last_url in url_list:
        index = url_list.index(last_url)
    criticism_in_pages = criticism_in_pages[:index]

    for i in reversed(criticism_in_pages):
        send_dict = lu.return_data_strip(i)
        hook.set_parameter(
            username=username,
            avatar_url=avatar_url,
            webhook_url=webhook_url,
            root_url=root_url)

        last_url = send_dict['url']

        hook.send_webhook_article(send_dict, 'article')

    setting_dict["criticism-in"]['last_url'] = last_url
    dump_json(config_path, setting_dict)

    url = setting_dict["most-recently-created"]["target_url"]
    username = setting_dict["most-recently-created"]["username"]
    avatar_url = setting_dict["most-recently-created"]["avatar_url"]
    webhook_url = setting_dict["most-recently-created"]["webhook_url"]
    root_url = setting_dict["most-recently-created"]["root_url"]
    last_url = setting_dict["most-recently-created"]["last_url"]

    most_recentry_created_pages = lu.LIST_PAGES(
        url=url,
        limit='50',
        order='created_at desc')

    url_list = [i['fullname'] for i in most_recentry_created_pages]

    index = 100
    if last_url in url_list:
        index = url_list.index(last_url)
    most_recentry_created_pages = most_recentry_created_pages[:index]

    for i in reversed(most_recentry_created_pages):
        send_dict = lu.return_data_strip(i)
        hook.set_parameter(
            username=username,
            avatar_url=avatar_url,
            webhook_url=webhook_url,
            root_url=root_url)

        hook.send_webhook_article(send_dict, 'article')

        last_url = send_dict['url']

    setting_dict["most-recently-created"]['last_url'] = last_url
    dump_json(config_path, setting_dict)
    '''

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
