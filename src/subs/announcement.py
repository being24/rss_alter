# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import pathlib
from datetime import datetime
from turtle import right
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
class Announcement:
    url: str
    title: str
    author: str
    datetime: datetime


class AnnouncementDB(Base):
    __tablename__ = 'announcement'

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class AnnouncementManager():
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
        AnnouncementDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        AnnouncementDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Announcement) -> AnnouncementDB:
        """dataclassをカラムに変換する

        Args:
            data (Announcement): dataclass

        Returns:
            AnnouncementDB: カラム
        """
        announcement = AnnouncementDB(
            url=data.url,
            title=data.title,
            author=data.author,
            datetime=data.datetime)

        return announcement

    @staticmethod
    def return_dataclass(data: AnnouncementDB) -> Announcement:
        """カラムをdataclassに変換する

        Args:
            data (AnnouncementDB): カラム

        Returns:
            Announcement: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        announcement = Announcement(
            url=data.url,
            title=data.title,
            author=data.author,
            datetime=datetime)
        return announcement

    def get_data(self, url: str) -> Optional[Announcement]:
        with self.Session() as session:
            announcement = session.query(
                AnnouncementDB).filter_by(url=url).first()
            if announcement is None:
                return None
            return self.return_dataclass(announcement)

    def get_all_data(self) -> List[Announcement]:
        with self.Session() as session:
            announcements = session.query(AnnouncementDB)
            return [self.return_dataclass(announcement)
                    for announcement in announcements]

    def register_data(self, data: Announcement) -> None:
        with self.Session() as session:
            stmt = insert(AnnouncementDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime)

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[AnnouncementDB.url],
                set_=dict(
                    title=data.title,
                    author=data.author,
                    datetime=data.datetime))

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Announcement):
        self.delete_announcement(data.url)
        data.url = data.url.replace('http://scp-jp.wikidot.com/forum/', '')
        self.register_data(data)
        print('Converted URL:', data.url)

    def delete_announcement(self, url: str) -> None:
        with self.Session() as session:
            session.query(AnnouncementDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = AnnouncementManager()
    data_list = db.get_all_data()
    # data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
    # db.register_datas([test, test2])
