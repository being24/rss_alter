import html
import json
import pathlib
import pprint
import re
from datetime import datetime

import feedparser

from webhook import webhook

data_path = pathlib.Path(__file__).parent
data_path /= '../data'
data_path = str(data_path.resolve())


def dump_json(json_data):
    with open(data_path + '/config.json', "w") as f:
        json.dump(
            json_data,
            f,
            ensure_ascii=False,
            indent=4,
            separators=(
                ',',
                ': '))


notified_dict = {}
RSS_key = 'most-recently-created'


tg_url = 'http://scp-jp.wikidot.com/feed/pages/pagename/most-recently-created/category/_default%2Cauthor%2Cprotected%2Cwanderers%2Ctheme/order/created_at+desc/limit/30/t/%E6%9C%80%E8%BF%91%E4%BD%9C%E6%88%90%E3%81%95%E3%82%8C%E3%81%9F%E8%A8%98%E4%BA%8B'
html_tag_replace = re.compile(r"<.*?>")


rss_row = feedparser.parse(tg_url)
entries = rss_row.entries


for entry in reversed(entries):
    # 解析
    link = entry.link
    pubdate = datetime.strptime(
        entry.published, "%a, %d %b %Y %H:%M:%S %z")
    pubdate = pubdate.astimezone().strftime("%Y/%m/%d %H:%M:%S %Z")

    summary = html_tag_replace.sub("", entry.content[0].value)
    summary = html.unescape(summary).strip()
    if len(summary) > 100:
        summary = summary[:100] + "...."
    # print(summary)
    # サマリーが50文字超えたら略記

notified_dict[RSS_key] = {'url': link, 'webhook_url': 'hoge'}
print(link)
dump_json(notified_dict)