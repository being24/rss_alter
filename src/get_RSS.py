import json
import pathlib

import listpages_get


# from webhook import webhook

data_path = pathlib.Path(__file__).parent
data_path /= '../data'
data_path = data_path.resolve()


def dump_json(json_data):
    with open(data_path / 'config.json', "w") as f:
        json.dump(
            json_data,
            f,
            ensure_ascii=False,
            indent=4,
            separators=(
                ',',
                ': '))


notified_dict = {}
RSS_key = 'most-recently-created'

if __name__ == "__main__":
    lp = listpages_get.listpages_util()
    data = lp.LIST_PAGES(limit='30')
    print(data)
