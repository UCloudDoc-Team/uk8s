#!/usr/bin/env python3
"""
check_style.py — 中文技术文档排版自检器(只报告，不改动)

用途:排版编辑完成后跑一遍,把两类"最容易被漏掉"的机械性问题扫出来,
供你逐条回看修正。它故意只做**提示**,不自动改——因为是否要改仍需人判断
(例如代码里的标点、版本号里的点号都不能动)。

它会自动跳过:
  - 围栏代码块(``` ... ```)整块
  - 行内代码(`...`)
  - Markdown 链接目标 ](...) 与裸 URL
这些区域内的内容一律不检查,避免误报到代码/链接上。

检查项:
  [NUM ] 数字与中文之间多了空格(规则 2:应无空格),如 "2 个""1.30 以上""80% 时"
  [PUNC] 含中文的句子里用了半角标点(规则 4:应全角),如 "节点,每个""示例:10Mbps""发现."

用法:
  python3 check_style.py FILE.md [FILE2.md ...]

退出码:发现问题返回 1,干净返回 0(方便在脚本里串联)。
"""

import re
import sys

CJK = r"一-鿿㐀-䶿"  # 常用+扩展A汉字

# 纯数字词元(如 2、1.30、80%)—— 不含字母,才适用规则 2「与中文之间无空格」。
# 关键:必须排除 base64 / 10Mbps / p95 / 10ms 这类"含字母的英文词元",
# 它们与中文之间反而**应当**有空格(规则 1),不能在这里误报。
NUM = r"[0-9]+(?:\.[0-9]+)?%?"                 # 纯数字:可带小数点、结尾百分号
NOT_WORD = r"(?<![0-9A-Za-z.])"               # 数字左边不能紧挨字母/数字/点(排除 base64 的 64)
# 纯数字 + 空格 + 汉字(应无空格)
RE_NUM_CJK = re.compile(rf"{NOT_WORD}{NUM}\s+(?=[{CJK}])")
# 汉字 + 空格 + 纯数字(其后不能再跟字母/数字/点,排除 10ms 这类)
RE_CJK_NUM = re.compile(rf"(?<=[{CJK}])\s+{NUM}(?![0-9A-Za-z.])")

# 半角标点,且相邻一侧是汉字——含中文的句子应改全角
# 逗号/分号/冒号/问号/感叹号:任一侧紧挨汉字即提示
RE_HALF_MARK = re.compile(rf"(?:(?<=[{CJK}])[,;:!?])|(?:[,;:!?](?=[{CJK}]))")
# 句号单独处理:只在前面是汉字时提示(避开 1.19、file.md、base64 -w0 等)
RE_HALF_DOT = re.compile(rf"(?<=[{CJK}])\.")


def strip_uncheckable(line: str) -> str:
    """把行内代码、链接目标、URL 换成等长占位,避免误报;保留列偏移。"""
    # 行内代码 `...`
    line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)
    # Markdown 链接目标 ](...)
    line = re.sub(r"\]\([^)]*\)", lambda m: " " * len(m.group(0)), line)
    # 裸 URL
    line = re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), line)
    return line


def check_file(path: str) -> list:
    findings = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        return [(0, "FILE", f"无法读取:{e}")]

    in_fence = False
    for i, raw in enumerate(lines, 1):
        stripped = raw.rstrip("\n")
        if re.match(r"\s*```", stripped):      # 围栏代码块起止
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        probe = strip_uncheckable(stripped)

        for m in RE_NUM_CJK.finditer(probe):
            ctx = stripped[max(0, m.start() - 4):m.end() + 4]
            findings.append((i, "NUM", f"数字后多空格 …{ctx}…"))
        for m in RE_CJK_NUM.finditer(probe):
            ctx = stripped[max(0, m.start() - 4):m.end() + 4]
            findings.append((i, "NUM", f"数字前多空格 …{ctx}…"))
        for m in RE_HALF_MARK.finditer(probe):
            ctx = stripped[max(0, m.start() - 4):m.end() + 4]
            findings.append((i, "PUNC", f"半角标点 '{m.group(0)}' …{ctx}…"))
        for m in RE_HALF_DOT.finditer(probe):
            ctx = stripped[max(0, m.start() - 4):m.end() + 4]
            findings.append((i, "PUNC", f"半角句号 '.' …{ctx}…"))

    return findings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    total = 0
    for path in argv[1:]:
        findings = check_file(path)
        if findings:
            print(f"\n=== {path} — {len(findings)} 处待查 ===")
            for line_no, kind, msg in findings:
                print(f"  L{line_no:<4} [{kind}] {msg}")
            total += len(findings)
        else:
            print(f"=== {path} — 干净,无机械性问题 ===")
    if total:
        print(f"\n共 {total} 处提示。逐条回看:确属正文中文的按规则改;"
              f"若落在代码/链接/版本号等边界上,保持不动即可。")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
