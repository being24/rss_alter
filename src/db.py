import pathlib
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import Mapped, declarative_base

Base = declarative_base()


db_path = pathlib.Path(__file__).parents[1] / "data/data.sqlite3"
db_path.resolve()

engine = create_engine(f"sqlite:///{db_path}")


class Thread(Base):
    __tablename__ = "thread"

    id: Mapped[int] = Column(Integer, primary_key=True)
    url: Mapped[str] = Column(String)
    title: Mapped[str] = Column(String)
    author: Mapped[str] = Column(String)
    datetime: Mapped[datetime] = Column(DateTime)
    type: Mapped[str] = Column(String)


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = Column(Integer, primary_key=True)
    url: Mapped[str] = Column(String)
    title: Mapped[str] = Column(String)
    tags: Mapped[str] = Column(String)
    created_by: Mapped[str] = Column(String)
    created_at: Mapped[datetime] = Column(DateTime)
    updated_at: Mapped[datetime] = Column(DateTime)
    type: Mapped[str] = Column(String)
