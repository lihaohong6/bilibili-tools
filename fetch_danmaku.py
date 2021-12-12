import json
from pathlib import Path
from typing import Any, Union
import xml.etree.ElementTree as ET

from bilibili_api import Danmaku, video

danmaku_attributes = ['dm_time', 'text']


def danmaku_to_dict(danmaku: Danmaku) -> dict[str, Any]:
    result = {}
    for attr in danmaku_attributes:
        result[attr] = getattr(danmaku, attr)
    return result


def danmaku_list_to_json(danmaku_list: list[Danmaku]) -> str:
    return json.dumps([danmaku_to_dict(d) for d in danmaku_list], ensure_ascii=False)


def json_to_danmaku_list(data: str) -> list[Danmaku]:
    dict_list = json.loads(data)
    result = []
    for d in dict_list:
        danmaku = Danmaku("")
        for attr in danmaku_attributes:
            setattr(danmaku, attr, d[attr])
        result.append(danmaku)
    return result


def parse_attrib(attrib: str) -> float:
    return float(attrib[:attrib.find(',')])


def xml_to_danmaku_list(filename: str) -> list[Danmaku]:
    tree = ET.parse(filename)
    root = tree.getroot()
    result = []
    for child in root:
        if child.tag == 'd':
            dm_time = parse_attrib(child.attrib['p'])
            result.append(Danmaku(text=child.text, dm_time=dm_time))
    return result


async def fetch_danmaku(v: Union[video.Video, str]) -> list[Danmaku]:
    if isinstance(v, video.Video):
        bv = v.get_bvid()
        file_path = Path(f"cache/{bv}.json")
        if file_path.exists():
            data = open(file_path, 'r', encoding='utf8').read()
            danmaku_list = json_to_danmaku_list(data)
        else:
            danmaku_list: list[Danmaku] = await v.get_danmakus(0)
            with open(file_path, 'w', encoding='utf8') as file:
                file.write(danmaku_list_to_json(danmaku_list))
        return danmaku_list
    else:
        return xml_to_danmaku_list(v)
