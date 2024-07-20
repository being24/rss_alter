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
class Solicitation:
    url: str
    title: str
    author: str
    datetime: datetime


class SolicitationDB(Base):
    __tablename__ = "solicitation"

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class SolicitationManager:
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
        SolicitationDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        SolicitationDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Solicitation) -> SolicitationDB:
        """dataclassをカラムに変換する

        Args:
            data (Solicitation): dataclass

        Returns:
            SolicitationDB: カラム
        """
        solicitation = SolicitationDB(
            url=data.url, title=data.title, author=data.author, datetime=data.datetime
        )

        return solicitation

    @staticmethod
    def return_dataclass(data: SolicitationDB) -> Solicitation:
        """カラムをdataclassに変換する

        Args:
            data (SolicitationDB): カラム

        Returns:
            Solicitation: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        solicitation = Solicitation(
            url=data.url, title=data.title, author=data.author, datetime=datetime
        )
        return solicitation

    def get_data(self, url: str) -> Optional[Solicitation]:
        with self.Session() as session:
            solicitation = session.query(SolicitationDB).filter_by(url=url).first()
            if solicitation is None:
                return None
            return self.return_dataclass(solicitation)

    def get_all_data(self) -> List[Solicitation]:
        with self.Session() as session:
            solicitations = session.query(SolicitationDB)
            return [
                self.return_dataclass(solicitation) for solicitation in solicitations
            ]

    def register_data(self, data: Solicitation) -> None:
        with self.Session() as session:
            stmt = insert(SolicitationDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime,
            )

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[SolicitationDB.url],
                set_=dict(title=data.title, author=data.author, datetime=data.datetime),
            )

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Solicitation):
        self.delete_solicitation(data.url)
        data.url = data.url.replace("http://scp-jp.wikidot.com/forum/", "")
        self.register_data(data)
        print("Converted URL:", data.url)

    def delete_solicitation(self, url: str) -> None:
        with self.Session() as session:
            session.query(SolicitationDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = SolicitationManager()
    data_list = db.get_all_data()
    # data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
    # db.register_datas([test, test2])
