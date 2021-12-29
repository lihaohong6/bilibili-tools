import datetime
import json
import math
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from bilibili_api import sync

from config import CACHE_ROOT
from utils.fetch_data import fetch_dynamic

DEFAULT_WIDTH = 70


def make_multiline(text: str, width: int = DEFAULT_WIDTH) -> str:
    paragraphs = text.split('\n')
    result = []
    for index, paragraph in enumerate(paragraphs):
        line_count = math.ceil(len(paragraph) / width)
        for line_number in range(0, line_count):
            start = line_number * width
            end = min(start + width, len(paragraph))
            result.append(paragraph[start:end])
        if index != len(paragraphs) - 1:
            result.append("")
    return "\n".join(result)


def dict_to_text(original: dict, fields: list[Union[str, tuple[str, str]]], delimiter: str = "\n") -> str:
    results = []
    for field in fields:
        if not isinstance(field, tuple):
            field = (field, field.lower())
        attributes = field[1].split(",")
        current = original
        for attribute in attributes:
            if attribute in current:
                current = current.get(attribute)
            else:
                current = None
                break
        if current is not None:
            results.append((field[0], current))
    return delimiter.join([f"{pair[0]}: {pair[1]}" for pair in results])


def origin_to_text(origin: dict) -> str:
    fields: list[Union[str, tuple[str, str]]] = [
        ("Description", 'desc'),
        "Dynamic",
        ("Repost Title", 'title'),
        ("Video Summary", 'summary'),
        ("Description", "item,description")
    ]
    return dict_to_text(origin, fields)


async def main():
    Path(CACHE_ROOT).mkdir(exist_ok=True)
    arg_parser = ArgumentParser()
    arg_parser.add_argument("uid", type=int, nargs="+", help="A list of bilibili uid")
    arg_parser.add_argument("-f", "--force-download", dest="download", action="store_true", default=False,
                            help="Whether the program should use cached results or re-download dynamics from bilibili.")
    args = arg_parser.parse_args()

    def dynamic_to_str(d) -> str:
        did = d['desc']['dynamic_id']
        time = datetime.datetime.fromtimestamp(d['desc']['timestamp'])
        card = d['card']
        fields = [
            ('Content', 'item,content'),
            ('Description', 'item,description'),
            'Title'
        ]
        text = dict_to_text(card, fields)
        if text.isspace():
            text = str(card)
        if 'origin' in card:
            origin = json.loads(card['origin'])
            text += "\nOrigin:\n" + origin_to_text(origin)
        return f"ID: {did}\n" \
               f"Time: {time}\n" \
               f"{make_multiline(text)}\n"

    for uid in args.uid:
        dynamics = await fetch_dynamic(uid, use_cache=not args.download)

        for dynamic in dynamics:
            # print(dynamic)
            # logging.info(dynamic)
            print(dynamic_to_str(dynamic))


# 入口
if __name__ == '__main__':
    sync(main())
