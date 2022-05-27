# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import pathlib
from datetime import date, datetime
from typing import List, Optional

import pytz
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String

Base = declarative_base()


@dataclasses.dataclass
class Article:
    url: str
    title: str
    tags: list
    created_by: str
    created_at: datetime
    updated_at: datetime


class ArticleDB(Base):
    __tablename__ = 'criticism_in'

    url = Column(String, primary_key=True)
    title = Column(String)
    tags = Column(String)
    created_by = Column(String)
    created_at = Column(String)
    updated_at = Column(String)

    def __init__(self, url, title, tags, created_by, created_at, updated_at):
        self.url = url
        self.title = title
        self.tags = tags
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at


class ArticleManager():
    def __init__(self):
        data_path = pathlib.Path(__file__).parents[1]
        data_path /= '../data'
        data_path = data_path.resolve()
        db_path = data_path
        db_path /= './data.sqlite3'
        engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=engine)

        self.create_table(engine)

    def create_table(self, engine):
        ArticleDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        ArticleDB.metadata.drop_all(bind=engine, checkfirst=True)

    def convert_to_column(self, data: Article) -> ArticleDB:
        """dataclassをカラムに変換する

        Args:
            data (Article): dataclass

        Returns:
            ArticleDB: カラム
        """
        article = ArticleDB(
            url=data.url,
            title=data.title,
            tags=data.tags,
            created_by=data.created_by,
            created_at=data.created_at,
            updated_at=data.updated_at)

        return article

    def return_dataclass(self, data: ArticleDB) -> Article:
        """カラムをdataclassに変換する

        Args:
            data (ArticleDB): カラム

        Returns:
            Article: dataclass
        """
        created_at = self.convert_wikidot_time_to_datetime(data.created_at)
        updated_at = self.convert_wikidot_time_to_datetime(data.updated_at)
        tags = data.tags.split(',')
        article = Article(
            url=data.url,
            title=data.title,
            tags=tags,
            created_by=data.created_by,
            created_at=created_at,
            updated_at=updated_at)
        return article

    def convert_wikidot_time_to_datetime(self, time: str) -> datetime:
        """wikidotの時刻表示をdatetimeに変換する

        Args:
            time (str): wikidotの時刻表示

        Returns:
            datetime: datetime
        """
        _time = datetime.strptime(time, '%d %b %Y %H:%M')
        time_aware = pytz.utc.localize(_time)

        return time_aware

    def get_data(self, url: str) -> Optional[Article]:
        with self.Session() as session:
            article = session.query(
                ArticleDB).filter_by(url=url).first()
            if article is None:
                return None
            return self.return_dataclass(article)

    def get_all_data(self) -> List[Article]:
        with self.Session() as session:
            articles = session.query(ArticleDB)
            return [self.return_dataclass(article)
                    for article in articles]

    def register_data(self, data: Article) -> None:
        with self.Session() as session:
            stmt = insert(ArticleDB).values(
                url=data.url,
                title=data.title,
                tags=data.tags,
                created_by=data.created_by,
                created_at=data.created_at,
                updated_at=data.updated_at)

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[ArticleDB.url],
                set_=dict(
                    title=data.title,
                    tags=data.tags,
                    created_by=data.created_by,
                    created_at=data.created_at,
                    updated_at=data.updated_at))

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Article):
        self.delete_article(data.url)
        data.url = data.url.replace('http://scp-jp.wikidot.com/forum/', '')
        self.register_data(data)
        print('Converted URL:', data.url)

    def delete_article(self, url: str) -> None:
        with self.Session() as session:
            session.query(ArticleDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = ArticleManager()

    data_list = db.get_all_data()
    for d in data_list:
        print(d.created_at)
    # db.register_datas([test, test2])
