"""zhnum —— 中文数字转换库。"""
from .core import ZhNumError, from_cn, to_amount, to_cn, to_cn_capital

__version__ = "0.1.0"

__all__ = ["ZhNumError", "from_cn", "to_amount", "to_cn", "to_cn_capital", "__version__"]
