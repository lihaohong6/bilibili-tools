from __future__ import annotations

from collections import Callable
from dataclasses import dataclass

from bilibili_api import Danmaku


# class Danmaku:
#     def __init__(self, text: str, time: int):
#         self.text = text
#         self.time = time


def parse_attrib(text: str) -> str:
    return text[:text.find(',')]


def build_cumulative_frequencies(frequencies: dict[int, int]) -> list[int]:
    keys = sorted(frequencies.keys())
    start = keys[0]
    end = keys[len(keys) - 1]
    cumulative_frequencies: list[int] = [start]
    for key in range(start, end + 1):
        curr = cumulative_frequencies[len(cumulative_frequencies) - 1]
        if key in frequencies:
            curr += frequencies[key]
        cumulative_frequencies.append(curr)
    return cumulative_frequencies


@dataclass
class Interval:
    start: int
    end: int


def convert_peaks(frequencies: dict[int, int], peak_multiplier: float) -> list[Interval]:
    frequency_list = list()
    start = min(frequencies.keys())
    end = max(frequencies.keys())
    for key in range(start, end + 1):
        frequency_list.append(frequencies[key] if key in frequencies else 0)
    # plot(frequency_list)
    average = sum(frequency_list) // len(frequency_list)
    peaks = [index for index, count in enumerate(frequency_list) if count >= average * peak_multiplier]
    result: list[Interval] = []
    curr = Interval(peaks[0], peaks[0])
    for peak in peaks:
        if peak <= curr.end + 1:
            curr.end = peak
        else:
            result.append(curr)
            curr = Interval(peak, peak)
    result.append(curr)
    return result


def seconds_to_time(seconds: int) -> str:
    return f"{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}"


def process_xml(danmaku_list: list[Danmaku], interval_length: int, peak_multiplier: float,
                keyword_checker: Callable[str, int] = lambda s: 1) -> str:
    # danmaku_list = []
    # for child in root:
    #     if child.tag != 'd':
    #         continue
    #     time = parse_attrib(child.attrib['p'])
    #     danmaku_list.append(Danmaku(child.text, int(float(time))))
    frequencies: dict[int, int] = dict()
    for danmaku in danmaku_list:
        key = int(danmaku.dm_time) // interval_length
        weight = keyword_checker(danmaku.text)
        if key in frequencies:
            frequencies[key] += weight
        else:
            frequencies[key] = weight
    intervals = convert_peaks(frequencies, peak_multiplier)
    result = f"{len(intervals)} results found:\n" + \
             "\n".join([f"{seconds_to_time(interval.start * interval_length)} to "
                        f"{seconds_to_time(interval.end * interval_length + interval_length - 1)}"
                        for interval in intervals])
    return result
