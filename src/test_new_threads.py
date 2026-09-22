from datetime import datetime

from models import Feed, ThreadsConfig
from new_threads import NewThreads


def _make_feed(link: str) -> Feed:
    return Feed(
        link=link,
        published=datetime(2026, 1, 1),
        summary="summary",
        title="title",
        wikidot_author_name="author",
        wikidot_author_id=1,
    )


def demo() -> None:
    common = ThreadsConfig(display_name="common", category_id=1, type="common")
    suggestion = ThreadsConfig(display_name="suggestion", category_id=2, type="suggestion")

    # 同一スレッドがhttp/https違いでcommon・suggestion両方のフィードに掲載されたケース
    configs_with_feeds = [
        (common, [_make_feed("http://scp-jp.wikidot.com/forum/t-1")]),
        (suggestion, [_make_feed("https://scp-jp.wikidot.com/forum/t-1")]),
    ]

    result = NewThreads.dedupe_new_feeds(configs_with_feeds, is_exist=lambda _: False)
    assert len(result) == 1, f"同一スレッドが重複して残った: {result}"
    assert result[0].type == "common", "最初に検出したconfigのtypeが優先されるべき"

    # DBに既存の場合は実行内重複チェック以前にスキップされる
    result_existing = NewThreads.dedupe_new_feeds(configs_with_feeds, is_exist=lambda _: True)
    assert result_existing == [], f"is_exist=Trueなのに登録候補が残った: {result_existing}"

    print("ok")


if __name__ == "__main__":
    demo()
