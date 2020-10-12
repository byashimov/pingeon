from datetime import datetime, timezone
from time import perf_counter


def utcnow() -> float:
    return datetime.now(tz=timezone.utc).timestamp()


class timer:
    start: float
    end: float

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter()

    # todo: replace with cached_property
    @property
    def total(self) -> float:
        return self.end - self.start
