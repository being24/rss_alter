#!/usr/bin/env python
# coding: utf-8

import unicodedata
import difflib
import itertools
import re

from sqlite_util import SQlite


class AgeFlyer():
    def __init__(self) -> None:
        pass

    def fly(self, word1: str, word2: str) -> float:
        '''
        p = re.compile(r'[0-9a-zA-Z- ]')
        clean_word1 = p.sub('', word1)
        clean_word2 = p.sub('', word2)
        '''
        xxx = re.compile(r'SCP-X*')
        jp = re.compile(r'-JP')
        # code_regex = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％：　 ]')
        draft = re.compile(r'[下書き]')

        clean_word1 = xxx.sub('', word1)
        clean_word2 = xxx.sub('', word2)
        clean_word1 = jp.sub('', clean_word1)
        clean_word2 = jp.sub('', clean_word2)
        # clean_word1 = code_regex.sub('', clean_word1)
        # clean_word2 = code_regex.sub('', clean_word2)
        clean_word1 = draft.sub('', clean_word1)
        clean_word2 = draft.sub('', clean_word2)

        # unicodedata.normalize() で全角英数字や半角カタカナなどを正規化する
        normalized_str1 = unicodedata.normalize(
            'NFKC', clean_word1)
        normalized_str2 = unicodedata.normalize(
            'NFKC', clean_word2)

        # 類似度を計算、0.0~1.0 で結果が返る
        def isjunk(c):
            return c in ["-", "(", ")", ]
        s = difflib.SequenceMatcher(
            None, normalized_str1, normalized_str2).ratio()
        '''
        if s >= 0.4:
            print(word1, "<~>", word2)
            print(clean_word1, "<~>", clean_word2)
            print("match ratio:", s, "\n")
            return True
        else:
            return False
        '''
        return s

    def fly_list(self, titles):
        for combination in itertools.combinations(titles, 2):
            self.fly(combination[0], combination[1])


if __name__ == "__main__":
    age = AgeFlyer()
    db = SQlite()

    table_name = 'criticism_in'
    created_by = 'thor_taisho'
    same_author_sql = f'SELECT * FROM "{table_name}" WHERE created_by="{created_by}"'
    title = 'SCP-5552: Our Stolen Theory - 奪われし理論 (1)'

    result = db.get(same_author_sql)
    # for i in result:
    #     age.fly(title, i.title)

    titles = [
        'SCP-XXX 夢見る風船',
        '夢見る風船　-9',
        '答えが見つかるまでは　明快ver',
        '答えが見つかるまでは　-11',
        'SCP-XXXX-JP 起源の石',
        'SCP-XXXX-JP 起源の石',
        'SCP-XXXX-JP 書けない',
        '書けない',
        'SCP-XXXX-JP そんなバハマ',
        'SCP-2012-JP そんなバハマ',
        '「魔か不思議の餃子」',
        '「食べられる餃子」',
        '元も”子”もないボールプール(改良１)',
        '元も”子”もないボールプール(改良１再投稿)',
        '蟷螂の卵',
        'カマキリの卵',
        'SCP-XXX-JP',
        'SCP-XXX-JP 改訂版',
        '下書き「恥ずかしい」',
        '下書き「恥ずかしい」'

    ]
    age.fly_list(titles)
