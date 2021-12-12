import datetime
import json
import logging
import math
from pathlib import Path

from bilibili_api import user, sync

width = 70


def make_multiline(text: str) -> str:
    paragraphs = text.split('\n')
    result = []
    for paragraph in paragraphs:
        line_count = math.ceil(len(paragraph) / width)
        for line_number in range(0, line_count):
            start = line_number * width
            end = min(start + width, len(paragraph))
            result.append(text[start:end])
        result.append("")
    return "\n".join(result)


async def main():
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(filename="logs/log.txt", level=logging.DEBUG)
    u = user.User(5050136)
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

    def dynamic_to_str(d) -> str:
        did = d['desc']['dynamic_id']
        time = datetime.datetime.fromtimestamp(d['desc']['timestamp'])
        card = d['card']
        if 'item' in card:
            item = card['item']
            if 'content' in item:
                text = item['content']
            else:
                text = item['description']
        elif 'title' in card:
            text = "Video title: " + card['title']
        else:
            text = str(d)
        return f"ID: {did}\n" \
               f"Time: {time}\n" \
               f"{make_multiline(text)}\n"

    for dynamic in dynamics:
        # print(dynamic)
        logging.info(dynamic)
        print(dynamic_to_str(dynamic))


# 入口
if __name__ == '__main__':
    sync(main())
