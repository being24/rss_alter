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
class Image:
    url: str
    title: str
    author: str
    datetime: datetime


class ImageDB(Base):
    __tablename__ = 'image'

    url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)

    def __init__(self, url, title, author, datetime):
        self.url = url
        self.title = title
        self.author = author
        self.datetime = datetime


class ImageManager():
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
        ImageDB.metadata.create_all(bind=engine, checkfirst=True)

    def delete_table(self, engine):
        ImageDB.metadata.drop_all(bind=engine, checkfirst=True)

    @staticmethod
    def convert_to_column(data: Image) -> ImageDB:
        """dataclassをカラムに変換する

        Args:
            data (Image): dataclass

        Returns:
            ImageDB: カラム
        """
        image = ImageDB(
            url=data.url,
            title=data.title,
            author=data.author,
            datetime=data.datetime)

        return image

    @staticmethod
    def return_dataclass(data: ImageDB) -> Image:
        """カラムをdataclassに変換する

        Args:
            data (ImageDB): カラム

        Returns:
            Image: dataclass
        """
        datetime = pytz.utc.localize(data.datetime)
        image = Image(
            url=data.url,
            title=data.title,
            author=data.author,
            datetime=datetime)
        return image

    def get_data(self, url: str) -> Optional[Image]:
        with self.Session() as session:
            image = session.query(
                ImageDB).filter_by(url=url).first()
            if image is None:
                return None
            return self.return_dataclass(image)

    def get_all_data(self) -> List[Image]:
        with self.Session() as session:
            images = session.query(ImageDB)
            return [self.return_dataclass(image)
                    for image in images]

    def register_data(self, data: Image) -> None:
        with self.Session() as session:
            stmt = insert(ImageDB).values(
                url=data.url,
                title=data.title,
                author=data.author,
                datetime=data.datetime)

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=[ImageDB.url],
                set_=dict(
                    title=data.title,
                    author=data.author,
                    datetime=data.datetime))

            session.execute(do_update_stmt)
            session.commit()

    def convert_url(self, data: Image):
        self.delete_image(data.url)
        data.url = data.url.replace('http://scp-jp.wikidot.com/forum/', '')
        self.register_data(data)
        print('Converted URL:', data.url)

    def delete_image(self, url: str) -> None:
        with self.Session() as session:
            session.query(ImageDB).filter_by(url=url).delete()
            session.commit()


if __name__ == "__main__":
    db = ImageManager()
    data_list = db.get_all_data()
    # data = [db.convert_url(data) for data in data_list]
    for d in data_list:
        print(d)
