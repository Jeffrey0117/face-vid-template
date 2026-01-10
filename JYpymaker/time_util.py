"""定義時間範圍類以及與時間相關的輔助函數"""

from typing import Union
from typing import Dict

SEC = 1000000
"""一秒=1e6微秒"""

def tim(inp: Union[str, float]) -> int:
    """將輸入的字串轉換為微秒, 也可直接輸入微秒數

    支持類似 "1h52m3s" 或 "0.15s" 這樣的格式, 可包含負號以表示負偏移
    """
    if isinstance(inp, (int, float)):
        return int(round(inp))

    sign: int = 1
    inp = inp.strip().lower()
    if inp.startswith("-"):
        sign = -1
        inp = inp[1:]

    last_index: int = 0
    total_time: float = 0
    for unit, factor in zip(["h", "m", "s"], [3600*SEC, 60*SEC, SEC]):
        unit_index = inp.find(unit)
        if unit_index == -1: continue

        total_time += float(inp[last_index:unit_index]) * factor
        last_index = unit_index + 1

    return int(round(total_time) * sign)

class Timerange:
    """記錄了起始時間及持續長度的時間範圍"""
    start: int
    """起始時間, 單位為微秒"""
    duration: int
    """持續長度, 單位為微秒"""

    def __init__(self, start: int, duration: int):
        """構造一個時間範圍

        Args:
            start (int): 起始時間, 單位為微秒
            duration (int): 持續長度, 單位為微秒
        """

        self.start = start
        self.duration = duration

    @classmethod
    def import_json(cls, json_obj: Dict[str, str]) -> "Timerange":
        """從json對象中恢復Timerange"""
        return cls(int(json_obj["start"]), int(json_obj["duration"]))

    @property
    def end(self) -> int:
        """結束時間, 單位為微秒"""
        return self.start + self.duration

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timerange):
            return False
        return self.start == other.start and self.duration == other.duration

    def overlaps(self, other: "Timerange") -> bool:
        """判斷兩個時間範圍是否有重疊"""
        return not (self.end <= other.start or other.end <= self.start)

    def __repr__(self) -> str:
        return f"Timerange(start={self.start}, duration={self.duration})"

    def __str__(self) -> str:
        return f"[start={self.start}, end={self.end}]"

    def export_json(self) -> Dict[str, int]:
        return {"start": self.start, "duration": self.duration}

def trange(start: Union[str, float], duration: Union[str, float]) -> Timerange:
    """Timerange的簡便構造函數, 接受字串或微秒數作為參數

    支持類似 "1h52m3s" 或 "0.15s" 這樣的格式

    Args:
        start (Union[str, float]): 起始時間
        duration (Union[str, float]): 持續長度, 注意**不是結束時間**
    """
    return Timerange(tim(start), tim(duration))

def srt_tstamp(srt_tstamp: str) -> int:
    """解析srt中的時間戳字串, 返回微秒數"""
    sec_str, ms_str = srt_tstamp.split(",")
    parts = sec_str.split(":") + [ms_str]

    total_time = 0
    for value, factor in zip(parts, [3600*SEC, 60*SEC, SEC, 1000]):
        total_time += int(value) * factor
    return total_time
