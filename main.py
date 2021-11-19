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


keywords = []


def check_keyword(text: str) -> int:
    weight = 1
    for keyword in keywords:
        if text.find(keyword) >= 0:
            weight += 1
    return weight


def process_video(bv: str, ):
    v = video.Video(bvid=bv)
    danmaku_list: list[Danmaku] = asyncio.run(v.get_danmakus(0))
    print("\n".join([f"{danmaku.dm_time} {danmaku.text}" for danmaku in danmaku_list]))
    result = process_xml(danmaku_list, args.interval_length, 5, check_keyword)
    print(result)


def main():
    global args
    args = get_args()
    videos: list[Union[str, PurePath]] = [bv for bv in args.bv_number]
    for bv in videos:
        process_video(bv)


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
