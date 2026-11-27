"""中文数字 ↔ 阿拉伯数字双向转换，以及人民币大写金额。

约定：
- 整数按「万进制四位一组」处理（个、万、亿、万亿）
- 10~19 读作「十」「十一」…而非「一十」（各节内一致，含「十五万」）
- 中间的零合并为一个「零」（如 100000001 → 一亿零一）
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext

_DIGITS_CN = "零一二三四五六七八九"
_DIGITS_CAP = "零壹贰叁肆伍陆柒捌玖"
_UNITS = ("", "十", "百", "千")
_UNITS_CAP = ("", "拾", "佰", "仟")
_SECTIONS = ("", "万", "亿", "万亿")

# 解析用映射（小写 + 大写 + 「两」都接受）
_CHAR_DIGIT = {}
for i, ch in enumerate(_DIGITS_CN):
    _CHAR_DIGIT[ch] = i
for i, ch in enumerate(_DIGITS_CAP):
    _CHAR_DIGIT[ch] = i
_CHAR_DIGIT["两"] = 2
_CHAR_UNIT = {"十": 10, "百": 100, "千": 1000,
              "拾": 10, "佰": 100, "仟": 1000}
_CHAR_SECTION = {"万": 10 ** 4, "亿": 10 ** 8}


class ZhNumError(ValueError):
    """无法解析的中文数字。"""


# ---------- 数字 → 中文 ----------
def _section_to_cn(value: int, digits: str, units: tuple[str, ...],
                   omit_leading_one: bool = True) -> str:
    """0~9999 一节内转中文；``omit_leading_one`` 时前导「一十/壹拾」省略为「十/拾」。"""
    if value == 0:
        return ""
    out = []
    need_zero = False
    for pos in (3, 2, 1, 0):  # 千 百 十 个
        digit = value // 10 ** pos % 10
        if digit == 0:
            need_zero = bool(out)
            continue
        if need_zero:
            out.append(digits[0])
            need_zero = False
        out.append(digits[digit] + units[pos])
    s = "".join(out)
    if omit_leading_one and (s.startswith("一十") or s.startswith("壹拾")):
        s = s[1:]
    return s


def _to_int_cn(n: int, digits: str, units: tuple[str, ...],
               omit_leading_one: bool = True) -> str:
    if n == 0:
        return digits[0]
    sections: list[int] = []
    while n:
        sections.append(n % 10 ** 4)
        n //= 10 ** 4
    parts: list[str] = []
    for idx in range(len(sections) - 1, -1, -1):
        value = sections[idx]
        if value == 0:
            continue
        # 高位节之后，本节 < 千 时需补零（如 一亿零一）
        if parts and value < 1000:
            parts.append(digits[0])
        if idx >= len(_SECTIONS):
            raise ZhNumError("数字过大（超出万亿亿）")
        parts.append(_section_to_cn(value, digits, units, omit_leading_one)
                     + _SECTIONS[idx])
    return "".join(parts)


def to_cn(n: int) -> str:
    """整数 → 中文小写，支持 0 与负数。"""
    n = int(n)
    if n < 0:
        return "负" + to_cn(-n)
    return _to_int_cn(n, _DIGITS_CN, _UNITS)


def to_cn_capital(n: int) -> str:
    """整数 → 中文大写（壹贰叁…），一般用于票据。"""
    n = int(n)
    if n < 0:
        return "负" + to_cn_capital(-n)
    return _to_int_cn(n, _DIGITS_CAP, _UNITS_CAP)


def to_amount(amount, capital: bool = True) -> str:
    """人民币大写金额：支持 0.01~万亿。

    规则：角分全为零时末尾加「整」；角为零分不为零时读「零X分」。
    ``capital=False`` 返回小写（一二三…）版本。
    """
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ZhNumError(f"无效金额：{amount!r}") from None
    if not amount.is_finite():
        raise ZhNumError("金额必须为有限数字")
    with localcontext() as context:
        context.prec = max(28, amount.adjusted() + 3)
        try:
            amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except InvalidOperation:
            raise ZhNumError("金额超出可转换范围") from None
    if amount < 0:
        return "负" + to_amount(-amount, capital)
    yuan = int(amount)
    cents = int((amount - yuan) * 100)
    jiao, fen = divmod(cents, 10)

    # 大写金额保留「壹拾」写法（票据规范：壹拾贰元）；小写仍读「十二元」
    digits = _DIGITS_CAP if capital else _DIGITS_CN
    units = _UNITS_CAP if capital else _UNITS
    if yuan == 0:
        out = digits[0] + "元"
    else:
        out = _to_int_cn(yuan, digits, units, omit_leading_one=not capital) + "元"
    if jiao == 0 and fen == 0:
        return out + "整"
    if jiao > 0:
        out += digits[jiao] + units[0] + "角"
    elif fen > 0:
        out += digits[0]
    if fen > 0:
        out += digits[fen] + units[0] + "分"
    else:
        out += "整"
    return out


# ---------- 中文 → 数字 ----------
def from_cn(text: str) -> int:
    """中文数字（含大写与「两」）→ 整数。无法解析时抛 ZhNumError。"""
    s = str(text).strip()
    negative = s.startswith("负")
    if negative:
        s = s[1:]
    if not s:
        raise ZhNumError("空字符串不是有效的中文数字")
    if s == _DIGITS_CN[0] or s == _DIGITS_CAP[0]:
        return 0

    value = 0        # 已完成的节累计
    section = 0      # 当前节内累计
    digit = -1       # 最近读到的数字（-1 表示尚未读数）
    i = 0
    while i < len(s):
        # 「万亿」必须先作为一个单位，避免被拆成「万」和「亿」。
        if s.startswith("万亿", i):
            value += (section + (digit if digit > 0 else 0)) * 10 ** 12
            section, digit = 0, -1
            i += 2
            continue
        ch = s[i]
        if ch in _CHAR_DIGIT:
            digit = _CHAR_DIGIT[ch]
        elif ch in _CHAR_UNIT:
            # 「十」前无数 → 视为 1（如「十五」）
            section += (digit if digit > 0 else 1) * _CHAR_UNIT[ch]
            digit = -1
        elif ch in _CHAR_SECTION:
            value += (section + (digit if digit > 0 else 0)) * _CHAR_SECTION[ch]
            section, digit = 0, -1
        else:
            raise ZhNumError(f"无法识别的字符 {ch!r}（原文：{text!r}）")
        i += 1
    total = value + section + (digit if digit > 0 else 0)
    if not negative and total == 0 and any(c in _CHAR_UNIT or c in _CHAR_SECTION for c in s):
        pass  # 「零」之外的全零串按 0 处理
    return -total if negative else total
