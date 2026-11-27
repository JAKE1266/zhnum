import os
import subprocess
import sys
import unittest


PYTHON = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}


def run_cli(*args):
    return subprocess.run(
        [PYTHON, "-m", "zhnum", *args],
        capture_output=True,
        env=ENV,
    )


class TestCli(unittest.TestCase):
    def test_version_under_legacy_encoding(self):
        result = run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.rstrip(b"\r\n"), b"zhnum 0.1.1")
        self.assertEqual(result.stderr, b"")

    def test_help_under_legacy_encoding(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("中文数字转换工具", result.stdout.decode("utf-8"))

    def test_to_cn_under_legacy_encoding(self):
        result = run_cli("to-cn", "123")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.decode("utf-8").splitlines(), ["一百二十三"])
        self.assertEqual(result.stderr, b"")

    def test_amount_decimal_under_legacy_encoding(self):
        result = run_cli("amount", "2.675")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.decode("utf-8").splitlines(), ["贰元陆角捌分"])

    def test_from_cn_trillion_under_legacy_encoding(self):
        result = run_cli("from-cn", "一万亿")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.rstrip(b"\r\n"), b"1000000000000")

    def test_nonfinite_amount_under_legacy_encoding(self):
        result = run_cli("amount", "inf")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        stderr = result.stderr.decode("utf-8")
        self.assertIn("金额必须为有限数字", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_invalid_amount_under_legacy_encoding(self):
        result = run_cli("amount", "abc")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertIn("无效金额", result.stderr.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
