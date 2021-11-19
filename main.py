# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
from argparse import ArgumentParser
from pathlib import Path, PurePath
from typing import Union

import requests
from bilibili_api import video, Danmaku, sync

from process_danmaku import process_xml

args = {}


def get_args():
    parser = ArgumentParser()
    parser.add_argument("bv_number", type=str, nargs='*')
    parser.add_argument("-f", "--find", action="store_true")
    parser.add_argument("-i", "--interval_length", type=int, default=5)
    return parser.parse_args()


def find_all_xml_files() -> list[PurePath]:
    return [path.relative_to('.') for path in Path('.').rglob('*.xml') if str(path)[0] != '.']


keywords: list[tuple[str, int]] = []


def check_keyword(text: str) -> int:
    weight = 1
    for keyword in keywords:
        if text.find(keyword[0]) >= 0:
            weight += keyword[1]
    return weight


def print_danmaku(danmaku_list: list[Danmaku]):
    print("\n".join([f"{danmaku.dm_time} {danmaku.text}" for danmaku in danmaku_list]))


def process_video(bv: str, ):
    v = video.Video(bvid=bv)
    danmaku_list: list[Danmaku] = asyncio.run(v.get_danmakus(0))
    result = process_xml(danmaku_list, args.interval_length, 5, check_keyword)
    print(result)


def fill_keywords():
    f = open("keywords.txt", "r")
    while f.readable():
        line = f.readline()
        if len(line) <= 1:
            break
        line = line.split(",")
        keyword = line[0]
        weight = int(line[1])
        keywords.append((keyword, weight))


def main():
    global args
    args = get_args()
    fill_keywords()
    videos: list[Union[str, PurePath]] = [bv for bv in args.bv_number]
    for bv in videos:
        process_video(bv)


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
