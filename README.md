# zhnum

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-17%20passing-success)
![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

零依赖的中文数字转换库 —— 整数 ↔ 中文小写 / 大写 / 人民币金额双向转换。

- **读法规范**：10~19 读「十」「十一」而非「一十」；中间零合并（100000001 → 一亿零一）
- **票据规范**：大写金额保留「壹拾贰元」（而非「拾贰元」），小写金额仍读「十二元」
- **金额细节**：角分全零加「整」；只有分时补「零X分」（12.05 → 壹拾贰元零伍分）
- **解析宽容**：`from_cn` 同时接受简体、大写（壹贰叁）与「两」
- **范围**：0 ~ 万亿亿（10^16 量级），负数支持「负」前缀

零第三方依赖，Python ≥ 3.8。

## 安装

```bash
pip install .
```

## 真实运行示例

```console
$ python -m zhnum to-cn 123456789
一亿二千三百四十五万六千七百八十九

$ python -m zhnum to-capital 1024
壹仟零贰拾肆

$ python -m zhnum amount 1234.56
壹仟贰佰叁拾肆元伍角陆分

$ python -m zhnum amount 100000000.88
壹亿元捌角捌分

$ python -m zhnum from-cn "一亿二千三百四十五万六千七百八十九"
123456789
```

## 作为库使用

```python
from zhnum import from_cn, to_amount, to_cn, to_cn_capital

to_cn(20500)          # '二万零五百'
to_cn_capital(15)     # '拾伍'
to_amount(12.05)      # '壹拾贰元零伍分'
to_amount(12.3, capital=False)   # '十二元叁角整'
from_cn("两千零三")   # 2003
from_cn("壹亿零一")   # 100000001
```

## 设计取舍

- **四位分节**：整数按万进制切成 0~9999 的节，节内处理千/百/十/零，节间处理「亿 / 万」与跨节补零
- **前导「一十」省略规则参数化**：读数时省略（十五、十一），票据金额不省略（壹拾贰元）——同一套算法两个开关
- **解析器与生成器对称**：所有生成输出都能被 `from_cn` 精确还原（随机 300 例往返测试覆盖）

## 运行测试

```bash
python -m unittest discover -s tests
# Ran 17 tests ... OK
```


## 📁 项目结构

```
zhnum/
├── LICENSE
├── pyproject.toml
├── tests/
├── zhnum/
└── README.md
```

## License

MIT
