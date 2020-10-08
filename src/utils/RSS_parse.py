#!/usr/bin/env python
# coding: utf-8

import json
from json import load
import pathlib
import pprint
import re
from datetime import datetime

import feedparser


def load_json(json_path: pathlib.Path) -> dict:
    if not json_path.exists():
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


class RSSPerse():
    def __init__(self) -> None:
        data_path = pathlib.Path(__file__).parents[1]
        data_path /= '../data'
        data_path = data_path.resolve()
        RSS_list_path = data_path
        RSS_list_path /= './RSS_list.json'

        if not RSS_list_path.exists():
            raise FileNotFoundError
        else:
            self.RSS_dict = load_json(RSS_list_path)

    def ReturnRSSList(self):
        return self.RSS_dict

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
                    postdate = datetime.strptime(
                        thread.published, "%a, %d %b %Y %H:%M:%S %z")
                    postdate = postdate.astimezone()
                    result.append({
                        "threadid": threadid,
                        "title": title,
                        "author": author,
                        "postdate": postdate
                    })
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

    # result = rss.getnewpostspercategory(url, categoryid)
    # pprint.pprint(result)
