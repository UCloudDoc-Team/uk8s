#!/usr/bin/env python3
"""
fix_style.py — 自动修正中文技术文档的机械性排版问题

修正范围(规则 2 + 规则 4):
  1. 纯数字与中文之间去掉空格(2 个→2个、1.30 以上→1.30以上)
  2. 含中文的句子里半角标点改全角(,→,  .→。 :→: ;→; !→! ?→?)

这两类是**纯机械替换**,不涉及语义判断,适合脚本一次性处理。
规则 1(中英空格)、规则 3(术语大小写)、规则 5(语义/错字)仍需人工逐条审查。

边界保护:会整块跳过围栏代码块(``` ... ```)、行内代码、URL、Markdown 链接目标,
避免误伤代码/命令/链接。YAML 代码块内的中文注释标点也会改(因为注释属于自然语言)。

用法:
  python3 fix_style.py FILE.md [FILE2.md ...]

会直接覆盖原文件,建议先提交 git 或留备份。
"""

import re
import sys

CJK = r"一-鿿㐀-䶿"

# 纯数字词元(不含字母),用于规则 2
NUM = r"[0-9]+(?:\.[0-9]+)?%?"
NOT_WORD_BEFORE = r"(?<![0-9A-Za-z.])"
NOT_WORD_AFTER = r"(?![0-9A-Za-z.])"

# 半角→全角映射(规则 4)
HALF_TO_FULL = {
    ",": "，", ".": "。", ":": "：", ";": "；",
    "!": "!", "?": "?",
    # 括号暂不自动改——需判断括号内是否全英文/代码
}


def fix_line(line: str, in_fence: bool) -> str:
    """修正一行文本。in_fence=True 时整行跳过。"""
    if in_fence:
        return line

    # 1. 把不可改区(行内代码/链接目标/URL)换成占位,记住原文
    chunks = []
    placeholders = []

    def save_chunk(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"\x00{idx}\x00"

    # 行内代码 `...`
    line = re.sub(r"`[^`]*`", save_chunk, line)
    # Markdown 链接目标 ](...)
    line = re.sub(r"\]\([^)]*\)", save_chunk, line)
    # 裸 URL
    line = re.sub(r"https?://\S+", save_chunk, line)

    # 2. 规则 2:纯数字 + 空格 + 中文 → 删空格
    line = re.sub(rf"{NOT_WORD_BEFORE}({NUM})\s+(?=[{CJK}])", r"\1", line)
    # 中文 + 空格 + 纯数字 → 删空格
    line = re.sub(rf"(?<=[{CJK}])\s+({NUM}){NOT_WORD_AFTER}", r"\1", line)

    # 3. 规则 4:含中文的句子里半角标点→全角
    # 逗号/分号/冒号/感叹号/问号:任一侧是汉字即改
    for half, full in HALF_TO_FULL.items():
        # 前后任一侧紧挨汉字
        line = re.sub(rf"(?<=[{CJK}]){re.escape(half)}", full, line)
        line = re.sub(rf"{re.escape(half)}(?=[{CJK}])", full, line)
    # 句号单独处理:只在前面是汉字时改(避开 1.19、file.md)
    line = re.sub(rf"(?<=[{CJK}])\.", "。", line)

    # 全角标点自带间距,收掉紧邻的半角空格(如 "超时： 检查" → "超时:检查")
    line = re.sub(r" *([，。：；!?]) *", r"\1", line)

    # 4. 还原占位
    for idx, chunk in enumerate(placeholders):
        line = line.replace(f"\x00{idx}\x00", chunk)

    return line


def fix_file(path: str) -> int:
    """修正一个文件,返回改动行数。"""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"错误:无法读取 {path}: {e}", file=sys.stderr)
        return 0

    new_lines = []
    in_fence = False
    changed = 0

    for raw in lines:
        stripped = raw.rstrip("\n")
        if re.match(r"\s*```", stripped):
            in_fence = not in_fence
            new_lines.append(raw)
            continue

        fixed = fix_line(stripped, in_fence)
        if fixed != stripped:
            changed += 1
        new_lines.append(fixed + "\n" if raw.endswith("\n") else fixed)

    if changed:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except OSError as e:
            print(f"错误:无法写入 {path}: {e}", file=sys.stderr)
            return 0

    return changed


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2

    total_files = 0
    total_changed = 0
    for path in argv[1:]:
        changed = fix_file(path)
        if changed:
            print(f"✓ {path} — {changed} 行已修正")
            total_changed += changed
            total_files += 1
        else:
            print(f"  {path} — 无需改动")

    if total_changed:
        print(f"\n共修正 {total_files} 个文件,{total_changed} 行。"
              f"建议再跑 check_style.py 验证一遍。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
