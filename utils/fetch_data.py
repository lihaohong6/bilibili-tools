import json
from pathlib import Path
from typing import Any, Union
import xml.etree.ElementTree as ET

from bilibili_api import Danmaku, video, user
from bilibili_api.dynamic import Dynamic

from config import CACHE_ROOT

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
        file_path = Path(f"{CACHE_ROOT}/{bv}.json")
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


def store_json(path: Path, data):
    string = json.dumps(data, ensure_ascii=False, default=lambda o: getattr(o, '__dict__', str(o)))
    with open(path, "w") as file:
        file.write(string)


async def fetch_dynamic(uid: int, use_cache: bool = True) -> list[Dynamic]:
    path = Path(f"{CACHE_ROOT}/dynamic{str(uid)}.json")
    if use_cache and path.exists() and path.is_file():
        file = open(path, "r")
        return json.loads(file.read())
    u = user.User(uid=uid)
    # 用于记录下一次起点
    offset = 0

    # 用于存储所有动态
    dynamics = []

    # 无限循环，直到 has_more != 1
    while True:
        # 获取该页动态
        page = await u.get_dynamics(offset)

        if 'cards' in page:
            # 若存在 cards 字段（即动态数据），则将该字段列表扩展到 dynamics
            dynamics.extend(page['cards'])

        if page['has_more'] != 1:
            # 如果没有更多动态，跳出循环
            break

        # 设置 offset，用于下一轮循环
        offset = page['next_offset']

    store_json(path, dynamics)

    return dynamics
