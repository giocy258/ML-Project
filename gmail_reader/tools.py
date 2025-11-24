from typing import Optional, Dict
import datetime
from zoneinfo import ZoneInfo


def tool_datetime_now(tz_name: str = "Europe/Rome") -> datetime.datetime:

    local_tz = ZoneInfo(tz_name)
    return datetime.datetime.now(local_tz)

