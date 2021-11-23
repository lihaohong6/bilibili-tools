# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import json
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path, PurePath
from typing import Union, Any, Iterable

import requests
from bilibili_api import video, Danmaku, sync

from process_danmaku import process_danmaku

args: Namespace


def get_args():
    parser = ArgumentParser()
    parser.add_argument("bv_number", type=str, nargs='*')
    parser.add_argument("-k", "--keyword", dest="keyword_file", type=str, default="keywords.txt")
    parser.add_argument("-f", "--file", type=str)
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


danmaku_attributes = ['dm_time', 'text']


def danmaku_to_dict(danmaku: Danmaku) -> dict[str, Any]:
    result = {}
    for attr in danmaku_attributes:
        result[attr] = getattr(danmaku, attr)
    return result


def danmaku_list_to_json(danmaku_list: list[Danmaku]) -> str:
    return json.dumps([danmaku_to_dict(d) for d in danmaku_list])


def json_to_danmaku_list(data: str) -> list[Danmaku]:
    dict_list = json.loads(data)
    result = []
    for d in dict_list:
        danmaku = Danmaku("")
        for attr in danmaku_attributes:
            setattr(danmaku, attr, d[attr])
        result.append(danmaku)
    return result


async def fetch_danmaku(v: video.Video) -> list[Danmaku]:
    bv = v.get_bvid()
    file_path = Path(f"cache/{bv}.json")
    if file_path.exists():
        data = open(file_path, 'r').read()
        danmaku_list = json_to_danmaku_list(data)
    else:
        danmaku_list: list[Danmaku] = await v.get_danmakus(0)
        file = open(file_path, 'w')
        file.write(danmaku_list_to_json(danmaku_list))
        file.close()
    return danmaku_list


async def process_video(bv: str):
    v = video.Video(bvid=bv)
    info_task = v.get_info()
    danmaku_list: list[Danmaku] = await fetch_danmaku(v)
    result = process_danmaku(danmaku_list, args.interval_length, 5, check_keyword)
    video_info = await info_task
    print(f"Title: {video_info['title']}. Source: {bv}.\n{result}")


def fill_keywords():
    f = open(args.keyword_file, "r")
    while f.readable():
        line = f.readline()
        if len(line) <= 1:
            break
        line = line.split(",")
        keyword = line[0]
        weight = int(line[1])
        keywords.append((keyword, weight))


def get_videos() -> set[str]:
    result = set()
    if args.file is not None:
        f = open(args.file, 'r')
        bvs = re.split('[,; \n\t\r\v\f]+', f.read())
        result = set([bv for bv in bvs if len(bv) > 5])
    result = result.union(set(args.bv_number))
    return result


async def main():
    global args
    Path("cache").mkdir(exist_ok=True)
    args = get_args()
    fill_keywords()
    videos: Iterable[str] = get_videos()
    tasks = []
    for bv in videos:
        tasks.append(asyncio.create_task(process_video(bv)))
    for task in tasks:
        await task


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
