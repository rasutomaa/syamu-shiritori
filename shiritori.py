#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syamuあだ名しりとり
"""

import argparse
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

try:
    import pykakasi
except ImportError:
    print("pykakasi が必要です: pip install pykakasi", file=sys.stderr)
    sys.exit(1)

KAKASI = pykakasi.kakasi()


@dataclass
class Word:
    id: int
    text: str
    reading: str
    start: str
    end: str

    def __str__(self):
        return f"{self.id} {self.text} ({self.reading})"


def to_hiragana(text: str) -> str:
    """漢字・カタカナをひらがなに変換し、しりとり用に正規化する"""
    result = KAKASI.convert(text)
    hira = "".join(item["hira"] for item in result)

    # カタカナが残っていた場合の保険
    hira = hira.translate(
        str.maketrans(
            "ァィゥェォャュョッン",
            "ぁぃぅぇぉゃゅょっん",
        )
    )

    # 空白と長音「ー」を除去
    hira = hira.replace(" ", "").replace("　", "").replace("ー", "")
    return hira


def load_words(path: Path) -> List[Word]:
    """あだ名リストを読み込む"""
    words: List[Word] = []
    seen = set()

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            m = re.match(r"^(\d+)\s+(.+)$", line)
            if not m:
                continue

            id_ = int(m.group(1))
            text = m.group(2).strip()
            reading = to_hiragana(text)
            if not reading:
                continue

            key = (id_, text)
            if key in seen:
                continue
            seen.add(key)

            words.append(
                Word(
                    id=id_,
                    text=text,
                    reading=reading,
                    start=reading[0],
                    end=reading[-1],
                )
            )

    return words


def find_next_words(words: List[Word], last_end: str, used_ids: Set[int]) -> List[Word]:
    """最後の文字で始まる未使用のあだ名を探す"""
    return [w for w in words if w.start == last_end and w.id not in used_ids]


def auto_chain(words: List[Word], tries: int = 2000) -> List[Word]:
    """自動で長めのしりとりチェーンを生成する"""
    best: List[Word] = []

    for _ in range(tries):
        unused = {w.id for w in words}
        current = random.choice(words)
        chain = [current]
        unused.remove(current.id)
        last_end = current.end

        while True:
            candidates = [
                w for w in words if w.start == last_end and w.id in unused
            ]
            if not candidates:
                break

            def next_count(w: Word) -> int:
                return len(
                    [
                        x
                        for x in words
                        if x.start == w.end and x.id in unused and x.id != w.id
                    ]
                )

            candidates.sort(key=next_count)
            min_count = next_count(candidates[0])
            best_candidates = [
                w for w in candidates if next_count(w) == min_count
            ]
            nxt = random.choice(best_candidates)

            chain.append(nxt)
            unused.remove(nxt.id)
            last_end = nxt.end

        if len(chain) > len(best):
            best = chain

    return best


def validate_chain(chain: List[Word]) -> List[str]:
    """しりとりチェーンの検証"""
    errors = []
    used = set()

    for i, w in enumerate(chain):
        if w.id in used:
            errors.append(f"{i + 1}: ID {w.id} が重複しています")
        used.add(w.id)

        if i > 0:
            prev = chain[i - 1]
            if prev.end != w.start:
                errors.append(
                    f"{i + 1}: {prev.text} の末尾 '{prev.end}' と "
                    f"{w.text} の先頭 '{w.start}' が一致しません"
                )

    return errors


def play(words: List[Word]) -> None:
    """対話的にしりとりをする"""
    print("=== Syamuあだ名しりとり ===")
    print("最初のあだ名を入力してください。空Enterでランダム。")

    text_to_word = {w.text: w for w in words}
    used: Set[int] = set()
    last: Word | None = None

    while True:
        if last is None:
            user_input = input("最初のあだ名: ").strip()
            if not user_input:
                last = random.choice(words)
                print(f"ランダム選択: {last.id} {last.text}")
            else:
                if user_input not in text_to_word:
                    print("リストにありません。")
                    continue
                last = text_to_word[user_input]
                print(f"開始: {last.id} {last.text}")
            used.add(last.id)
        else:
            print(f"\n現在: {last.id} {last.text} (末尾: {last.end})")
            user_input = input("次のあだ名: ").strip()
            if not user_input:
                print("終了します。")
                break

            if user_input not in text_to_word:
                print("リストにありません。")
                continue

            nxt = text_to_word[user_input]
            if nxt.id in used:
                print("すでに使われています。")
                continue
            if nxt.start != last.end:
                print(f"先頭が '{last.end}' ではありません。")
                continue

            used.add(nxt.id)
            last = nxt
            print(f"あなた: {last.id} {last.text}")

        # コンピュータの番
        candidates = find_next_words(words, last.end, used)
        if not candidates:
            print("コンピュータは返せません。あなたの勝ち！")
            break

        comp = random.choice(candidates)
        used.add(comp.id)
        last = comp
        print(f"コンピュータ: {comp.id} {comp.text} (末尾: {comp.end})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Syamuあだ名しりとり")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/Syamuあだ名しりとり.txt"),
        help="あだ名リストのパス",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("play", help="対話的にしりとり")

    auto_p = sub.add_parser("auto", help="自動でしりとりチェーンを生成")
    auto_p.add_argument("--tries", type=int, default=2000, help="試行回数")

    val_p = sub.add_parser("validate", help="チェーンファイルを検証")
    val_p.add_argument("file", type=Path, help="検証するチェーンファイル（1行1あだ名）")

    args = parser.parse_args()

    if not args.data.exists():
        print(f"データファイルが見つかりません: {args.data}", file=sys.stderr)
        sys.exit(1)

    words = load_words(args.data)
    print(f"{len(words)} 件のあだ名を読み込みました。")

    if args.command == "play":
        play(words)

    elif args.command == "auto":
        chain = auto_chain(words, args.tries)
        print(f"チェーン長: {len(chain)}")
        for i, w in enumerate(chain, 1):
            print(f"{i} {w.id} {w.text}")

    elif args.command == "validate":
        lines = args.file.read_text(encoding="utf-8").splitlines()
        chain: List[Word] = []
        text_to_word = {w.text: w for w in words}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            m = re.match(r"^\d+\s+(.+)$", line)
            text = m.group(1) if m else line

            if text not in text_to_word:
                print(f"リストにない: {text}", file=sys.stderr)
                sys.exit(1)

            chain.append(text_to_word[text])

        errors = validate_chain(chain)
        if errors:
            print("検証エラー:")
            for e in errors:
                print(e)
            sys.exit(1)
        else:
            print("OK: 有効なしりとりチェーンです。")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
