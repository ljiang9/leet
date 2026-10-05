#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leet - leet-speak 编码/解码器。

把普通英文转成"黑客文"(leet-speak),也支持反向解码回来。
纯标准库,无第三方依赖。

设计取舍:
- level 1 只替换 9 个字母(a/b/e/g/i/o/s/t/z),且 l 保持不变。
  这是有意为之: `leet "hello world"` 必须输出经典的 `h3ll0 w0rld`,
  而不是 `h3110 w0r1d`。
- level 1 的目标符号互不相同,所以"纯字母输入"下
  decode(encode(x)) == x 精确可逆。
- 解码是"尽力而为"的: leet 符号可能和原文的数字/标点撞车
  (比如原文里的 `!` 和编码后的 i 都是 `!`),歧义见 README。
"""

import argparse
import random
import sys

# ---------------------------------------------------------------------------
# 映射表
# ---------------------------------------------------------------------------

# level 1: 经典数字替换。
LEVEL1 = {
    "a": "4",
    "b": "8",
    "e": "3",
    "g": "9",
    "i": "1",
    "o": "0",
    "s": "5",
    "t": "7",
    "z": "2",
}

# level 2: 符号风。全字母覆盖,含多字符符号(如 u -> |_|)。
LEVEL2 = {
    "a": "@", "b": "8", "c": "(", "d": "|)", "e": "3", "f": "|=",
    "g": "9", "h": "|-|", "i": "1", "j": "_|", "k": "|<", "l": "£",
    "m": "|\\/|", "n": "|\\|", "o": "0", "p": "|*", "q": "(_,)",
    "r": "|2", "s": "5", "t": "7", "u": "|_|", "v": "√",
    "w": "\\/\\/", "x": "><", "y": "`/", "z": "2",
}

# level 3: 随机变体。每个字母 3 种写法,--seed 可复现。
# 变体字符串在全表范围内唯一,解码按最长匹配优先,是确定的。
LEVEL3 = {
    "a": ["4", "@", "/-\\"],
    "b": ["8", "|3", "ß"],
    "c": ["(", "<", "©"],
    "d": ["|)", "[)", "Ð"],
    "e": ["3", "€", "ë"],
    "f": ["|=", "ph", "ƒ"],
    "g": ["9", "6", "§"],
    "h": ["|-|", "#", "]-["],
    "i": ["1", "!", "¦"],
    "j": ["_|", "_/", "¿"],
    "k": ["|<", "|{", "‡"],
    "l": ["£", "¬", "[_]"],
    "m": ["|\\/|", "/\\/\\", "^^"],
    "n": ["|\\|", "<\\>", "^/"],
    "o": ["0", "()", "[]"],
    "p": ["|*", "|o", "|°"],
    "q": ["(_,)", "(,)", "0,"],
    "r": ["|2", "/2", "®"],
    "s": ["5", "$", "~"],
    "t": ["7", "+", "†"],
    "u": ["|_|", "(_)", "µ"],
    "v": ["\\/", "|/", "√"],
    "w": ["ω", "vv", "\\^/"],
    "x": ["><", "}{", "×"],
    "y": ["`/", "¥", "//"],
    "z": ["2", "~/_", "%"],
}

LEVELS = {1: LEVEL1, 2: LEVEL2, 3: LEVEL3}


# ---------------------------------------------------------------------------
# 编解码
# ---------------------------------------------------------------------------

def _reverse_map(table):
    """符号 -> 字母 的反向表。level 3 会把每个变体都登记上。"""
    rev = {}
    for letter, glyph in table.items():
        glyphs = glyph if isinstance(glyph, list) else [glyph]
        for g in glyphs:
            rev[g] = letter
    return rev


def encode(text, level=1, seed=None):
    """把文本编码成 leet-speak。

    字母大小写不敏感(统一按小写映射);不在映射表里的字符原样保留。
    level 3 每次从变体里随机挑一个,传 seed 可复现。
    """
    table = LEVELS[level]
    rng = random.Random(seed)
    out = []
    for ch in text:
        key = ch.lower()
        if key in table:
            glyph = table[key]
            if isinstance(glyph, list):
                glyph = rng.choice(glyph)
            out.append(glyph)
        else:
            out.append(ch)
    return "".join(out)


def decode(text, level=1):
    """把 leet-speak 解回普通英文(尽力而为,歧义见 README)。

    按符号长度从长到短做最长匹配;匹配不上的字符原样保留。
    输出统一为小写(大小写信息在编码时已丢失)。
    """
    rev = _reverse_map(LEVELS[level])
    glyphs = sorted(rev, key=len, reverse=True)
    out = []
    i = 0
    while i < len(text):
        for g in glyphs:
            if text.startswith(g, i):
                out.append(rev[g])
                i += len(g)
                break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def print_table(level):
    """返回当前等级的映射表文本。"""
    table = LEVELS[level]
    rows = []
    for letter in sorted(table):
        g = table[letter]
        g = "/".join(g) if isinstance(g, list) else g
        rows.append("  %s -> %s" % (letter, g))
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="leet-speak 编码/解码器: 把英文转成黑客文,也能解回来。",
    )
    parser.add_argument("text", nargs="?", help="要转换的文本;省略则从 stdin 读取")
    parser.add_argument("--level", type=int, choices=(1, 2, 3), default=1,
                        help="leet 等级: 1=经典数字替换, 2=符号风, 3=随机变体 (默认: 1)")
    parser.add_argument("--decode", action="store_true", help="反向解码")
    parser.add_argument("--seed", type=int, default=None,
                        help="level 3 随机种子,相同种子输出相同")
    parser.add_argument("--table", action="store_true",
                        help="打印当前等级的映射表并退出")
    args = parser.parse_args(argv)

    if args.table:
        print(print_table(args.level))
        return 0

    if args.text is not None:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.error("请提供要转换的文本,或通过管道从 stdin 输入。")

    if args.decode:
        print(decode(text, args.level))
    else:
        print(encode(text, args.level, args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
