"""运行 UI 自动化用例并生成 Allure 报告。"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
ALLURE_RESULTS = REPORT_DIR / "allure-results"
ALLURE_REPORT = REPORT_DIR / "allure-report"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行测试并生成 Allure 报告")
    parser.add_argument("paths", nargs="*", help="指定用例路径，默认跑 tests/")
    parser.add_argument("-m", "--marker", default="", help="pytest marker，如 smoke")
    parser.add_argument("-k", "--keyword", default="", help="按用例名关键字过滤")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式运行（覆盖 .env 中的 HEADLESS）",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="有界面模式运行（覆盖 .env 中的 HEADLESS）",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="结束后不自动打开报告",
    )
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"--alluredir={ALLURE_RESULTS}",
        "--clean-alluredir",
    ]
    if args.marker:
        cmd.extend(["-m", args.marker])
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    if args.paths:
        cmd.extend(args.paths)
    return cmd


def generate_allure_report() -> subprocess.CompletedProcess[str]:
    allure_bin = shutil.which("allure")
    if not allure_bin:
        raise FileNotFoundError("未找到 allure 命令，请确认 Allure 已安装并加入 PATH")

    cmd = [
        allure_bin,
        "generate",
        str(ALLURE_RESULTS),
        "-o",
        str(ALLURE_REPORT),
        "--clean",
    ]
    print("生成报告:", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, check=False)


def has_allure_results() -> bool:
    return ALLURE_RESULTS.exists() and any(ALLURE_RESULTS.iterdir())


def main() -> int:
    args = parse_args()
    if args.headless and args.headed:
        print("不能同时指定 --headless 和 --headed")
        return 2

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if args.headless:
        env["HEADLESS"] = "true"
    elif args.headed:
        env["HEADLESS"] = "false"

    cmd = build_command(args)
    print("执行:", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT, env=env)

    if not has_allure_results():
        print("未生成 Allure 结果，请检查 allure-pytest 是否已安装。")
        return result.returncode

    gen = generate_allure_report()
    if gen.returncode != 0:
        print("Allure 报告生成失败，请确认本机已安装 Allure CLI。")
        return gen.returncode or 1

    index = ALLURE_REPORT / "index.html"
    print(f"Allure 报告: {index}")
    if not args.no_open and index.exists():
        #webbrowser.open(index.resolve().as_uri())
        subprocess.Popen(
        [ shutil.which("allure"),
         "open",
        str(ALLURE_REPORT)
    ], shell=True)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
