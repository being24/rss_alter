import json
import os
import pathlib

from dotenv import load_dotenv
from models import ThreadInfo


class NewThreads:
    def __init__(self):
        root_path = pathlib.Path(__file__).parents[1]
        dotenv_path = root_path / ".env"
        load_dotenv(dotenv_path)

        webhook_url = os.getenv("TEST")

        assert webhook_url is not None

        config_path = root_path / "data" / "NewThreads.json"

        self.configs = []

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)


if __name__ == "__main__":
    nt = NewThreads()
