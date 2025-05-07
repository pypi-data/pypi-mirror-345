import datetime
import logging
import socket
import threading
import time
from typing import List

import pytest

from buildgrid.common.config import StatsdMetricPublisherConfig, create_metric_publisher
from buildgrid.common.metrics.log_metric_publisher import LogMetricPublisher
from buildgrid.common.metrics.statsd_metric_publisher import StatsdMetricPublisher


def test_common_metrics(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    publisher = LogMetricPublisher("dev")

    with publisher.common_metrics("test_metric"):
        pass

    assert len(caplog.record_tuples) == 2
    tuples = caplog.record_tuples
    assert tuples[0] == ("buildgrid.common.metrics.log_metric_publisher", logging.INFO, "dev.test_metric=1")
    assert tuples[1][2].endswith("ms")


def test_common_metrics_tags(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    publisher = LogMetricPublisher("dev")

    with publisher.common_metrics("test_metric", tags={"foo": "bar"}):
        pass

    assert len(caplog.record_tuples) == 2
    tuples = caplog.record_tuples
    assert tuples[0] == ("buildgrid.common.metrics.log_metric_publisher", logging.INFO, "dev.test_metric,foo=bar=1")
    assert tuples[1][2].endswith("ms")


def test_common_metrics_additional_tags(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    publisher = LogMetricPublisher("dev", additional_tags={"foo": "bar"})

    with publisher.common_metrics("test_metric"):
        pass

    assert len(caplog.record_tuples) == 2
    tuples = caplog.record_tuples
    assert tuples[0] == ("buildgrid.common.metrics.log_metric_publisher", logging.INFO, "dev.test_metric,foo=bar=1")
    assert tuples[1][2].endswith("ms")


def test_common_metrics_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    publisher = LogMetricPublisher("dev")

    try:
        with publisher.common_metrics("test_metric"):
            raise RuntimeError()
    except Exception:
        pass

    assert len(caplog.record_tuples) == 3
    tuples = caplog.record_tuples
    assert tuples[0] == ("buildgrid.common.metrics.log_metric_publisher", logging.INFO, "dev.test_metric=1")
    assert tuples[2] == ("buildgrid.common.metrics.log_metric_publisher", logging.INFO, "dev.test_metric.error=1")
    assert tuples[1][2].endswith("ms")


class MockStatsdServer:
    def __init__(self, port: int = 28125) -> None:
        self.data: List[bytes] = []
        self._stop = False
        self._lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        self.sock.settimeout(0.05)

    def run(self) -> None:
        self.t = threading.Thread(target=self._run)
        self.t.start()

    def stop(self) -> None:
        with self._lock:
            self._stop = True
        self.t.join()

    def _run(self) -> None:
        while True:
            try:
                data = self.sock.recv(128)
                with self._lock:
                    self.data.append(data)
            except socket.timeout:
                with self._lock:
                    if self._stop:
                        return
            time.sleep(0.05)


def test_statsd_metric_publisher() -> None:
    port = 28125
    publisher = StatsdMetricPublisher.new("127.0.0.1", prefix="buildgrid.common", port=port)
    mock_server = MockStatsdServer(port=port)
    mock_server.run()

    publisher.count("count", 2)
    publisher.duration("duration", datetime.timedelta(seconds=1, milliseconds=200, microseconds=345))

    mock_server.stop()
    assert mock_server.data == [
        b"buildgrid.common.count:2|c",
        b"buildgrid.common.duration:1200.345000|ms",
    ]


def test_statsd_metric_publisher_tags() -> None:
    port = 28125
    config = {
        "mode": "statsd",
        "name": "statsd_metric_publisher",
        "prefix": "buildgrid.common",
        "statsd_host": "127.0.0.1",
        "statsd_port": port,
        "tag_format": "influx-statsd",
    }
    publisher = create_metric_publisher(StatsdMetricPublisherConfig(**config))  # type: ignore[arg-type]
    mock_server = MockStatsdServer(port=port)
    mock_server.run()

    publisher.count("count", 2, tags={"foo": "bar"})
    publisher.duration(
        "duration", datetime.timedelta(seconds=1, milliseconds=200, microseconds=345), tags={"foo": "bar"}
    )

    mock_server.stop()
    assert mock_server.data == [
        b"buildgrid.common.count,foo=bar:2|c",
        b"buildgrid.common.duration,foo=bar:1200.345000|ms",
    ]


def test_statsd_metric_publisher_additional_tags() -> None:
    port = 28125
    config = {
        "mode": "statsd",
        "name": "statsd_metric_publisher",
        "prefix": "buildgrid.common",
        "statsd_host": "127.0.0.1",
        "statsd_port": port,
        "tag_format": "graphite",
        "additional_tags": {"k1": "v1"},
    }
    publisher = create_metric_publisher(StatsdMetricPublisherConfig(**config))  # type: ignore[arg-type]
    mock_server = MockStatsdServer(port=port)
    mock_server.run()

    publisher.count("count", 2, tags={"k2": "v2"})

    mock_server.stop()
    assert mock_server.data == [
        b"buildgrid.common.count;k2=v2;k1=v1:2|c",
    ]
