#!/usr/bin/env python
# coding: utf-8


import dataclasses
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
        sql_statement = f"""INSERT INTO {table_name}( url, title, tags, created_by, created_at, updated_at ) VALUES( ?, ?, ?, ?, ?, ? )
                            ON  conflict( url ) DO UPDATE SET title = excluded.title, tags = excluded.tags, created_by = excluded.created_by, created_at = excluded.created_at, updated_at = excluded.updated_at"""
        return sql_statement

    def get_listpages_and_send_webhook(self):
        for key, val in self.listpages_dict.items():

            target_url = val["target_url"]
            webhook_url = val["webhook_url"]
            param_dict = val["params"]
            root_url = val["root_url"]

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
                webhook_url = val["age_url"]
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
                            pass

                    self.db.execute(merge_sql, not_notified)

            webhook_url = val["webhook_url"]

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
        self.db = SQlite()

        data_path = pathlib.Path(__file__)
        data_path /= '../data'
        data_path = data_path.resolve()
        self.config_path = data_path
        self.config_path /= './NewThreads.json'

        if not self.config_path.exists():
            raise FileNotFoundError
        else:
            self.RSS_dict = self.com.load_json(self.config_path)

        for key in self.RSS_dict.keys():
            sql = f"""
                    create table if not exists "{key}"
                    (url TEXT PRIMARY KEY, title TEXT, author TEXT, datetime TEXT)
                """

            self.db.create_table(sql)

    def merge_sql(self, table_name) -> str:
        sql_statement = f"""INSERT INTO {table_name}(url , title , author , datetime ) VALUES( ?, ?, ?, ?)
                            ON  conflict( url ) DO NOTHING"""
        return sql_statement

    def get_rss_and_send_webhook(self) -> None:
        webhook_url = self.RSS_dict["setting"]["webhook_url"]

        for key, vals in self.RSS_dict.items():
            if key == "setting":
                continue

            url = vals["url"]
            categoryid = vals["categoryid"]
            username = vals["username"]

            self.hook.set_parameter(
                webhook_url=webhook_url,
                root_url=url,
                username=username)

            result = self.rss.getnewpostspercategory(
                url=url, categoryid=categoryid)

            for page in reversed(result):
                exists_sql = f'SELECT COUNT(*) FROM "{key}" WHERE url="{page.url}" AND datetime="{page.created_at}"'

                if not self.db.is_exist(exists_sql):
                    send_dict = dataclasses.asdict(page)
                    self.hook.send_webhook(send_dict, 'RSS')
                    merge_sql = self.merge_sql(key)
                    data = dataclasses.astuple(page)
                    self.db.execute(merge_sql, data)


if __name__ == "__main__":
    NewPagesAndCriticismIn().get_listpages_and_send_webhook()
    NewThreads().get_rss_and_send_webhook()