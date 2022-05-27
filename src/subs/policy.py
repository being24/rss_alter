# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import pathlib
from datetime import datetime
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
class Policy:
    url: str
    title: str
    author: str
    datetime: datetime


class PolicyDB(Base):
    __tablename__ = 'policy'

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class PolicyManager():
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
        PolicyDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        PolicyDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Policy) -> PolicyDB:
        """dataclassをカラムに変換する

        Args:
            data (Policy): dataclass

        Returns:
            PolicyDB: カラム
        """
        PolicyManager = PolicyDB(
            url=data.url,
            title=data.title,
            author=data.author,
            datetime=data.datetime)

        return PolicyManager

    @staticmethod
    def return_dataclass(data: PolicyDB) -> Policy:
        """カラムをdataclassに変換する

        Args:
            data (PolicyDB): カラム

        Returns:
            Policy: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        PolicyManager = Policy(
            url=data.url,
            title=data.title,
            author=data.author,
            datetime=datetime)
        return PolicyManager

    def get_data(self, url: str) -> Optional[Policy]:
        with self.Session() as session:
            PolicyManager = session.query(
                PolicyDB).filter_by(url=url).first()
            if PolicyManager is None:
                return None
            return self.return_dataclass(PolicyManager)

    def get_all_data(self) -> List[Policy]:
        with self.Session() as session:
            PolicyManagers = session.query(PolicyDB)
            return [self.return_dataclass(PolicyManager)
                    for PolicyManager in PolicyManagers]

    def register_data(self, data: Policy) -> None:
        with self.Session() as session:
            stmt = insert(PolicyDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime)

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[PolicyDB.url],
                set_=dict(
                    title=data.title,
                    author=data.author,
                    datetime=data.datetime))

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Policy):
        self.delete_PolicyManager(data.url)
        data.url = data.url.replace('http://scp-jp.wikidot.com/forum/', '')
        self.register_data(data)
        print('Converted URL:', data.url)

    def delete_PolicyManager(self, url: str) -> None:
        with self.Session() as session:
            session.query(PolicyDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = PolicyManager()
    data_list = db.get_all_data()
    data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
    # db.register_datas([test, test2])
