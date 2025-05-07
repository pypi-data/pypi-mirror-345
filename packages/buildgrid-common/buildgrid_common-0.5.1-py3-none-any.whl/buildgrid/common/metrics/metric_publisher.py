from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import timedelta
from typing import ContextManager, Iterator

ERROR_SUFFIX = ".error"


class MetricPublisher(ABC):
    """A minimal interface to publish metrics"""

    def __init__(self, prefix: str | None, additional_tags: dict[str, str] | None) -> None:
        self._prefix = prefix
        self._additional_tags = additional_tags or {}

    @abstractmethod
    def count(self, metric_name: str, count: int, tags: dict[str, str] | None = None) -> None:
        """Send a count metric

        Example:
            def some_func():
                metric_publisher.count("some_func", 1)
                # ...

        Args:
            metric_name (str): Name of the metric
            count (int): Count to increase
        """
        pass

    @abstractmethod
    def duration(self, metric_name: str, duration: timedelta, tags: dict[str, str] | None = None) -> None:
        """Send a duration metric

        Example:
            def some_func():
                start = datetime.now()
                # ...
                end = datetime.now()
                metric_publisher.duration("some_func", end - start)
        Args:
            metric_name (str): Name of the metric
            duration (timedelta): Duration to publish
        """
        pass

    @abstractmethod
    def timeit(self, metric_name: str, tags: dict[str, str] | None = None) -> ContextManager[None]:
        """Context manager to time a code block

        Example:
            def some_func():
                with metric_publisher.timeit("some_func"):
                    #...
                # a duration metric is published
        Args:
            metric_name (str): Name of the metric

        Returns:
            ContextManager[None]:
        """
        pass

    @contextmanager
    def common_metrics(self, metric_name: str, tags: dict[str, str] | None = None) -> Iterator[None]:
        """Context manger that publishes metrics of one count, duration,
            and error count if an exception happens

        Args:
            metric_name (str): Name of the metric

        Yields:
            Iterator[None]:
        """
        self.count(metric_name, 1, tags)
        try:
            with self.timeit(metric_name, tags):
                yield
        except Exception:
            self.count(metric_name + ERROR_SUFFIX, 1, tags)
            raise

    @staticmethod
    def format_metric_name_with_tags(
        metric_name: str, tags: dict[str, str] | None, additional_tags: dict[str, str] | None, tag_delimiter: str
    ) -> str:
        tag_strs: list[str] = []
        if tags:
            for key, value in tags.items():
                tag_strs.append(f"{key}={value}")
        if additional_tags:
            for key, value in additional_tags.items():
                tag_strs.append(f"{key}={value}")

        if tag_strs:
            joined_tags = tag_delimiter.join(tag_strs)
            metric_name = f"{metric_name}{tag_delimiter}{joined_tags}"

        return metric_name
