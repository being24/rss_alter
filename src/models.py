from datetime import datetime

from pydantic import BaseModel


def convert_datetime(string: str) -> datetime:
    new = datetime.strptime(string, "%d %b %Y %H:%M")
    return new


class ThreadInfo(BaseModel):
    url: str
    title: str
    author: str
    datetime: datetime
    type: str = "thread"


class ArticleInfo(BaseModel):
    url: str
    title: str
    tags: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    type: str = "article"


class ThreadsConfig(BaseModel):
    display_name: str
    category_id: int
    type: str


class Feed(BaseModel):
    link: str
    published: datetime
    summary: str
    title: str
    wikidot_author_name: str
    wikidot_author_id: int
    type: str = "feed"
