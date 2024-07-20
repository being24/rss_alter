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
class Characterhub:
    url: str
    title: str
    author: str
    datetime: datetime


class CharacterhubDB(Base):
    __tablename__ = "characterhub"

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class CharacterhubManager:
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
        CharacterhubDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        CharacterhubDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Characterhub) -> CharacterhubDB:
        """dataclassをカラムに変換する

        Args:
            data (Characterhub): dataclass

        Returns:
            CharacterhubDB: カラム
        """
        characterhub = CharacterhubDB(
            url=data.url, title=data.title, author=data.author, datetime=data.datetime
        )

        return characterhub

    @staticmethod
    def return_dataclass(data: CharacterhubDB) -> Characterhub:
        """カラムをdataclassに変換する

        Args:
            data (CharacterhubDB): カラム

        Returns:
            Characterhub: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        characterhub = Characterhub(
            url=data.url, title=data.title, author=data.author, datetime=datetime
        )
        return characterhub

    def get_data(self, url: str) -> Optional[Characterhub]:
        with self.Session() as session:
            characterhub = session.query(CharacterhubDB).filter_by(url=url).first()
            if characterhub is None:
                return None
            return self.return_dataclass(characterhub)

    def get_all_data(self) -> List[Characterhub]:
        with self.Session() as session:
            characterhubs = session.query(CharacterhubDB)
            return [
                self.return_dataclass(characterhub) for characterhub in characterhubs
            ]

    def register_data(self, data: Characterhub) -> None:
        with self.Session() as session:
            stmt = insert(CharacterhubDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime,
            )

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[CharacterhubDB.url],
                set_=dict(title=data.title, author=data.author, datetime=data.datetime),
            )

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Characterhub):
        self.delete_characterhub(data.url)
        data.url = data.url.replace("http://scp-jp.wikidot.com/forum/", "")
        self.register_data(data)
        print("Converted URL:", data.url)

    def delete_characterhub(self, url: str) -> None:
        with self.Session() as session:
            session.query(CharacterhubDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = CharacterhubManager()
    data_list = db.get_all_data()
    data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
    # db.register_datas([test, test2])
