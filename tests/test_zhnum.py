import unittest
from decimal import Decimal, localcontext

from zhnum.core import ZhNumError, from_cn, to_amount, to_cn, to_cn_capital


class TestToCn(unittest.TestCase):
    def test_small(self):
        cases = {0: "零", 5: "五", 10: "十", 11: "十一", 15: "十五", 20: "二十",
                 99: "九十九", 100: "一百", 101: "一百零一", 110: "一百一十",
                 205: "二百零五", 999: "九百九十九"}
        for n, want in cases.items():
            self.assertEqual(to_cn(n), want, n)

    def test_thousands_and_zeros(self):
        cases = {1000: "一千", 1005: "一千零五", 1010: "一千零一十", 1500: "一千五百",
                 20500: "二万零五百", 100000: "十万", 1000000: "一百万",
                 100000001: "一亿零一", 100010001: "一亿零一万零一"}
        for n, want in cases.items():
            self.assertEqual(to_cn(n), want, n)

    def test_large(self):
        self.assertEqual(to_cn(123456789), "一亿二千三百四十五万六千七百八十九")
        self.assertEqual(to_cn(15), "十五")
        self.assertEqual(to_cn(150000), "十五万")
        self.assertEqual(to_cn(1100000000), "十一亿")

    def test_negative_and_roundtrip(self):
        self.assertEqual(to_cn(-42), "负四十二")
        for n in range(0, 20000, 7):
            self.assertEqual(from_cn(to_cn(n)), n, n)

    def test_trillion_roundtrip(self):
        self.assertEqual(to_cn(10 ** 12), "一万亿")
        self.assertEqual(from_cn("一万亿"), 10 ** 12)
        for n in (10 ** 12 - 1, 10 ** 12, 10 ** 12 + 1,
                  1234567890123456, 10 ** 16 - 1):
            with self.subTest(n=n):
                self.assertEqual(from_cn(to_cn(n)), n)


class TestCapital(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(to_cn_capital(15), "拾伍")
        self.assertEqual(to_cn_capital(1024), "壹仟零贰拾肆")
        self.assertEqual(to_cn_capital(0), "零")
        self.assertEqual(to_cn_capital(123456789), "壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖")

    def test_roundtrip(self):
        for n in range(0, 10000, 13):
            self.assertEqual(from_cn(to_cn_capital(n)), n, n)

    def test_trillion_roundtrip(self):
        for n in (10 ** 12 - 1, 10 ** 12, 10 ** 12 + 1,
                  1234567890123456, 10 ** 16 - 1):
            with self.subTest(n=n):
                self.assertEqual(from_cn(to_cn_capital(n)), n)


class TestAmount(unittest.TestCase):
    def test_full(self):
        self.assertEqual(to_amount(1234.56), "壹仟贰佰叁拾肆元伍角陆分")

    def test_whole_yuan(self):
        self.assertEqual(to_amount(100), "壹佰元整")
        self.assertEqual(to_amount(100.00), "壹佰元整")

    def test_jiao_only(self):
        self.assertEqual(to_amount(12.3), "壹拾贰元叁角整")

    def test_fen_only(self):
        self.assertEqual(to_amount(12.05), "壹拾贰元零伍分")

    def test_lowercase(self):
        self.assertEqual(to_amount(12.05, capital=False), "十二元零五分")
        self.assertEqual(to_amount(100, capital=False), "一百元整")

    def test_negative(self):
        self.assertEqual(to_amount(-3.5), "负叁元伍角整")

    def test_decimal_half_up(self):
        cases = [(2.675, "贰元陆角捌分"), ("2.675", "贰元陆角捌分"),
                 (Decimal("1.005"), "壹元零壹分"), (-2.675, "负贰元陆角捌分")]
        for value, want in cases:
            with self.subTest(value=value):
                self.assertEqual(to_amount(value), want)

    def test_low_precision_context(self):
        with localcontext() as context:
            context.prec = 6
            self.assertEqual(to_amount("2.675"), "贰元陆角捌分")
            self.assertEqual(context.prec, 6)

    def test_nonfinite_amounts(self):
        for value in (float("inf"), float("-inf"), float("nan"), "NaN"):
            with self.subTest(value=value):
                with self.assertRaises(ZhNumError):
                    to_amount(value)

    def test_invalid_amounts(self):
        for value in ("abc", "", None):
            with self.subTest(value=value):
                with self.assertRaises(ZhNumError):
                    to_amount(value)


class TestFromCn(unittest.TestCase):
    def test_common(self):
        cases = {"零": 0, "五": 5, "十": 10, "十一": 11, "二十": 20, "一百零一": 101,
                 "两": 2, "两千零三": 2003, "二万零五百": 20500, "一亿零一": 100000001,
                 "十五万": 150000, "十一亿": 1100000000}
        for text, want in cases.items():
            self.assertEqual(from_cn(text), want, text)

    def test_capital_accepted(self):
        self.assertEqual(from_cn("壹仟零贰拾肆"), 1024)
        self.assertEqual(from_cn("壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖"), 123456789)

    def test_invalid(self):
        for bad in ["", "abc", "一二三five", "圆圈"]:
            with self.assertRaises(ZhNumError):
                from_cn(bad)

    def test_negative(self):
        self.assertEqual(from_cn("负四十二"), -42)


class TestRoundtrip(unittest.TestCase):
    def test_both_directions_random(self):
        import random
        random.seed(2026)
        for _ in range(300):
            n = random.randint(-(10 ** 16 - 1), 10 ** 16 - 1)
            self.assertEqual(from_cn(to_cn(n)), n, n)
            if n >= 0:
                self.assertEqual(from_cn(to_cn_capital(n)), n, n)


if __name__ == "__main__":
    unittest.main()
