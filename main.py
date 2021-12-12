import asyncio
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path, PurePath
from typing import Iterable

from bilibili_api import video, Danmaku

from fetch_danmaku import fetch_danmaku
from process_danmaku import process_danmaku

args: Namespace


def get_args():
    parser = ArgumentParser()
    parser.add_argument("danmaku_source", type=str, nargs='*',
                        help="Input Danmaku source. "
                             "Possible options are BV numbers and file names (only XML is supported)")
    parser.add_argument("-k", "--keyword", dest="keyword_file", type=str, default="keywords.txt",
                        help="Specify a file which contains keywords. "
                             "Danmakus containing a keyword will have increased weight.")
    parser.add_argument("-f", "--file", type=str,
                        help="Specify a file from which the program will read BV numbers.")
    parser.add_argument("-i", "--interval_length", type=int, default=5,
                        help="Minimum length of the time interval. Used to avoid scattered time intervals. "
                             "Default to 5.")
    parser.add_argument("-m", "--peak-multiplier", dest="multiplier", type=float, default=6,
                        help="Only select time intervals with danmaku count x times more than the average. "
                             "Higher means less intervals found. Default to 6. ")
    return parser.parse_args()


def find_all_xml_files() -> list[PurePath]:
    # find all .xml files in current directory; ignoring hidden folders
    return [path.relative_to('.') for path in Path('.').rglob('*.xml')
            if str(path)[0] != '.']


keywords: list[tuple[str, int]] = []


def check_keyword(text: str) -> int:
    weight = 1
    for keyword in keywords:
        if text.find(keyword[0]) >= 0:
            weight += keyword[1]
    return weight


def print_danmaku(danmaku_list: list[Danmaku]):
    print("\n".join([f"{danmaku.dm_time} {danmaku.text}" for danmaku in danmaku_list]))


async def process_video(source: str):
    if source.find('BV') == 0:
        bv = True
        v = video.Video(bvid=source)
        info_task = v.get_info()
    else:
        bv = False
        v = source
    danmaku_list: list[Danmaku] = await fetch_danmaku(v)
    result = process_danmaku(danmaku_list, args.interval_length, args.multiplier, check_keyword)
    video_info = await info_task if bv else {'title': 'unknown'}
    print(f"Title: {video_info['title']}. Source: {source}.\n{result}")


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
    result = result.union(set(args.danmaku_source))
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
