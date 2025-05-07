import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterator

from .metric_publisher import MetricPublisher

LOGGER = logging.getLogger(__name__)


class LogMetricPublisher(MetricPublisher):
    def __init__(
        self, prefix: str | None = None, level: int = logging.INFO, additional_tags: dict[str, str] | None = None
    ):
        super().__init__(prefix, additional_tags)
        self._level = level

    def count(self, metric_name: str, count: int, tags: dict[str, str] | None = None) -> None:
        LOGGER.log(self._level, "%s=%s", self._format_full_name(metric_name, tags), count)

    def duration(self, metric_name: str, duration: timedelta, tags: dict[str, str] | None = None) -> None:
        LOGGER.log(
            self._level, "%s.time=%.3fms", self._format_full_name(metric_name, tags), duration.total_seconds() * 1000
        )

    @contextmanager
    def timeit(self, metric_name: str, tags: dict[str, str] | None = None) -> Iterator[None]:
        start = datetime.now()
        try:
            yield
        finally:
            end = datetime.now()
            diff = end - start
            self.duration(metric_name, diff)

    def _format_full_name(self, metric_name: str, tags: dict[str, str] | None) -> str:
        name = metric_name if not self._prefix else f"{self._prefix}.{metric_name}"
        return self.format_metric_name_with_tags(name, tags, self._additional_tags, ",")
