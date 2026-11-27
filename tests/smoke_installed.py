import os
import subprocess
import sys
import sysconfig
import tempfile
from importlib import metadata
from pathlib import Path

import zhnum


def main() -> None:
    dist = metadata.distribution("zhnum")
    assert dist.metadata["Name"] == "zhnum"
    assert dist.version == "0.1.1"
    assert zhnum.__version__ == "0.1.1"
    assert dist.metadata["Requires-Python"] == ">=3.8"
    assert not dist.requires

    source_root = Path(__file__).resolve().parent.parent
    module_path = Path(zhnum.__file__).resolve()
    assert source_root not in module_path.parents, module_path

    assert zhnum.from_cn(zhnum.to_cn(10 ** 12 + 1)) == 10 ** 12 + 1
    assert zhnum.from_cn(zhnum.to_cn_capital(10 ** 16 - 1)) == 10 ** 16 - 1
    assert zhnum.to_amount("2.675") == "贰元陆角捌分"
    try:
        zhnum.to_amount("inf")
    except zhnum.ZhNumError:
        pass
    else:
        raise AssertionError("non-finite amount was accepted")

    executable = Path(sysconfig.get_path("scripts")) / (
        "zhnum.exe" if os.name == "nt" else "zhnum"
    )
    assert executable.is_file(), executable

    env = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
    with tempfile.TemporaryDirectory() as workdir:
        result = subprocess.run(
            [sys.executable, "-m", "zhnum", "to-cn", "123"],
            capture_output=True, cwd=workdir, env=env, check=True,
        )
        assert result.stdout.decode("utf-8").splitlines() == ["一百二十三"]
        assert result.stderr == b""

        console = subprocess.run(
            [str(executable), "amount", "2.675"],
            capture_output=True, cwd=workdir, env=env, check=True,
        )
        assert console.stdout.decode("utf-8").splitlines() == ["贰元陆角捌分"]
        assert console.stderr == b""

        invalid = subprocess.run(
            [str(executable), "amount", "inf"],
            capture_output=True, cwd=workdir, env=env,
        )
        assert invalid.returncode == 1
        assert invalid.stdout == b""
        stderr = invalid.stderr.decode("utf-8")
        assert "金额必须为有限数字" in stderr
        assert "Traceback" not in stderr

    print("installed zhnum 0.1.1 smoke: OK")


if __name__ == "__main__":
    main()
