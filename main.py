#!/usr/bin/env python
# coding: utf-8


import pathlib

from src.age_flyer import AgeFlyer
from src.common import BaseUtilities
from src.listpages import ListpagesUtil
from src.RSS_parse import RSSPerse
from src.sqlite_util import SQlite
from src.webhook import Webhook


class NewPagesAndCriticismIn():
    def __init__(self) -> None:
        self.com = BaseUtilities()
        self.hook = Webhook()
        self.lu = ListpagesUtil()
        self.db = SQlite()
        self.age = AgeFlyer()

        data_path = pathlib.Path(__file__)
        data_path /= '../data'
        data_path = data_path.resolve()
        self.config_path = data_path
        self.config_path /= './NewAndCriticism.json'

        if not self.config_path.exists():
            raise FileNotFoundError
        else:
            self.listpages_dict = self.com.load_json(self.config_path)

    def merge_sql(self, table_name) -> str:
        sql_statement = f'INSERT INTO {table_name}( url, title, tags, created_by, created_at, updated_at ) VALUES( ?, ?, ?, ?, ?, ? ) ON  conflict( url ) DO UPDATE SET tags = excluded.tags, updated_at = excluded.updated_at'
        return sql_statement

    def get_listpages_and_send_webhook(self):
        for key, vals in self.listpages_dict.items():

            target_url = vals["target_url"]
            webhook_url = vals["webhook_url"]
            param_dict = vals["params"]
            root_url = vals["root_url"]

            merge_sql = self.merge_sql(key)

            result = self.lu.LIST_PAGES(
                url=target_url, limit="250", param_dict=param_dict)

            result = [self.lu.return_data_strip(i) for i in result]

            self.db.create_db(key)

            not_notified_list = []
            for page in result:
                exists_sql = f'SELECT COUNT(*) FROM "{key}" WHERE url="{page.url}" AND created_at="{page.created_at}"'
                if not self.db.is_exist(exists_sql):
                    not_notified_list.append(page)

            if key == 'criticism_in':
                webhook_url = vals["age_url"]
                self.hook.set_parameter(
                    webhook_url=webhook_url,
                    root_url=root_url)
                for not_notified in not_notified_list:
                    same_author_sql = f'SELECT * FROM "{key}" WHERE created_by="{not_notified.created_by}"'
                    selected_data = self.db.get(same_author_sql)
                    for i in selected_data:
                        match_ratio = self.age.fly(i.title, not_notified.title)
                        if match_ratio > 0.4:
                            self.hook.send_age(i, not_notified)

                    self.db.execute(merge_sql, not_notified)

            self.hook.set_parameter(
                webhook_url=webhook_url,
                root_url=root_url)

            for i in reversed(not_notified_list):
                self.hook.send_webhook(i, 'LISTPAGES')
                pass

            data = [list(i) for i in result]
            self.db.executemany(merge_sql, data)


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
        webhook_url = self.RSS_dict["setting"]["webhook_url"]

        for key, vals in self.RSS_dict.items():
            if key == "setting":
                continue

            url = vals["url"]
            last_url = vals["last_url"]
            categoryid = vals["categoryid"]

            self.hook.set_parameter(
                webhook_url=webhook_url,
                root_url=url)

            result = self.rss.getnewpostspercategory(
                url=url, categoryid=categoryid)

            url_list = [i['threadid'] for i in result]

            index = 100
            if last_url in url_list:
                index = url_list.index(last_url)
            result = result[:index]

            for i in reversed(result):
                send_dict = self.rss.return_data_strip(i)

                last_url = send_dict['url']

                self.hook.send_webhook(send_dict, 'RSS')

            self.com.dump_json(self.config_path, self.RSS_dict)


if __name__ == "__main__":
    NewPagesAndCriticismIn().get_listpages_and_send_webhook()
    NewThreads().get_rss_and_send_webhook()
    # メモ jsonの整理（last_urlはいらない、webhookurlを合わせる、avatorurlを分ける）、DBは今日に分を送り込む
