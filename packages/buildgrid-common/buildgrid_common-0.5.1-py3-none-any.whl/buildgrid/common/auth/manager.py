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


import asyncio
import logging
import sys
from abc import ABC, abstractmethod
from typing import Any, Mapping, NoReturn, cast

import grpc.aio as grpc

from buildgrid.common.auth.config import InstanceAuthorizationConfig
from buildgrid.common.auth.enums import AuthMetadataAlgorithm
from buildgrid.common.auth.exceptions import (
    AuthError,
    ExpiredTokenError,
    InvalidAuthorizationHeaderError,
    InvalidTokenError,
    MissingTokenError,
    UnboundedTokenError,
    UnexpectedTokenParsingError,
)

# Since jwt authorization is not required, make it optional.
# If used, but module not imported/found, will raise an exception.
try:
    import jwt
except ImportError:
    pass


LOGGER = logging.getLogger(__name__)


def _log_and_raise(request_name: str, exception: AuthError) -> NoReturn:
    LOGGER.info(f"Authorization error. Rejecting {request_name=}", exc_info=exception)
    raise exception


JWKS_CACHE_SIZE = 64


class JwtParser:
    def __init__(
        self,
        *,
        algorithm: AuthMetadataAlgorithm,
        secret: str | None = None,
        jwks_url: str | None = None,
        audience: str | None = None,
        jwks_fetch_minutes: int = 60,
    ) -> None:
        self._check_jwt_support()

        self._algorithm = algorithm
        self._audience = audience
        self._jwks_client = None

        if (secret is None and jwks_url is None) or (secret is not None and jwks_url is not None):
            raise TypeError("Exactly one of `secret` or `jwks_url` must be set")

        self._secret = secret

        if jwks_url is not None:
            try:
                jwks_lifespan = jwks_fetch_minutes * 60
                self._jwks_client = jwt.PyJWKClient(jwks_url, lifespan=jwks_lifespan, max_cached_keys=JWKS_CACHE_SIZE)
            except NameError:
                LOGGER.error("JWT auth is enabled but PyJWT could not be imported.")
                raise

    def _check_jwt_support(self) -> None:
        if "jwt" not in sys.modules:
            raise RuntimeError("JWT authorization method requires PyJWT")

    async def parse(self, token: str) -> dict[str, Any]:
        payload: dict[str, Any] | None = None
        try:
            if self._secret is not None:
                payload = jwt.decode(
                    token,
                    self._secret,
                    algorithms=[self._algorithm.value.upper()],
                    audience=self._audience,
                    options={"require": ["exp"], "verify_exp": True},
                )

            elif self._jwks_client is not None:
                signing_key = await asyncio.to_thread(self._jwks_client.get_signing_key_from_jwt, token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[self._algorithm.value.upper()],
                    audience=self._audience,
                    options={"require": ["exp"], "verify_exp": True},
                )

        except jwt.exceptions.ExpiredSignatureError as e:
            raise ExpiredTokenError() from e

        except jwt.exceptions.MissingRequiredClaimError as e:
            raise UnboundedTokenError("Missing required JWT claim, likely 'exp' was not set") from e

        except jwt.exceptions.InvalidTokenError as e:
            raise InvalidTokenError() from e

        except Exception as e:
            raise UnexpectedTokenParsingError() from e

        if payload is None:
            raise InvalidTokenError()

        return payload

    async def identity_from_token(self, token: str) -> tuple[str | None, str | None, str | None]:
        payload = await self.parse(token)
        return payload.get("act"), payload.get("sub"), payload.get("aud")


class AuthManager(ABC):
    @abstractmethod
    async def authorize(self, context: grpc.ServicerContext[Any, Any], instance_name: str, request_name: str) -> bool:
        """Determine whether or not a request is authorized.

        This method takes a ``ServicerContext[Any,Any]`` for an incoming gRPC request,
        along with the name of the request, and the name of the instance that
        the request is intended for. Information about the identity of the
        requester is extracted from the context, for example a JWT token.

        This identity information is compared to the ACL configuration given
        to this class at construction time to determine authorization for the
        request.

        Args:
            context (ServicerContext[Any,Any]): The context for the gRPC request to check
                the authz status of.

            instance_name (str): The name of the instance that the gRPC request
                will be interacting with. This is used for per-instance ACLs.

            request_name (str): The name of the request being authorized, for
                example `Execute`.

        Returns:
            bool: Whether the request is authorized.

        """


class JWTAuthManager(AuthManager):
    def __init__(
        self,
        *,
        acls: Mapping[str, InstanceAuthorizationConfig],
        algorithm: AuthMetadataAlgorithm,
        secret: str | None,
        jwks_url: str | None,
        audience: str | None,
        jwks_fetch_minutes: int,
    ) -> None:
        """Initializes a new :class:`JWTAuthManager`.

        Args:
            acls (Mapping[str, InstanceAuthorizationConfig]): An optional
                map of instance name -> ACL config to use for per-instance
                authorization.

            algorithm (AuthMetadataAlgorithm): The crytographic algorithm used
                to encode `secret`.

            secret (str): The secret or key to be used for validating request,
                depending on `method`.

            jwks_url (str): The url to fetch the JWKs. Either secret or
                this field must be specified if the authentication method is JWT.

            audience (str): The audience used to validate jwt tokens against.
                The tokens must have an audience field.

            jwks_fetch_minutes (int): The number of minutes to cache JWKs fetches for.

        Raises:
            InvalidArgumentError: If `algorithm` is not supported.

        """
        self._acls = acls
        self._token_parser = JwtParser(
            secret=secret,
            algorithm=algorithm,
            jwks_url=jwks_url,
            audience=audience,
            jwks_fetch_minutes=jwks_fetch_minutes,
        )

    def _token_from_request_context(self, context: grpc.ServicerContext[Any, Any], request_name: str) -> str:
        try:
            # The interface of this method is wrong
            bearer = cast(str, dict(context.invocation_metadata())["authorization"])  # type: ignore[arg-type]
            # Reject requests with malformatted bearer
            if not bearer.startswith("Bearer "):
                _log_and_raise(request_name, InvalidAuthorizationHeaderError())

            return bearer[7:]
        except KeyError:
            # Reject requests not carrying a token
            _log_and_raise(request_name, MissingTokenError())

    async def authorize(self, context: grpc.ServicerContext[Any, Any], instance_name: str, request_name: str) -> bool:
        token = self._token_from_request_context(context, request_name)
        try:
            actor, subject, workflow = await self._token_parser.identity_from_token(token)
        except NameError:
            LOGGER.error("JWT auth is enabled but PyJWT is not installed.")
            return False
        except AuthError as e:
            LOGGER.info("Error authorizing JWT token", exc_info=e)
            return False

        instance_acl_config = self._acls.get(instance_name)
        if instance_acl_config is not None:
            return instance_acl_config.is_authorized(request_name, actor=actor, subject=subject, workflow=workflow)

        # If there is an ACL, but no config for this instance, deny all
        return False


class HeadersAuthManager(AuthManager):
    def __init__(
        self,
        acls: Mapping[str, InstanceAuthorizationConfig],
    ) -> None:
        """Initializes a new :class:`HeadersAuthManager`.

        Args:
            acls (Mapping[str, InstanceAuthorizationConfig]): An optional
                map of instance name -> ACL config to use for per-instance
                authorization.
        """
        self._acls = acls

    async def authorize(self, context: grpc.ServicerContext[Any, Any], instance_name: str, request_name: str) -> bool:
        # The interface of `invocation_metadata()` is wrong
        metadata_dict: dict[str, str] = dict(context.invocation_metadata())  # type: ignore [arg-type]
        actor = str(metadata_dict.get("x-request-actor"))
        subject = str(metadata_dict.get("x-request-subject"))
        workflow = str(metadata_dict.get("x-request-workflow"))

        instance_acl_config = self._acls.get(instance_name)
        if instance_acl_config is not None:
            return instance_acl_config.is_authorized(request_name, actor=actor, subject=subject, workflow=workflow)

        # If there is an ACL, but no config for this instance, deny all
        return False


class NoOpAuthManager(AuthManager):
    async def authorize(self, context: grpc.ServicerContext[Any, Any], instance_name: str, request_name: str) -> bool:
        """Always allow the request if auth is not configured"""
        return True
