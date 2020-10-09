#!/usr/bin/env python
# coding: utf-8

import json
import pathlib


class BaseUtilities(object):
    def load_json(self, json_path: pathlib.Path) -> dict:
        if not json_path.exists():
            raise FileNotFoundError

        with open(json_path, encoding='utf-8') as f:
            json_dict = json.load(f)

        return json_dict

    def dump_json(self, json_path, data) -> None:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False)
