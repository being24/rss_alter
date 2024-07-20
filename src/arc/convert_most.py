# convert old db to new db

from models import ArticleInfo, ThreadInfo, convert_datetime
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


old_db = create_engine("sqlite:///data/data_old.sqlite3")
new_db = create_engine("sqlite:///data/data.sqlite3")

old_session = sessionmaker(old_db)
new_session = sessionmaker(new_db)

# create new db

Base = declarative_base()


class Thread(Base):
    __tablename__ = "thread"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    author = Column(String)
    datetime = Column(DateTime)
    type = Column(String)


class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    tags = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    type = Column(String)


with old_session() as session:
    metadata = MetaData()
    metadata.reflect(bind=old_db)
    threads = []
    articles = []

    for table in metadata.sorted_tables:
        table_name = table.name
        table = Table(table_name, metadata, autoload=True, autoload_with=old_db)

        print(f"Converting {table_name}...")

        # get data
        data: list = session.query(table).all()

        if table_name == "announcement":
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="announcement",
                )
                for row in data
            ]

            threads.extend(data)

        elif table_name == "bosyuu":
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="call_for_opinions",
                )
                for row in data
            ]

            threads.extend(data)

        elif table_name == "common":
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="common",
                )
                for row in data
            ]

            threads.extend(data)

        elif table_name == "criticism_in":
            data = [
                ArticleInfo(
                    url="http://scp-jp-sandbox3.wikidot.com/" + row.url,
                    title=row.title,
                    tags=row.tags.replace(" ", ","),
                    created_by=row.created_by,
                    created_at=convert_datetime(row.created_at),
                    updated_at=convert_datetime(row.updated_at),
                    type="criticism_in",
                )
                for row in data
            ]

            articles.extend(data)

        elif table_name == "image":
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="media_provide",
                )
                for row in data
            ]

            threads.extend(data)

        if table_name == "init":
            pass

        elif table_name == "kyara":
            # kyaraテーブルの処理
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="character_hub",
                )
                for row in data
            ]

            threads.extend(data)

        elif table_name == "notification":
            # notificationテーブルの処理
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="notification",
                )
                for row in data
            ]

            threads.extend(data)

        elif table_name == "policy":
            # policyテーブルの処理
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="policy",
                )
                for row in data
            ]

            threads.extend(data)

        elif table_name == "recently_created":
            # recently_createdテーブルの処理
            data = [
                ArticleInfo(
                    url="http://scp-jp.wikidot.com/" + row.url,
                    title=row.title,
                    tags=row.tags.replace(" ", ","),
                    created_by=row.created_by,
                    created_at=convert_datetime(row.created_at),
                    updated_at=convert_datetime(row.updated_at),
                    type="recently_created",
                )
                for row in data
            ]

            articles.extend(data)

        elif table_name == "setting":
            # settingテーブルの処理
            pass

        elif table_name == "suggestion":
            # suggestionテーブルの処理
            data = [
                ThreadInfo(
                    url=row.url,
                    title=row.title,
                    author=row.author,
                    datetime=row.datetime,
                    type="suggestion",
                )
                for row in data
            ]

            threads.extend(data)

    # sort by datetime
    threads.sort(key=lambda x: x.datetime)
    articles.sort(key=lambda x: x.created_at)

    print(threads[0])
    print(articles[0])

# insert data
with new_session() as session:
    for thread in threads:
        session.add(
            Thread(
                url=thread.url,
                title=thread.title,
                author=thread.author,
                datetime=thread.datetime,
                type=thread.type,
            )
        )

    for article in articles:
        session.add(
            Article(
                url=article.url,
                title=article.title,
                tags=article.tags,
                created_by=article.created_by,
                created_at=article.created_at,
                updated_at=article.updated_at,
                type=article.type,
            )
        )

    session.commit()
