from typing import Callable
from dataclasses import dataclass

from bilibili_api import Danmaku


# class Danmaku:
#     def __init__(self, text: str, time: int):
#         self.text = text
#         self.time = time


def parse_attrib(text: str) -> str:
    return text[:text.find(',')]


def build_cumulative_frequencies(frequencies: list[int]) -> list[int]:
    cumulative = frequencies.copy()
    for index in range(1, len(frequencies)):
        cumulative[index] += cumulative[index - 1]
    return cumulative


@dataclass
class Interval:
    start: int
    end: int


# TODO: what if stream popularity goes up and down; determine danmaku density relative to a 10 minutes window?
def convert_peaks(frequencies: list[int], min_interval: int, peak_multiplier: float) -> list[Interval]:
    average = sum(frequencies) / len(frequencies)
    cumulative = build_cumulative_frequencies(frequencies)
    # FIXME: 0th second will never be selected in a peak. But does that really matter?
    peaks = [Interval(index - min_interval + 1, index)
             for index in range(min_interval, len(frequencies))
             if (cumulative[index] - cumulative[index - min_interval]) / min_interval / average >= peak_multiplier]
    result = []
    if len(peaks) == 0:
        return []
    curr: Interval = peaks[0]
    for peak in peaks:
        if peak.start <= curr.end + 1:
            curr.end = peak.end
        else:
            result.append(curr)
            curr = peak
    result.append(curr)
    return result


def seconds_to_time(seconds: int) -> str:
    return f"{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}"


def build_frequencies(danmaku_list: list[Danmaku], keyword_checker: Callable[[str], int]):
    end_time = int(max(danmaku_list, key=lambda d: d.dm_time).dm_time)
    frequency_list = [0] * (end_time + 1)
    for danmaku in danmaku_list:
        time = int(danmaku.dm_time)
        weight = keyword_checker(danmaku.text)
        frequency_list[time] += weight
    return frequency_list


def process_danmaku(danmaku_list: list[Danmaku], interval_length: int, peak_multiplier: float,
                    keyword_checker: Callable[[str], int] = lambda s: 1) -> str:
    frequencies: list[int] = build_frequencies(danmaku_list, keyword_checker)
    intervals = convert_peaks(frequencies, interval_length, peak_multiplier)
    result = f"{len(intervals)} results found:\n" + \
             "\n".join([f"{seconds_to_time(interval.start)} to "
                        f"{seconds_to_time(interval.end)}"
                        for interval in intervals])
    return result
