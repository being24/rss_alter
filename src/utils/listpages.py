import asyncio
import datetime
import json
import pathlib

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
            # print(f'requesting Page {p}')

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

            # print(f'Page {p} Done')

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
        strip_data['title'] = data['title']
        strip_data['url'] = data['fullname']

        strip_data['created_by'] = data['created_by']
        strip_data['created_at'] = self.utc_to_jst(data['created_at'])
        strip_data['updated_at'] = self.utc_to_jst(data['updated_at'])

        return strip_data

    def utc_to_jst(self, timestamp_utc):
        datetime_utc = datetime.datetime.strptime(
            timestamp_utc, "%d %b %Y %H:%M")
        datetime_jst = datetime_utc + datetime.timedelta(hours=+9)
        timestamp_jst = datetime.datetime.strftime(
            datetime_jst, "%d %b %Y %H:%M")

        return timestamp_jst
