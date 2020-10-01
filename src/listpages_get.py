#!/usr/bin/env python
# coding: utf-8

import asyncio
import datetime
import json
import logging
import os
import pathlib
import time

import bs4
import requests


class ListpagesUtil(object):
    """
    listpagemoduleを扱うclass
    """

    def __init__(self) -> None:
        data_path = pathlib.Path(__file__).parent
        data_path /= '../data'
        data_path = data_path.resolve()
        self.json_path = data_path
        self.json_path /= './data_test.json'

    def dump_json(self, data) -> None:
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False)

    def LIST_PAGES(self, url, **kwargs):
        kwargs['module_body'] = '\n'.join(
            map('|| {0} || %%{0}%% ||'.format, [
                'fullname',
                'title',
                'created_at',
                'created_by_unix',
                'created_by_id',
                'created_by',
                'updated_at',
                'updated_by',
                'updated_by_unix',
                'updated_by_id',
                'commented_at',
                'commented_by',
                'commented_by_unix',
                'commented_by_id',
                'parent_fullname',
                'comments',
                'size',
                'rating',
                'rating_votes',
                'revisions',
                'tags',
            ]))

        obj = {
            'perPage': '250',
            'moduleName': 'list/ListPagesModule'
        }
        obj.update(kwargs)

        listpages = []
        results = []

        sem = asyncio.Semaphore(10)

        def perPage(p=1, mode="oj"):
            print(f'requesting Page {p}')

            obj.update({'p': p})
            param = [k + '=' + str(obj[k]) for k in obj]
            param.append('wikidot_token7=123456')
            while True:
                res = requests.post(
                    url,
                    data="&".join(param).encode('utf-8'),
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                    cookies={
                        'wikidot_token7': '123456'})
                if res.status_code is requests.codes.ok:
                    break

            print(f'Page {p} Done')

            if mode == "html":
                return bs4.BeautifulSoup(res.json()['body'], 'html.parser')
            elif mode == "oj":
                body_html = bs4.BeautifulSoup(
                    res.json()['body'], 'html.parser')
                body_html_select = body_html.select('.list-pages-item')
                items = [i for i in body_html_select]
                _listpages = []
                for i in items:
                    oj = {}
                    tr = i.select('tr')
                    for t in tr:
                        x = t.select('td')
                        oj[x[0].text] = x[1].text
                    _listpages.append(oj)
                return _listpages

        async def get_async(p):
            async with sem:
                loop = asyncio.get_event_loop()
                soup = await loop.run_in_executor(None, perPage, p)
                return soup

        first_page = perPage(1, mode="html")

        pager = first_page.select('.pager')
        if len(pager):
            n = pager[0].select('.target')
            n = int(n[len(n) - 2].text.strip())
        else:
            n = 1

        loop = asyncio.get_event_loop()

        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*[get_async(i) for i in range(1, n + 1)])
        results = loop.run_until_complete(tasks)

        for i in results:
            listpages += i
        return listpages

    def return_data_strip(self, data) -> dict:
        strip_data = {}
        print(data)
        strip_data['title'] = data['title']
        strip_data['url'] = data['fullname']

        strip_data['created_by'] = data['created_by']
        strip_data['created_at'] = self.utc_to_jst(data['created_at'])
        strip_data['updated_at'] = self.utc_to_jst(data['updated_at'])

        return strip_data

    def utc_to_jst(self, timestamp_utc):
        datetime_utc = datetime.datetime.strptime(
            timestamp_utc + "+0000", "%d %m %Y %H:%M.%f%z")
        datetime_jst = datetime_utc.astimezone(
            datetime.timezone(datetime.timedelta(hours=+9)))
        timestamp_jst = datetime.datetime.strftime(
            datetime_jst, '%Y-%m-%d %H:%M:%S.%f')
        return timestamp_jst


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


if __name__ == "__main__":

    data_path = pathlib.Path(__file__).parent
    data_path /= '../data'
    data_path = data_path.resolve()
    json_path = data_path
    json_path /= './config.json'

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

    lu = ListpagesUtil()
    hook = Webhook()

    setting_dict = load_json(json_path)

    temp_dict = setting_dict["criticism-in"]
    url = temp_dict["target_url"]
    username = temp_dict["username"]
    avatar_url = temp_dict["avatar_url"]
    webhook_url = temp_dict["webhook_url"]
    root_url = temp_dict["root_url"]

    criticism_in_pages = lu.LIST_PAGES(
        url=url,
        limit='1',
        tags='_criticism-in',
        category='draft')

    for i in criticism_in_pages:  # レートリミット回避目的で順番に処理する
        # webhookを投げる処理を書く(名前とURLは引数にする)しwebhookはもっとリッチにする
        send_dict = lu.return_data_strip(i)
        hook.set_parameter(
            username=username,
            avatar_url=avatar_url,
            webhook_url=webhook_url,
            root_url=root_url)

        hook.send_webhook(send_dict)

    temp_dict = setting_dict["most-recently-created"]
    url = temp_dict["target_url"]
    username = temp_dict["username"]
    avatar_url = temp_dict["avatar_url"]
    webhook_url = temp_dict["webhook_url"]
    root_url = temp_dict["root_url"]

    most_recentry_created_pages = lu.LIST_PAGES(
        url=url,
        limit='3',)

    for i in most_recentry_created_pages:
        send_dict = lu.return_data_strip(i)
        hook.set_parameter(
            username=username,
            avatar_url=avatar_url,
            webhook_url=webhook_url,
            root_url=root_url)

        hook.send_webhook(send_dict)
