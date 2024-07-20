#!/usr/bin/env python
# coding: utf-8

import dataclasses
import datetime
import pathlib
import pprint
import re

import feedparser

from common import BaseUtilities  # ここ、何とかしたいんだけどどうすりゃいいんだ、実行場所によってエラーが出たりでなかったりする


@dataclasses.dataclass
class RSSData():
    url: str
    title: str
    author: str
    created_at: str


class RSSPerse():
    def __init__(self) -> None:
        com = BaseUtilities()

        data_path = pathlib.Path(__file__).parent
        data_path /= '../data'
        data_path = data_path.resolve()
        RSS_list_path = data_path
        RSS_list_path /= './NewThreads.json'

        if not RSS_list_path.exists():
            raise FileNotFoundError
        else:
            self.RSS_dict = com.load_json(RSS_list_path)

    def ReturnRSSList(self):
        return self.RSS_dict

    def return_data_strip(self, data) -> dict:  # ここを修正
        strip_data = {}
        strip_data['title'] = data['title']
        strip_data['url'] = data['threadid']

        strip_data['created_at'] = self.utc_to_jst(data['postdate'])
        strip_data['author'] = data['author']

        return strip_data

    def utc_to_jst(self, timestamp_utc):
        # datetime_jst = timestamp_utc + datetime.timedelta(hours=+9)
        timestamp_jst = datetime.datetime.strftime(
            timestamp_utc, "%d %b %Y %H:%M")

        return timestamp_jst

    def getnewpostspercategory(self, url, categoryid):
        try:
            result = []
            feed = feedparser.parse(
                f"http://{url}/feed/forum/ct-{categoryid}.xml")
            threads = feed.entries
            for thread in threads:
                try:
                    guid = thread.guid
                    threadid = guid.replace(f"http://{url}/forum/t-", "")
                    title = thread.title
                    try:
                        author = thread.wikidot_authorname
                        # unix化
                        author = author.lower()
                        author = re.sub("[_ ]", "-", author)
                    except Exception:
                        author = "unknown"
                    postdate = datetime.datetime.strptime(
                        thread.published, "%a, %d %b %Y %H:%M:%S %z")
                    postdate = postdate.astimezone().strftime('%Y-%m-%d %H:%M:%S')
                    result.append(RSSData(
                        url=threadid,
                        title=title,
                        author=author,
                        created_at=postdate
                    ))
                except Exception as e:
                    print(e)
                    raise
            return result
        except Exception as e:
            print(e)
            raise


if __name__ == "__main__":
    rss = RSSPerse()
    rss.ReturnRSSList()
    url = 'scp-jp.wikidot.com/'
    categoryid = '790925'

    result = rss.getnewpostspercategory(url, categoryid)
    pprint.pprint(result)
