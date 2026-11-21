"""支持 ``python -m zhnum`` 运行。"""
import argparse
import sys

from . import __version__, from_cn, to_amount, to_cn, to_cn_capital


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="zhnum", description="中文数字转换工具")
    ap.add_argument("--version", action="version", version=f"zhnum {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("to-cn", help="数字 → 中文小写")
    sp.add_argument("n", type=int)
    sp = sub.add_parser("to-capital", help="数字 → 中文大写")
    sp.add_argument("n", type=int)
    sp = sub.add_parser("amount", help="金额 → 人民币大写")
    sp.add_argument("x", type=float)
    sp = sub.add_parser("from-cn", help="中文 → 数字")
    sp.add_argument("text")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "to-cn":
            print(to_cn(args.n))
        elif args.cmd == "to-capital":
            print(to_cn_capital(args.n))
        elif args.cmd == "amount":
            print(to_amount(args.x))
        else:
            print(from_cn(args.text))
        return 0
    except (ValueError,) as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
