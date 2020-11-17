# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import sqlite3
from typing import NamedTuple


class SQlite():
    def __init__(self):
        data_path = pathlib.Path(__file__).parent
        data_path /= '../data'
        data_path = data_path.resolve()
        self.db_path = data_path
        self.db_path /= './data.sqlite3'

        if not self.db_path.exists():
            self.create_db('init')

        self.con = self._connect()

    def create_db(self, table_name):
        db = sqlite3.connect(self.db_path)
        db.execute(
            f'create table if not exists "{table_name}"'
            '(url TEXT PRIMARY KEY, title TEXT, tags TEXT,'
            'created_by TEXT, created_at TEXT, updated_at TEXT)')

    def _connect(self):
        con = sqlite3.connect(f'{self.db_path}')
        con.row_factory = sqlite3.Row
        return con

    def create_table(self, sql):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(sql)

        conn.commit()
        conn.close()

    def execute(self, sql: str, data: tuple):
        cur = self.con.cursor()
        try:
            cur.execute(sql, data)
        except sqlite3.IntegrityError as e:
            print(f"主キーが重複しています{e}")

        self.con.commit()

    def executemany(self, sql: str, data_list: list):
        cur = self.con.cursor()
        try:
            cur.executemany(sql, data_list)
        except sqlite3.IntegrityError as e:
            print(f"主キーが重複しています{e}")

        self.con.commit()

    def get(self, sql: str) -> list:
        cur = self.con.cursor()

        cur.execute(sql)

        fieldname_list = [(field[0], type(field[0]))
                          for field in cur.description]
        RowNamedtuple = NamedTuple("RowNamedtuple", fieldname_list)
        rows = [RowNamedtuple._make(row) for row in cur]
        return rows

    def is_exist(self, sql: str) -> bool:
        cur = self.con.cursor()
        cur.execute(sql)
        result = cur.fetchall()[0][0]

        return(result)


if __name__ == "__main__":
    db = SQlite()
    table_name = 'criticism_in'
    db.create_db(table_name)
    '''
    insert_sql = f'INSERT INTO "{table_name}"( url, title, tags, created_by, created_at, updated_at ) VALUES( ?, ?, ?, ?, ?, ? ) ON  conflict( url ) DO UPDATE SET tags = excluded.tags, updated_at = excluded.updated_at'
    data = (
        'url',
        'author',
        'tag2',
        'created_by',
        'created_at',
        'updated_at2')

    db.execute(insert_sql, data)
    '''
    '''
    url = 'operation-tungsten-gargantua-05'

    get_sql = f'SELECT COUNT(*) FROM "{table_name}" WHERE url="{url}"'

    result = db.is_exist(get_sql)
    print(result)
    '''

    created_by = 'thor_taisho'
    same_author_sql = f'SELECT * FROM "{table_name}" WHERE created_by="{created_by}"'

    result = db.get(same_author_sql)
    for i in result:
        print(i.title)
