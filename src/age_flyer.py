import difflib
import itertools
import re
import unicodedata


class AgeFlyer:
    def __init__(self) -> None:
        pass

    def preprocess(self, word: str) -> str:
        re_jp = re.compile(r"\w{3}-.{3,5}-JP")
        re_cn = re.compile(r"\w{3}-CN-.{3,5}")
        re_en = re.compile(r"\w{3}-\w{3,5}")

        if word is None:
            return ""

        clean_word = word
        clean_word = re_jp.sub("", clean_word)
        clean_word = re_cn.sub("", clean_word)
        clean_word = re_en.sub("", clean_word)
        clean_word = "".join(char for char in clean_word if char.isalnum())

        clean_word = clean_word.replace("SCP下書き", "")
        clean_word = clean_word.replace("下書き", "")
        clean_word = clean_word.replace("闇寿司ファイル", "")

        clean_word = unicodedata.normalize("NFKC", clean_word)

        return clean_word

    def fry(self, new: str, old: str) -> float:
        new = self.preprocess(new)
        old = self.preprocess(old)

        s = difflib.SequenceMatcher(None, new, old).ratio()

        return s

    def pop_in(self, titles: list):
        for combination in itertools.combinations(titles, 2):
            self.fry(combination[0], combination[1])


if __name__ == "__main__":
    samples = [
        "SCP-1382-JP - 暗中の救助信号",
        "SCP-XXX-JPてすと",
        "SCP",
        "Tale",
        '闇寿司ファイルNo.119 "握手"',
        "SCP-CN-1129 - 膨化",
        "SCP下書き「未認可霊柩車」",
        "SCP-XXXX",
        "改稿人類",
        "SCP-XXX-JP - 三夏への手向け(下書き)",
        "SCP-XXX-JP - あの橋を目指せ(下書き)",
        "SCP-XXX-JP - 絶え間ない空旅(下書き)",
        "SCP-XXX-JP - 魔王は勇者がだーいすき！(下書き)",
        "SCP-XXX 夢見る風船",
        "夢見る風船　-9",
        "答えが見つかるまでは　明快ver",
        "答えが見つかるまでは　-11",
        "SCP-XXXX-JP 起源の石",
        "SCP-XXXX-JP 起源の石",
        "SCP-XXXX-JP 書けない",
        "書けない",
        "SCP-XXXX-JP そんなバハマ",
        "SCP-2012-JP そんなバハマ",
        "「魔か不思議の餃子」",
        "「食べられる餃子」",
        "元も”子”もないボールプール(改良１)",
        "元も”子”もないボールプール(改良１再投稿)",
        "蟷螂の卵",
        "カマキリの卵",
        "SCP-XXX-JP",
        "SCP-XXX-JP 改訂版",
    ]

    titles = [
        "SCP-XXX 夢見る風船",
        "夢見る風船　-9",
        "答えが見つかるまでは　明快ver",
        "答えが見つかるまでは　-11",
        "SCP-XXXX-JP 起源の石",
        "SCP-XXXX-JP 起源の石",
        "SCP-XXXX-JP 書けない",
        "書けない",
        "SCP-XXXX-JP そんなバハマ",
        "SCP-2012-JP そんなバハマ",
        "「魔か不思議の餃子」",
        "「食べられる餃子」",
        "元も”子”もないボールプール(改良１)",
        "元も”子”もないボールプール(改良１再投稿)",
        "蟷螂の卵",
        "カマキリの卵",
        "SCP-XXX-JP",
        "SCP-XXX-JP 改訂版",
        "SCP-XXX-JP - 三夏への手向け(下書き)",
        "SCP-XXX-JP - あの橋を目指せ(下書き)",
        "SCP-XXX-JP - 絶え間ない空旅(下書き)",
        "SCP-XXX-JP - 魔王は勇者がだーいすき！(下書き)",
        "SCP-1382-JP - 暗中の救助信号",
        "SCP-3182-JP - 清適の湯",
    ]
    age = AgeFlyer()
    age.pop_in(samples)
