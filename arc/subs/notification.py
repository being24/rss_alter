# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import pathlib
from datetime import datetime
from typing import List, Optional

import pytz
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String

Base = declarative_base()


@dataclasses.dataclass
class Notification:
    url: str
    title: str
    author: str
    datetime: datetime


class NotificationDB(Base):
    __tablename__ = "notification"

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class NotificationManager:
    def __init__(self):
        data_path = pathlib.Path(__file__).parents[1]
        data_path /= "../data"
        data_path = data_path.resolve()
        db_path = data_path
        db_path /= "./data.sqlite3"
        engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=engine)

        self.create_table(engine)

    def create_table(self, engine):
        NotificationDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        NotificationDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Notification) -> NotificationDB:
        """dataclassをカラムに変換する

        Args:
            data (Notification): dataclass

        Returns:
            NotificationDB: カラム
        """
        NotificationManager = NotificationDB(
            url=data.url, title=data.title, author=data.author, datetime=data.datetime
        )

        return NotificationManager

    @staticmethod
    def return_dataclass(data: NotificationDB) -> Notification:
        """カラムをdataclassに変換する

        Args:
            data (NotificationDB): カラム

        Returns:
            Notification: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        NotificationManager = Notification(
            url=data.url, title=data.title, author=data.author, datetime=datetime
        )
        return NotificationManager

    def get_data(self, url: str) -> Optional[Notification]:
        with self.Session() as session:
            NotificationManager = (
                session.query(NotificationDB).filter_by(url=url).first()
            )
            if NotificationManager is None:
                return None
            return self.return_dataclass(NotificationManager)

    def get_all_data(self) -> List[Notification]:
        with self.Session() as session:
            notificationManagers = session.query(NotificationDB)
            return [
                self.return_dataclass(NotificationManager)
                for NotificationManager in notificationManagers
            ]

    def register_data(self, data: Notification) -> None:
        with self.Session() as session:
            stmt = insert(NotificationDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime,
            )

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[NotificationDB.url],
                set_=dict(title=data.title, author=data.author, datetime=data.datetime),
            )

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Notification):
        self.delete_notificationManager(data.url)
        data.url = data.url.replace("http://scp-jp.wikidot.com/forum/", "")
        self.register_data(data)
        print("Converted URL:", data.url)

    def delete_notificationManager(self, url: str) -> None:
        with self.Session() as session:
            session.query(NotificationDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = NotificationManager()
    data_list = db.get_all_data()
    data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
    # db.register_datas([test, test2])
