from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Union
from uuid import uuid4


class Status(str, Enum):
    OK = "ok"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class Log:
    key: str = field(init=False, default_factory=lambda: uuid4().hex)
    function: str
    status: Status
    start_time: float
    end_time: float
    result: Dict[str, Union[str, int]]
