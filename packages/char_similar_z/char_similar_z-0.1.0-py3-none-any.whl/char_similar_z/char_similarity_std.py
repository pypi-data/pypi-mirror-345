from .path_config import get_dict
from typing import Union, Optional


class CharSimilarity:
    def __init__(self, code: int = 4, rounded: int = 4):
        self.code = code
        self.rounded = rounded
        self.dict_char_component = get_dict("component")
        self.dict_char_fourangle = get_dict("fourangle")
        self.dict_char_frequency = get_dict("frequency")
        self.dict_char_number = get_dict("number")
        self.dict_char_pinyin = get_dict("pinyin")
        self.dict_char_stroke = get_dict("stroke")
        self.dict_char_struct = get_dict("struct")
        self.dict_char_order = get_dict("order")

    def _sim_fourangle(self, char1: str, char2: str):
        """计算两汉字相似度, 通过四角码(只计算前4位)
        calculate similarity of two chars, by judge wether is the same fourangle
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.5
        """
        code = self.code
        char1_f4 = self.dict_char_fourangle.get(char1, "")
        char2_f4 = self.dict_char_fourangle.get(char2, "")
        result = 0
        if char1_f4 and char2_f4:
            same_count = sum(1 for cf1, cf2 in zip(char1_f4[:code], char2_f4[:code]) if cf1 == cf2)
            result = same_count / code
        return result

    def _sim_pinyin(self, char1: str, char2: str):
        """计算两汉字相似度, 通过两个字拼音(拼音/声母/韵母/声调)
        calculate similarity of two chars, by char pinyin
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.75
        """
        code = self.code
        char1_pi = self.dict_char_pinyin.get(char1, [])
        char2_pi = self.dict_char_pinyin.get(char2, [])
        result = 0
        if char1_pi and char2_pi:
            same_count = sum(1 for cp1, cp2 in zip(char1_pi, char2_pi) if cp1 == cp2)
            result = same_count / code
        return result

    def _sim_component(self, char1: str, char2: str):
        """计算两汉字相似度, 通过偏旁部首
        calculate similarity of two chars, by judge wether is the same component
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: int, eg. 1 or 0
        """
        char1_component = self.dict_char_component.get(char1, "")
        char2_component = self.dict_char_component.get(char2, "")
        result = 0
        if char1_component and char1_component == char2_component:
            result = 1
        return result

    def _sim_frequency(self, char1: str, char2: str):
        """计算两汉字相似度, 通过两个字频log10的(1- 绝对值差/最大值)
        calculate similarity of two chars, by char frequency
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.75
        """
        char1_fr = self.dict_char_frequency.get(char1, 0)
        char2_fr = self.dict_char_frequency.get(char2, 0)
        result = 0
        if char1_fr and char2_fr:
            result = 1 - abs((char1_fr - char2_fr) / max(char1_fr, char2_fr))
        return result

    def _sim_number(self, char1: str, char2: str):
        """计算两汉字相似度, 通过两个字笔画数的(1- 绝对值差/最大值)
        calculate similarity of two chars, by char number of stroke
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.75
        """
        char1_nu = self.dict_char_number.get(char1, 0)
        char2_nu = self.dict_char_number.get(char2, 0)
        result = 0
        if char1_nu and char2_nu:
            result = 1 - abs((char1_nu - char2_nu) / max(char1_nu, char2_nu))
        return result

    def _sim_stroke(self, char1: str, char2: str):
        """计算两汉字相似度, 通过两个字拆字的(相同元素/所有元素)
        calculate similarity of two chars, by char count of stroke
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.75
        """
        char1_st = self.dict_char_stroke.get(char1, [])
        char2_st = self.dict_char_stroke.get(char2, [])
        result = 0
        if char1_st and char2_st:
            count_and = len(set(char1_st) & set(char2_st))
            count_union = len(set(char1_st) | set(char2_st))
            result = count_and / count_union
        return result

    def _sim_struct(self, char1: str, char2: str):
        """计算两汉字相似度, 通过两个字构造结构
        calculate similarity of two chars, by char struct
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: int, 0 or 1, eg. 1
        """
        char1_st = self.dict_char_struct.get(char1, "")
        char2_st = self.dict_char_struct.get(char2, "")
        result = 0
        if char1_st and char2_st and char1_st == char2_st:
            result = 1
        return result

    def _sim_order(self, char1: str, char2: str):
        """计算两汉字相似度, 通过两个字笔顺(相同元素/所有元素)
        calculate similarity of two chars, by char struct
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.6
        """
        char1_or = self.dict_char_order.get(char1, "")
        char2_or = self.dict_char_order.get(char2, "")
        result = 0
        if char1_or and char2_or:
            count_and = len(set(list(char1_or)) & set(list(char2_or)))
            count_union = len(set(list(char1_or)) | set(list(char2_or)))
            result = count_and / count_union
        return result

    def _sim_w2v(self, char1: str, char2: str) -> float:
        """计算两汉字相似度, 通过词向量
        calculate similarity of two chars, by char struct
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.6
        """
        import xiangsi as xs

        return xs.cossim(char1, char2)

    def _run_shape_similarity(self, char1: str, char2: str):
        """计算两汉字相似度(字形重点)
        calculate similarity of two chars, by char shape
        rate(text-char-similar): 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate(nlp-hanzi-similar): 造字结构 10 四角编码 8 拆字 6 偏旁部首 6 笔画数 2  拼音 1
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.6
        """
        weights = {
            "fourangle": 7,
            "component": 2,
            "frequency": 5,
            "number": 6,
            "stroke": 4,
            "struct": 8,
            "order": 3,
        }

        scores = {
            "fourangle": self._sim_fourangle(char1, char2),
            "component": self._sim_component(char1, char2),
            "frequency": self._sim_frequency(char1, char2),
            "number": self._sim_number(char1, char2),
            "stroke": self._sim_stroke(char1, char2),
            "struct": self._sim_struct(char1, char2),
            "order": self._sim_order(char1, char2),
        }

        numerator = sum(scores[k] * weights[k] for k in scores)
        denominator = sum(weights.values())

        return numerator, denominator

    def _sim_by_shape(self, numerator: Union[float, int], denominator: Union[float, int]) -> float:
        return numerator / denominator

    def _sim_by_pinyin(
        self, char1: str, char2: str, numerator: Union[float, int], denominator: Union[float, int], rate_pinyin=35
    ) -> float:
        """计算两汉字相似度(拼音重点)
        calculate similarity of two chars, by char shape
        rate(text-char-similar): 拼音 35 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate(nlp-hanzi-similar): 造字结构 10 四角编码 8 拆字 6 偏旁部首 6 笔画数 2  拼音 1
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.6
        """
        score = self._sim_pinyin(char1, char2)
        return (numerator + score * rate_pinyin) / (denominator + rate_pinyin)

    def _sim_by_w2v(
        self, char1: str, char2: str, numerator: Union[float, int], denominator: Union[float, int], rate_w2v: int = 35
    ) -> float:
        """计算两汉字相似度(字形重点)
        calculate similarity of two chars, by char shape
        rate(text-char-similar): 字义 35 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate(nlp-hanzi-similar): 造字结构 10 四角编码 8 拆字 6 偏旁部首 6 笔画数 2  拼音 1
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
        Returns:
            result: float, 0-1, eg. 0.6
        """
        score = self._sim_w2v(char1, char2)
        return (numerator + score * rate_w2v) / (denominator + rate_w2v)

    def _sim_by_all(
        self,
        char1: str,
        char2: str,
        numerator: Union[float, int],
        denominator: Union[float, int],
        rate_pinyin: int = 35,
        rate_w2v: int = 35,
    ) -> float:
        """计算两汉字相似度(字形-拼音-语义)
        calculate similarity of two chars, by char shape
        rate-shape(text-char-similar): 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate-pinyin(text-char-similar): 拼音 35 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate-w2v(text-char-similar): 字义 35 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate-all(text-char-similar): 字义 35 拼音 35 造字结构 8 四角编码 7 笔画数 6 字频log10 5 拆字集合 4 笔画集合 3 偏旁部首 2
        rate(nlp-hanzi-similar): 造字结构 10 四角编码 8 拆字 6 偏旁部首 6 笔画数 2  拼音 1
        Args:
            char1: string, eg. "一"
            char2: string, eg. "而"
            rounded： int, eg. 4
            kind: string, eg. "shape" or "pinyin" or "w2v" or "all"
        Returns:
            result: float, 0-1, eg. 0.6
        """
        score_pinyin = self._sim_pinyin(char1, char2)
        score_w2v = self._sim_w2v(char1, char2)
        new_numerator = numerator + score_pinyin * rate_pinyin + score_w2v * rate_w2v
        new_denominator = denominator + rate_pinyin + rate_w2v
        return new_numerator / new_denominator

    def std_cal_sim(self, char1: str, char2: str, rounded: Optional[int] = None, kind: str = "shape") -> float:
        numerator, denominator = self._run_shape_similarity(char1, char2)
        if kind.upper() == "PINYIN":
            result = self._sim_by_pinyin(char1, char2, numerator, denominator)
        elif kind.upper() == "W2V":
            result = self._sim_by_w2v(char1, char2, numerator, denominator)
        elif kind.upper() == "ALL":
            result = self._sim_by_all(char1, char2, numerator, denominator)
        else:
            result = self._sim_by_shape(numerator, denominator)

        if rounded:
            result = round(result, rounded)
        else:
            result = round(result, self.rounded)
        return result


__all__ = ["CharSimilarity"]

if __name__ == "__main__":
    import time

    sim = CharSimilarity()
    char1 = "我"
    char2 = "他"
    for kind in ["shape", "pinyin", "w2v", "all"]:
        t0 = time.time()
        score = sim.std_cal_sim(char1, char2, kind=kind)
        print(f"相似度({char1}, {char2})[{kind}]: {score}, 用时: {time.time() - t0}s")
