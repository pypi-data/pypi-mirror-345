"""
假设我们得到了四个字符, 现在我们要正确的排序(语序)
1. 对这个四个字符进行排列组合,
2. 对每一个排列组合进行判断, 判断这个排列是否出现在数据库中,
    2.1 如果出现, 则返回这个排列组合
    2.2. 如果没有, 则返回None
3. 如果没有找到, 则可能是传递的 word 书写错误,尝试利用正则进行匹配
4. 实在没有,则返回随机组合
# 需要在 构造一个 dbdata/frequency.csv,  第一列是 word,第二列是 count(频率)
# 用于判断这个排列组合是否在数据库中
"""

import itertools
import random
from typing import List
import pandas as pd
from pathlib import Path

from collections import Counter
import importlib.resources as pkg_resources
from . import data  # 确保 src/cfun/data/__init__.py 存在


class Phrase:
    basedb_path = pkg_resources.files(data).joinpath("frequency.parquet")

    def __init__(self, userdb: str = "", corrector: str = "charsimilar"):
        """
        根据短语，返回正确的语序
        :param userdb: 用户自定义的数据库， 如果不传入，则使用默认的数据库, 数据库应该有两列，word 和 count列
        :param corrector: 是否使用纠错器, 纠正器的类型
            - charsimilar 版本有点旧， 可能会有冲突，但速度快，精准度还可以
            - bert 版本比较新， 速度慢， 但是精准度高
        """
        self.userdb = self._load_dataframe(userdb) if userdb else None
        self.basedb = self._load_dataframe(self.basedb_path)
        self.db = self._merge_databases()

        if corrector in ["bert", "charsimilar"]:
            self.corrector_type = corrector
        else:
            self.corrector_type = False
        self.corrector = self._loadcorrector() if self.corrector_type else None

    @staticmethod
    def generate_permutations(fragment: str) -> List[str]:
        """
        生成给定字符列表的所有排列组合
        :param fragment: 字符串
        :return: 所有排列组合的列表
        """
        assert isinstance(fragment, str) and len(fragment) > 0, "fragment must be a non-empty string"
        chars = list(fragment)
        assert all(len(c) == 1 for c in chars), "Each character must be a single letter."
        return ["".join(p) for p in itertools.permutations(chars)]

    def _loadcorrector(self):
        """加载纠错器"""
        if self.corrector_type == "bert":
            from pycorrector import MacBertCorrector

            return MacBertCorrector("shibing624/macbert4csc-base-chinese")
        elif self.corrector_type == "charsimilar":
            from char_similar_z import std_cal_sim

            return std_cal_sim

    @staticmethod
    def _load_dataframe(path: Path | str) -> pd.DataFrame:
        """加载数据
        :param path: 数据库路径
        :return: DataFrame
        """
        if isinstance(path, str):
            path = Path(path)
        assert path.exists(), f"{path} does not exist"
        if path.suffix == ".csv":
            return pd.read_csv(str(path), encoding="utf-8", dtype={"word": str, "count": int})
        elif path.suffix == ".parquet":
            return pd.read_parquet(str(path))
        else:
            raise ValueError("Unsupported file type. Only .csv and .parquet are supported.")

    # 模糊匹配 --- 正则匹配
    @staticmethod
    def generate_regex_patterns(s, n=1):

        assert isinstance(s, str), "s must be a string"
        assert isinstance(n, int), "n must be an integer"
        assert 1 <= n <= len(s), "n 必须在 1 和字符串长度之间"

        patterns = []
        # 获取所有可能的 n 个位置的组合
        indices_combinations = itertools.combinations(range(len(s)), n)
        # 对每个组合生成对应的正则表达式

        for indices in indices_combinations:
            # 创建一个列表，把原字符串变为可变的列表
            # 用 '.' 替换这些位置的字符
            temp = list(s)
            for index in indices:
                temp[index] = "."

            # 把列表重新合成字符串
            patterns.append("".join(temp))
        return patterns

    @staticmethod
    def get_ordinal_string(fragment, target) -> str:
        """
        根据findstring中字符的顺序重新排列phrase中的字符
        如果findstring中有的字符在phrase中没有出现，则用phrase中剩余的字符随机替换
        :param fragment: 原始字符串（目标顺序）   eg: 收下留情
        :param target: 匹配到的字符串（目标顺序） eg:  手下留情
        :return: 重排后的字符串
        """
        assert len(fragment) == len(target), "fragment and target must have the same length"

        # 利用原始的字符串进行组合, 因为我们找的的字符串和 fragment 不一定相同
        p_chars = list(fragment)
        f_chars = list(target)
        # 如果 fragment 中有重复字符（例如 ["a","a","b","c"]），使用集合会丢失这个信息,因此使用列表推导式
        residual = [c for c in p_chars if c not in f_chars]
        random.shuffle(residual)  # 预先打乱剩余字符以提高随机性
        # 构建结果字符串
        residual_iter = iter(residual)
        return "".join(char if char in p_chars else next(residual_iter) for char in f_chars)

    def _merge_databases(self) -> pd.DataFrame:
        """合并用户数据库和基础数据库"""
        if self.userdb is None:
            return self.basedb
        # 合并用户数据库和基础数据库
        df_user = self.userdb.copy()
        df_base = self.basedb.copy()
        df = pd.concat([df_user, df_base]).drop_duplicates("word", keep="last")
        return df.sort_values(by="count", ascending=False).reset_index(drop=True)

    # 获取数据库中的匹配(完全匹配)
    def best_match_from_db(self, permutations: List[str]) -> str:
        """
        批量查找数据库中的匹配
        :param permutations: 字符串列表(所有的可能组合)
        :return: 字符串
        eg:
        permutations = ["首虾留情", "首留情虾", "虾首留情", "虾留情首", "留情首虾", "留情虾首"]

        """
        assert isinstance(permutations, list), "permutations must be a list"
        matched = self.db[self.db["word"].isin(permutations)]
        if not matched.empty:
            # 如果找到了匹配的词, 则返回第一个(频率最高的)
            matched = matched.drop_duplicates(subset=["word"], keep="last")
            matched = matched.sort_values(by="count", ascending=False).reset_index(drop=True)
            # 取出第一个词
            return matched.iloc[0]["word"]
        return ""

    # 模糊匹配 --- 正则匹配
    def best_match_from_regex(self, permutations: List[str], n: int = 1) -> tuple[str, pd.DataFrame]:
        """
        对带有正则通配符的字符串组合进行模糊匹配
        :param permutations: 所有的可能组合(里面含有正则通配符)
        :param n: 替换成正则通配符 '.' 的字符数量
        :return: 匹配到最有可能的字符串, 以及 匹配到的所有可能组成的 DataFrame
        :rtype: tuple[str, pd.DataFrame]
        :example:
        permutations = ["首虾留情", "首留情虾", "虾首留情", "虾留情首", "留情首虾", "留情虾首"]
        n = 1
        """
        assert isinstance(permutations, list), "permutations must be a list"
        assert len(permutations) > 0, "permutations must not be empty"

        # 预先生成所有正则模式
        # patterns = []
        # for combo in permutations:
        #     patterns.extend(self.generate_regex_patterns(combo, n))
        # patterns = list(set(patterns))
        patterns = list({pattern for combo in permutations for pattern in self.generate_regex_patterns(combo, n)})

        regex = "|".join(f"({p})" for p in patterns)

        matched_df = self.db[self.db["word"].str.fullmatch(regex, na=False)]
        if not matched_df.empty:
            # 如果找到了匹配的词, 则返回第一个(频率最高的), 和所有匹配的 DataFrame
            matched_df = matched_df.drop_duplicates(subset=["word"], keep="last")
            result_df = matched_df.sort_values(by="count", ascending=False).reset_index(drop=True)
            return result_df.iloc[0]["word"], result_df
        return "", pd.DataFrame(columns=["word", "count"])

    def _bertcorrector(self, candidates: list[str]) -> tuple[bool, str, str]:
        """
        检查是否有错误
        :param candidates: 字符串列表 (想要检查的组合)
        :param fragment: 原始字符串 (无顺序)
        :return: (是否有错误, 错误的字符, 正确的字符)
        """
        if not self.corrector_type:
            return False, None, None
        corrected_list = self.corrector.correct_batch(candidates)

        # 提取并统计错误组合
        ie_list = [
            (e, r)
            for item in corrected_list
            if "errors" in item and len(item["errors"]) == 1
            for e, r, _ in item["errors"]
        ]
        # 如果没有错误组合，返回 False
        if not ie_list:
            return False, None, None

        # 找出最常见的第一个元素
        first_elements_count = Counter(e for e, _ in ie_list)
        most_common_first = first_elements_count.most_common(1)[0][0]

        # 筛选出所有第一个元素为 most_common_first 的元素
        filtered_ie_list = [x for x in ie_list if x[0] == most_common_first]

        # 找出最常见的第二个元素(在第一个的基础上)
        last_elements_count = Counter(r for _, r in filtered_ie_list)
        most_common_last = last_elements_count.most_common(1)[0][0]
        # 筛选出所有第二个元素为 most_common_last 的元素
        final_ie_list = [x for x in filtered_ie_list if x[1] == most_common_last]
        # 检查所有元素是否相同
        if final_ie_list and all(x == final_ie_list[0] for x in final_ie_list):
            return True, final_ie_list[0][0], final_ie_list[0][1]

        return False, None, None  # 如果没有找到符合条件的组合，返回 False

    def _charsimilarcorrector(self, match_df: pd.DataFrame, fragment: str) -> str:
        """
        字符相似度纠错器
        :param match_df: 匹配到的 DataFrame
        :param fragment: 原始字符串 (无顺序)
        :return: (是否有错误, 错误的字符, 正确的字符)
        pip install char-similar
        """
        # from char_similar_z import std_cal_sim

        # "all"(字形:拼音:字义=1:1:1)  # "w2v"(字形:字义=1:1)  # "pinyin"(字形:拼音=1:1)  # "shape"(字形=1)
        # 计算两个字符串的相似度， 先找出不同的字符，然后计算相似度
        cc = []  # 存储错误的字符和正确的字符, 以及候选字符串
        for index, row in match_df.iterrows():
            word, count = row["word"], row["count"]
            error1 = list(set(fragment) - set(word))
            right1 = list(set(word) - set(fragment))
            cc.append((error1[0], right1[0], word))

        sim = 0
        res = None
        for item in cc:
            error1, right1, word1 = item
            # 计算相似度
            simtmp = self.corrector(error1, right1, rounded=4, kind="pinyin")
            # print(f"error1: {error1}, right1: {right1}, word1: {word1}, simtmp: {simtmp}")
            if simtmp > sim:
                sim = simtmp
                res = word1
        return res

    def get_yuxu(self, fragment: str) -> tuple[str, str, bool]:
        """
        获取最可能的语序组合
        :param fragment: 传入的字符串
        :return: (原始组合, 数据库匹配组合, 是否完全匹配)
        """
        assert isinstance(fragment, str), "fragment must be a string"

        # 获取所有排列组合
        combinations = self.generate_permutations(fragment)

        # 获取数据库中的匹配
        matched = self.best_match_from_db(combinations)

        # 如果没有找到, 则可能是传递的 fragment 中存在错别字, 尝试利用正则进行匹配（模糊匹配）
        if matched == "":

            matched, match_df = self.best_match_from_regex(combinations, n=1)
            # print(f"模糊匹配的结果: {matched},fragment: {fragment},  match_df:\n{match_df} \n")
            # 如果 match_df 长度为空或为1，则直接返回
            if match_df.empty:
                matched = ""
            elif len(match_df) == 1:
                pass
            else:
                # 对模糊匹配的结果进行处理，找出最合理的字符串
                candidates = [self.get_ordinal_string(fragment, i) for i in match_df["word"]]
                if self.corrector_type == "bert":
                    # 这里的思路： 先把匹配到的字符串与原始字符串进行顺序还原，然后让bert纠错器进行纠错，看是否有错误，统计错误多的，
                    has_err, wrong, right = self._bertcorrector(candidates)
                    # 如果有错误的，则改成正确的
                    if has_err:
                        raw = candidates[0].replace(wrong, right)
                        combinations2 = self.generate_permutations(raw)
                        corrected = self.best_match_from_db(combinations2)
                        matched = corrected if corrected else matched
                elif self.corrector_type == "charsimilar":
                    # 这里的思路： 直接对模糊匹配的结果进行处理，找出所有错误，正确的字符组合，然后计算相似度，返回最相似的字符串
                    res = self._charsimilarcorrector(match_df, fragment)
                    matched = res if res else matched

        if matched != "":
            # 根据找到的组合,还原最终结果
            reword = self.get_ordinal_string(fragment, matched)
            return reword, matched, reword == matched
            # 返回, reword: 原来的语序, matched: 数据库中的语序(纠正后的), isfind: 是否正确
        else:
            # 证明在数据库中的确没有, 那么我们应该从网页上找(不一定能找到,因为错别字), 这里就直接返回随机组合
            return "".join(fragment), "", False


if __name__ == "__main__":

    p = Phrase(corrector="charsimilar")
    fragment = ["下收留情", "手下留情", "人七上下", "情首虾留", "将相王候"]
    for f in fragment:
        reword, matched, isright = p.get_yuxu(f)
        print(f"reword: {reword}, matched: {matched}, isright: {isright}")

    ######## 没有开启纠错器的情况下 ########
    # reword: 收下留情, matched: 手下留情, isright: False
    # reword: 手下留情, matched: 手下留情, isright: True
    # reword: 七上人下, matched: 七上八下, isright: False
    # reword: 情首虾留, matched: , isright: False
    # reword: 候王将相, matched: 帝王将相, isright: False
    ######## 开启纠错器的情况下 ########
    # reword: 收下留情, matched: 手下留情, isright: False
    # reword: 手下留情, matched: 手下留情, isright: True
    # reword: 七上人下, matched: 七上八下, isright: False
    # reword: 情首虾留, matched: , isright: False
    # reword: 王候将相, matched: 王侯将相, isright: False
