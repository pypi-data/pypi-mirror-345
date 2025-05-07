# Copyright (C) 2023 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
from enum import Enum
from typing import Annotated, Literal

from grpc import ServerCredentials, ssl_server_credentials
from pydantic import BaseModel, Field

from buildgrid.common.auth.config import parse_acl_config
from buildgrid.common.auth.enums import AuthMetadataAlgorithm
from buildgrid.common.auth.manager import AuthManager, HeadersAuthManager, JWTAuthManager, NoOpAuthManager
from buildgrid.common.metrics.log_metric_publisher import LogMetricPublisher
from buildgrid.common.metrics.metric_publisher import MetricPublisher
from buildgrid.common.metrics.statsd_metric_publisher import StatsdMetricPublisher, StatsdTagFormat


class MetricPublisherMode(str, Enum):
    LOG = "log"
    STATSD = "statsd"


class LogMetricPublisherConfig(BaseModel):
    mode: Literal["log"] = "log"
    name: str = "log_metric_publisher"
    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"] = "INFO"
    prefix: str | None = "buildgrid.logstream"
    additional_tags: dict[str, str] | None = None


class StatsdMetricPublisherConfig(BaseModel):
    mode: Literal["statsd"] = "statsd"
    name: str = "statsd_metric_publisher"
    prefix: str = "buildgrid.logstream"
    statsd_host: str = "localhost"
    statsd_port: int = 8125
    additional_tags: dict[str, str] | None = None
    tag_format: StatsdTagFormat = StatsdTagFormat.INFLUX_STATSD


MetricPublisherConfig = Annotated[LogMetricPublisherConfig | StatsdMetricPublisherConfig, Field(discriminator="mode")]


def create_metric_publisher(config: MetricPublisherConfig) -> MetricPublisher:
    if config.mode == MetricPublisherMode.LOG.value:
        return LogMetricPublisher(
            prefix=config.prefix, level=logging.getLevelName(config.level), additional_tags=config.additional_tags
        )
    elif config.mode == MetricPublisherMode.STATSD.value:
        return StatsdMetricPublisher.new(
            host=config.statsd_host,
            port=config.statsd_port,
            prefix=config.prefix,
            additional_tags=config.additional_tags,
            tag_format=config.tag_format,
        )
    else:
        raise ValueError("Invalid metric publisher config")


class TLSCredentials(BaseModel):
    # See also https://grpc.github.io/grpc/python/grpc.html#grpc.ssl_server_credentials

    key_path: str
    """File path to TLS key in PEM format"""
    cert_path: str
    """File path to TLS certificate in PEM format"""
    root_cert_path: str | None
    """File path to client root certificate in PEM format"""


def create_server_credentials(config: TLSCredentials) -> ServerCredentials:
    with open(config.key_path, "rb") as f:
        key = f.read()
    with open(config.cert_path, "rb") as f:
        cert = f.read()
    root_cert: bytes | None = None
    if config.root_cert_path:
        with open(config.root_cert_path, "rb") as f:
            root_cert = f.read()
    return ssl_server_credentials(
        [(key, cert)], root_certificates=root_cert, require_client_auth=root_cert is not None
    )


class AuthMetadataMode(str, Enum):
    # No authorization:
    NONE = "none"
    # Authorize based on client identity headers:
    HEADERS = "headers"
    # JWT based authorization:
    JWT = "jwt"


class NoAuthConfig(BaseModel):
    mode: Literal["none"] = AuthMetadataMode.NONE.value


class HeadersAuthConfig(BaseModel):
    mode: Literal["headers"] = AuthMetadataMode.HEADERS.value
    acl_path: str


class JWTAuthConfig(BaseModel):
    mode: Literal["jwt"] = AuthMetadataMode.JWT.value
    acl_path: str
    algorithm: AuthMetadataAlgorithm
    secret_path: str | None = None
    jwks_url: str | None = None
    audience: str | None = None
    jwks_fetch_minutes: int = 60


AuthConfig = Annotated[NoAuthConfig | HeadersAuthConfig | JWTAuthConfig, Field(discriminator="mode")]


def create_auth_manager(config: AuthConfig) -> AuthManager:
    if config.mode == AuthMetadataMode.NONE.value:
        return NoOpAuthManager()
    elif config.mode == AuthMetadataMode.HEADERS.value:
        return HeadersAuthManager(acls=parse_acl_config(config.acl_path))
    elif config.mode == AuthMetadataMode.JWT.value:
        secret = None
        if config.secret_path:
            with open(config.secret_path, "r") as f:
                secret = f.read()
        return JWTAuthManager(
            acls=parse_acl_config(config.acl_path),
            algorithm=config.algorithm,
            secret=secret,
            jwks_url=config.jwks_url,
            jwks_fetch_minutes=config.jwks_fetch_minutes,
            audience=config.audience,
        )

    raise ValueError("Invalid auth config")
