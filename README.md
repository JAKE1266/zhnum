# zhnum

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-29%20passing-success)
![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

零依赖的中文数字转换库 —— 整数 ↔ 中文小写 / 大写 / 人民币金额双向转换。

- **读法规范**：10~19 读「十」「十一」而非「一十」；中间零合并（100000001 → 一亿零一）
- **票据规范**：大写金额保留「壹拾贰元」（而非「拾贰元」），小写金额仍读「十二元」
- **金额细节**：Decimal 四舍五入到分（2.675 → 贰元陆角捌分）；拒绝 NaN、Infinity 与非法输入
- **解析宽容**：`from_cn` 同时接受简体、大写（壹贰叁）与「两」
- **范围**：0 ~ 万亿亿以内（< 10^16），「万亿」完整往返，负数支持「负」前缀

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
- **解析器与生成器对称**：所有生成输出都能被 `from_cn` 精确还原（随机 300 例覆盖至 < 10^16）
- **UTF-8 CLI**：Windows 默认编码下也稳定输出中文帮助、转换结果与错误信息

## 运行测试

```bash
python -m unittest discover -s tests
# Ran 29 tests ... OK
```

CI 会构建 wheel/sdist 并运行 `twine check`，再从仓库外目录安装真实 wheel，执行入口冒烟与全部测试；覆盖 Ubuntu/Windows/macOS × Python 3.8/3.9/3.11/3.13，共 13 个作业。

## 项目结构

```
zhnum/
├── LICENSE
├── CHANGELOG.md
├── MANIFEST.in
├── zhnum/
├── tests/
│   ├── smoke_installed.py
│   ├── test_cli.py
│   └── test_zhnum.py
├── .github/workflows/ci.yml
├── pyproject.toml
└── README.md
```

## License

MIT
