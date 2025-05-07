from contextlib import contextmanager
from datetime import timedelta
from enum import Enum
from typing import Iterator

from statsd import StatsClient

from .metric_publisher import MetricPublisher


class StatsdTagFormat(str, Enum):
    INFLUX_STATSD = "influx-statsd"
    GRAPHITE = "graphite"


class StatsdMetricPublisher(MetricPublisher):
    def __init__(
        self,
        statsd_client: StatsClient,
        prefix: str | None = None,
        additional_tags: dict[str, str] | None = None,
        tag_format: StatsdTagFormat = StatsdTagFormat.INFLUX_STATSD,
    ):
        super().__init__(prefix, additional_tags)
        self._client = statsd_client
        self._tag_format = tag_format
        self._tag_delemiter = "," if self._tag_format == StatsdTagFormat.INFLUX_STATSD else ";"

    @classmethod
    def new(
        cls,
        host: str,
        port: int,
        prefix: str | None = None,
        additional_tags: dict[str, str] | None = None,
        tag_format: StatsdTagFormat = StatsdTagFormat.INFLUX_STATSD,
    ) -> "StatsdMetricPublisher":
        statsd_client = StatsClient(host=host, port=port, prefix=prefix)
        return cls(statsd_client, prefix, additional_tags, tag_format)

    def count(self, metric_name: str, count: int, tags: dict[str, str] | None = None) -> None:
        self._client.incr(
            self.format_metric_name_with_tags(metric_name, tags, self._additional_tags, self._tag_delemiter), count
        )

    def duration(self, metric_name: str, duration: timedelta, tags: dict[str, str] | None = None) -> None:
        self._client.timing(
            self.format_metric_name_with_tags(metric_name, tags, self._additional_tags, self._tag_delemiter), duration
        )

    @contextmanager
    def timeit(self, metric_name: str, tags: dict[str, str] | None = None) -> Iterator[None]:
        with self._client.timer(
            self.format_metric_name_with_tags(metric_name, tags, self._additional_tags, self._tag_delemiter)
        ):
            yield
