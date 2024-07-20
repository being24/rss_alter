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
class Suggestion:
    url: str
    title: str
    author: str
    datetime: datetime


class SuggestionDB(Base):
    __tablename__ = "suggestion"

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class SuggestionManager:
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
        SuggestionDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        SuggestionDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Suggestion) -> SuggestionDB:
        """dataclassをカラムに変換する

        Args:
            data (Suggestion): dataclass

        Returns:
            SuggestionDB: カラム
        """
        SuggestionManager = SuggestionDB(
            url=data.url, title=data.title, author=data.author, datetime=data.datetime
        )

        return SuggestionManager

    @staticmethod
    def return_dataclass(data: SuggestionDB) -> Suggestion:
        """カラムをdataclassに変換する

        Args:
            data (SuggestionDB): カラム

        Returns:
            Suggestion: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        SuggestionManager = Suggestion(
            url=data.url, title=data.title, author=data.author, datetime=datetime
        )
        return SuggestionManager

    def get_data(self, url: str) -> Optional[Suggestion]:
        with self.Session() as session:
            SuggestionManager = session.query(SuggestionDB).filter_by(url=url).first()
            if SuggestionManager is None:
                return None
            return self.return_dataclass(SuggestionManager)

    def get_all_data(self) -> List[Suggestion]:
        with self.Session() as session:
            suggestions = session.query(SuggestionDB)
            return [
                self.return_dataclass(SuggestionManager)
                for SuggestionManager in suggestions
            ]

    def register_data(self, data: Suggestion) -> None:
        with self.Session() as session:
            stmt = insert(SuggestionDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime,
            )

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[SuggestionDB.url],
                set_=dict(title=data.title, author=data.author, datetime=data.datetime),
            )

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Suggestion):
        self.delete_suggestion(data.url)
        data.url = data.url.replace("http://scp-jp.wikidot.com/forum/", "")
        self.register_data(data)
        print("Converted URL:", data.url)

    def delete_suggestion(self, url: str) -> None:
        with self.Session() as session:
            session.query(SuggestionDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = SuggestionManager()
    data_list = db.get_all_data()
    data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
    # db.register_datas([test, test2])
