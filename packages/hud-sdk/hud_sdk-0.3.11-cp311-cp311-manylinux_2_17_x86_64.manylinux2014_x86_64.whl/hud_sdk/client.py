import asyncio
import gzip
import json
import pprint
import socket
import ssl
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import (
    Any,
    Coroutine,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import uuid4

import aiohttp
import requests
from requests.adapters import HTTPAdapter, Retry

from .config import config
from .logging import internal_logger
from .schemas import events
from .schemas.events import FileDeclaration
from .schemas.requests import (
    Batch as BatchRequest,
)
from .schemas.requests import (
    FatalError as FatalErrorRequest,
)
from .schemas.requests import (
    FileDeclarations as FileDeclarationsRequest,
)
from .schemas.requests import (
    Init as InitRequest,
)
from .schemas.requests import (
    Ping,
)
from .schemas.requests import (
    Send as SendRequest,
)
from .schemas.responses import (
    FileDeclarations as FileDeclarationsResponse,
)
from .user_options import UserOptions
from .version import version as hud_version


class HudClientException(Exception):
    pass


class HudThrottledException(Exception):
    pass


SyncHandlerReturnType = Any
AsyncHandlerReturnType = Coroutine[Any, Any, Any]
HandlerReturnType = TypeVar(
    "HandlerReturnType", AsyncHandlerReturnType, SyncHandlerReturnType
)


class Client(Generic[HandlerReturnType], ABC):
    session_id = None  # type: Optional[str]

    def set_session_id(self, session_id: str) -> None:
        internal_logger.debug("Setting session_id", data=dict(session_id=session_id))
        self.session_id = session_id

    @abstractmethod
    def init_session(self, exporter_id: str) -> HandlerReturnType:
        pass

    @abstractmethod
    def get_remote_config(self) -> HandlerReturnType:
        pass

    @abstractmethod
    def send_logs_json(self, data: Any, request_type: str) -> HandlerReturnType:
        pass

    @abstractmethod
    def send_sessionless_logs_json(
        self, data: Any, request_type: str
    ) -> HandlerReturnType:
        pass

    @abstractmethod
    def send_file_declarations(
        self, ordered_file_declarations: List[FileDeclaration]
    ) -> HandlerReturnType:
        pass

    @abstractmethod
    def send_batch_json(self, data: Any, request_type: str) -> HandlerReturnType:
        pass

    @abstractmethod
    def send_single_json(self, data: Any, request_type: str) -> HandlerReturnType:
        pass

    @abstractmethod
    def send_fatal_error(self, fatal_error: FatalErrorRequest.FatalErrorData) -> None:
        pass

    @abstractmethod
    def keepalive(self) -> HandlerReturnType:
        pass

    @abstractmethod
    def close(self) -> HandlerReturnType:
        pass

    @property
    @abstractmethod
    def is_async(self) -> bool:
        pass


class ConsoleClient(Client[SyncHandlerReturnType]):
    def init_session(self, exporter_id: str) -> None:
        print("init_session exporter_id={}".format(exporter_id), file=sys.stderr)

    def get_remote_config(self) -> Optional[Dict[str, Union[List[str], int]]]:
        print("get_remote_config", file=sys.stderr)
        return None

    def send_logs_json(self, data: Any, request_type: str) -> None:
        print("send_logs_json", file=sys.stderr)
        for log in data["logs"]:
            pprint.pprint({"type": "Log", **log}, stream=sys.stderr, sort_dicts=False)

    def send_sessionless_logs_json(self, data: Any, request_type: str) -> None:
        print("send_sessionless_logs_json", file=sys.stderr)
        for log in data["logs"]:
            pprint.pprint({"type": "Log", **log}, stream=sys.stderr, sort_dicts=False)

    def send_file_declarations(
        self, ordered_file_declarations: List[FileDeclaration]
    ) -> FileDeclarationsResponse:
        print("send_file_declarations", file=sys.stderr)
        for item in ordered_file_declarations:
            pprint.pprint(
                {"type": "FileDeclaration", **item.to_json_data()},
                stream=sys.stderr,
                sort_dicts=False,
            )
        return FileDeclarationsResponse([], True)

    def send_batch_json(self, data: Any, request_type: str) -> None:
        print("Send batch of {} {}".format(len(data), request_type), file=sys.stderr)
        for item in data:
            pprint.pprint(
                {"type": request_type, **item}, stream=sys.stderr, sort_dicts=False
            )

    def send_single_json(self, data: Any, request_type: str) -> None:
        print("Send single {}".format(request_type), file=sys.stderr)
        pprint.pprint(
            {"type": request_type, **data}, stream=sys.stderr, sort_dicts=False
        )

    def keepalive(self) -> None:
        print("keepalive", file=sys.stderr)

    @property
    def is_async(self) -> bool:
        return False

    def close(self) -> None:
        return

    def send_fatal_error(self, fatal_error: FatalErrorRequest.FatalErrorData) -> None:
        fatal_error_request = FatalErrorRequest(
            fatal_error,
            send_time=datetime.now(timezone.utc),
        )
        print(
            "send_fatal_error: {}".format(fatal_error_request.to_json_data()),
            file=sys.stderr,
        )


class JSONClient(Client[SyncHandlerReturnType]):
    def __init__(self, path: str) -> None:
        self.path = path

    def _write_to_json(self, data: Any) -> None:
        with open(self.path, mode="a") as file:
            file.write(json.dumps(data) + "\n")

    def init_session(self, exporter_id: str) -> None:
        self._write_to_json({"type": "init_session", "exporter_id": exporter_id})

    def get_remote_config(self) -> Optional[Dict[str, Union[List[str], int]]]:
        self._write_to_json({"type": "get_remote_config"})
        return None

    def send_logs_json(self, data: Any, request_type: str) -> None:
        for log in data["logs"]:
            self._write_to_json({"type": "log", **log})

    def send_sessionless_logs_json(self, data: Any, request_type: str) -> None:
        for log in data["logs"]:
            self._write_to_json({"type": "log", **log})

    def send_file_declarations(
        self, ordered_file_declarations: List[FileDeclaration]
    ) -> FileDeclarationsResponse:
        for item in ordered_file_declarations:
            self._write_to_json({"type": "FileDeclaration", **item.to_json_data()})
        return FileDeclarationsResponse([], True)

    def send_batch_json(self, data: Any, request_type: str) -> None:
        for item in data:
            self._write_to_json({"type": request_type, **item})

    def send_single_json(self, data: Any, request_type: str) -> None:
        self._write_to_json({"type": request_type, **data})

    def keepalive(self) -> None:
        self._write_to_json({"type": "keepalive"})

    @property
    def is_async(self) -> bool:
        return False

    def close(self) -> None:
        return

    def send_fatal_error(self, fatal_error: FatalErrorRequest.FatalErrorData) -> None:
        fatal_error_request = FatalErrorRequest(
            fatal_error, send_time=datetime.now(timezone.utc)
        )
        self._write_to_json(
            {"type": "fatal_error", **fatal_error_request.to_json_data()}
        )


class BaseHttpClient(Client[HandlerReturnType]):
    source = "python-sdk"

    api_key: str
    service: Optional[str]
    tags: Dict[str, str]
    session: "Optional[aiohttp.ClientSession | requests.Session]"
    session_id: Optional[str]
    max_retries: int
    backoff_factor: float
    status_forcelist: List[int]

    def __init__(self, host: str, user_identity: "UserOptions | str") -> None:
        self.host = host
        if isinstance(user_identity, UserOptions):
            self.api_key = user_identity.key
            self.service = user_identity.service
            self.tags = user_identity.tags
        else:
            self.api_key = user_identity
            self.service = None
            self.tags = {}
        self.session = None
        self.session_id = None
        self.max_retries = config.api_max_retries
        self.backoff_factor = config.api_backoff_factor
        self.status_forcelist = [429, 500, 502, 503, 504]

    @abstractmethod
    def _send(self, uri: str, request: Any, request_type: str) -> HandlerReturnType:
        pass

    def set_session_id(self, session_id: str) -> None:
        super().set_session_id(session_id)
        if self.session:
            self.session.headers["X-Session-ID"] = session_id


class AsyncHttpClient(BaseHttpClient[AsyncHandlerReturnType]):
    def __init__(self, host: str, user_identity: "UserOptions | str") -> None:
        super().__init__(host, user_identity)

        ssl_context = self._create_ssl_context()
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        )  # type: aiohttp.ClientSession
        if not hasattr(self.session, "headers"):
            self.session.headers = {}  # type: ignore[misc, assignment]

        self.timeout = None  # type: Optional[aiohttp.ClientTimeout | float]
        if hasattr(aiohttp, "ClientTimeout"):
            self.timeout = aiohttp.ClientTimeout(total=config.api_timeout)
        else:
            self.timeout = config.api_timeout

    @staticmethod
    def _create_ssl_context() -> ssl.SSLContext:
        if config.user_cert:
            return ssl.create_default_context(cafile=config.user_cert)
        elif config.user_ca_bundle:
            return ssl.create_default_context(cafile=config.user_ca_bundle)
        return ssl.create_default_context()

    @property
    def is_async(self) -> bool:
        return True

    async def _send(self, uri: str, request: Any, request_type: str) -> Any:
        url = "{}/{}".format(self.host, uri)
        headers = {
            "Content-Type": "application/json",
            "X-Hud-Request-ID": str(uuid4()),
            "Content-Encoding": "gzip",
        }

        if self.session_id:
            headers["X-Session-ID"] = self.session_id
        if request_type:
            headers["X-Hud-Type"] = request_type
        if self.session.headers:
            # In old versions of aiohttp, session headers are not sent with the request
            headers.update(self.session.headers)
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    url,
                    data=gzip.compress(json.dumps(request).encode("utf-8")),
                    headers=headers,
                    timeout=self.timeout,  # type: ignore[arg-type]
                ) as res:
                    if (
                        res.status in self.status_forcelist
                        and attempt < self.max_retries - 1
                    ):
                        await asyncio.sleep(self.backoff_factor * (2**attempt))
                        continue
                    res.raise_for_status()
                    if res.status == 202:
                        raise HudThrottledException()
                    return await res.json()
            except HudThrottledException:
                raise
            except Exception as e:
                if attempt < self.max_retries - 1 and self.should_retry(e):
                    await asyncio.sleep(self.backoff_factor * (2**attempt))
                    continue

                internal_logger.warning(
                    "Failed to send request",
                    data=dict(type=request_type),
                    exc_info=True,
                )
                raise

    def should_retry(self, e: Exception) -> bool:
        if hasattr(aiohttp, "ClientConnectorDNSError"):
            if isinstance(e, aiohttp.ClientConnectorDNSError):
                return True
        if isinstance(e, aiohttp.ClientConnectorError) and isinstance(
            e.os_error, socket.gaierror
        ):
            return True
        if isinstance(e, asyncio.TimeoutError):
            return True
        return False

    async def init_session(self, exporter_id: str) -> None:
        internal_logger.debug(
            "Initializing session for service", data=dict(service=self.service)
        )
        if self.service is None:
            raise HudClientException("Cannot initialize session without service")
        request = InitRequest(
            token=self.api_key,
            service=self.service,
            start_time=datetime.now(timezone.utc),
            type=self.source,
            sdk_version=hud_version,
            tags=self.tags,
            exporter_run_id=exporter_id,
        )
        internal_logger.debug("Sending request", data={"type": "Init"})
        res = await self._send("sink/init", request.to_json_data(), "Init")
        session_id = res["sessionId"]
        self.set_session_id(session_id)

        extra_headers = res.get("extraHeaders")
        if extra_headers:
            for key, value in extra_headers.items():
                try:
                    self.session.headers[key] = str(value)
                except Exception:
                    internal_logger.warning(
                        "Failed to set extra header", data=dict(key=key)
                    )

    async def get_remote_config(self) -> Optional[Dict[str, Union[List[str], int]]]:
        internal_logger.debug("Sending request", data={"type": "GetRemoteConfig"})
        return await self._send("sink/remote-config/get", {}, "GetRemoteConfig")  # type: ignore[no-any-return]

    async def send_logs_json(self, data: Any, request_type: str) -> None:
        await self._send("sink/logs", data, request_type)

    async def send_sessionless_logs_json(self, data: Any, request_type: str) -> None:
        internal_logger.debug("Sending request", data={"type": request_type})
        await self._send("sink/sessionless-logs", data, request_type)

    async def send_file_declarations(
        self, ordered_file_declarations: List[FileDeclaration]
    ) -> FileDeclarationsResponse:
        internal_logger.debug("Sending request", data={"type": "FileDeclarations"})

        file_declarations_request = FileDeclarationsRequest(ordered_file_declarations)

        wanted_files = await self._send(
            "sink/file-declarations",
            file_declarations_request.to_json_data(),
            "FileDeclarations",
        )
        return FileDeclarationsResponse.from_json_data(wanted_files)

    async def send_batch_json(self, data: Any, request_type: str) -> None:
        arr = cast(List[Any], data)
        size = config.batch_size
        version = cast(Type[events.Event], getattr(events, request_type)).get_version()
        internal_logger.debug("Sending request", data={"type": request_type})
        for i in range(0, len(arr), size):
            request = BatchRequest(
                arr=[i for i in arr[i : i + size]],
                event_version=version,
                send_time=datetime.now(timezone.utc),
                source=self.source,
                type=request_type,
            )
            await self._send("sink/batch", request.to_json_data(), request_type)

    async def send_single_json(self, data: Any, request_type: str) -> None:
        internal_logger.debug("Sending request", data={"type": request_type})
        request = SendRequest(
            event_version=getattr(events, request_type).get_version(),
            send_time=datetime.now(timezone.utc),
            source=self.source,
            type=request_type,
            raw=data,
        )
        await self._send("sink/send", request.to_json_data(), request_type)

    async def keepalive(self) -> None:
        internal_logger.debug("Sending request", data={"type": "Keepalive"})
        request = Ping(send_time=datetime.now(timezone.utc))
        await self._send("sink/ping", request.to_json_data(), "Keepalive")

    def send_fatal_error(self, fatal_error: FatalErrorRequest.FatalErrorData) -> None:
        raise NotImplementedError(
            "send_fatal_error is not implemented for async client"
        )

    async def close(self) -> None:
        await self.session.close()


class SyncHttpClient(BaseHttpClient[SyncHandlerReturnType]):
    def __init__(self, host: str, user_identity: "UserOptions | str") -> None:
        super().__init__(host, user_identity)
        self.session = requests.Session()  # type: requests.Session
        self.verify = config.user_cert or config.user_ca_bundle
        self.session.mount(
            self.host,
            HTTPAdapter(
                max_retries=Retry(
                    total=config.api_max_retries,
                    backoff_factor=config.api_backoff_factor,
                    status_forcelist=self.status_forcelist,
                )
            ),
        )

    def _send(self, uri: str, request: Any, request_type: str) -> Any:
        try:
            with self.session.post(
                "{}/{}".format(self.host, uri),
                data=gzip.compress(json.dumps(request).encode("utf-8")),
                verify=self.verify,
                headers={
                    "X-Hud-Type": request_type,
                    "X-Hud-Request-ID": str(uuid4()),
                    "Content-Encoding": "gzip",
                    "Content-Type": "application/json",
                },
            ) as res:
                res.raise_for_status()
                if res.status_code == 202:
                    raise HudThrottledException()
                return res.json()
        except HudThrottledException:
            raise
        except requests.exceptions.SSLError:
            internal_logger.warning(
                "Failed to send request, SSLError",
                data=dict(type=request_type),
                exc_info=True,
            )
        except Exception:
            internal_logger.warning(
                "Failed to send request", data=dict(type=request_type), exc_info=True
            )
            raise

    @property
    def is_async(self) -> bool:
        return False

    def close(self) -> None:
        self.session.close()

    def init_session(self, exporter_id: str) -> None:
        if self.service is None or self.tags is None:
            raise HudClientException(
                "Cannot initialize session without service and tags"
            )
        internal_logger.debug("Sending request", data={"type": "Init"})
        internal_logger.debug(
            "Initializing session for service", data=dict(service=self.service)
        )
        request = InitRequest(
            token=self.api_key,
            service=self.service,
            start_time=datetime.now(timezone.utc),
            type=self.source,
            sdk_version=hud_version,
            tags=self.tags,
            exporter_run_id=exporter_id,
        )
        res = self._send("sink/init", request.to_json_data(), "Init")
        session_id = res["sessionId"]
        self.set_session_id(session_id)

        extra_headers = res.get("extraHeaders")
        if extra_headers:
            for key, value in extra_headers.items():
                try:
                    self.session.headers[key] = str(value)
                except Exception:
                    internal_logger.warning(
                        "Failed to set extra header", data=dict(key=key)
                    )

    def get_remote_config(self) -> Optional[Dict[str, Union[List[str], int]]]:
        internal_logger.debug("Sending request", data={"type": "GetRemoteConfig"})
        return self._send("sink/remote-config/get", {}, "GetRemoteConfig")  # type: ignore[no-any-return]

    def send_logs_json(self, data: Any, request_type: str) -> None:
        internal_logger.debug("Sending request", data={"type": request_type})
        self._send("sink/logs", data, request_type)

    def send_sessionless_logs_json(self, data: Any, request_type: str) -> None:
        self._send("sink/sessionless-logs", data, request_type)

    def send_file_declarations(
        self, ordered_file_declarations: List[FileDeclaration]
    ) -> FileDeclarationsResponse:
        raise NotImplementedError

    def send_batch_json(self, data: Any, request_type: str) -> None:
        arr = cast(List[Any], data)
        size = config.batch_size
        version = cast(Type[events.Event], getattr(events, request_type)).get_version()
        internal_logger.debug("Sending request", data={"type": request_type})
        for i in range(0, len(arr), size):
            request = BatchRequest(
                arr=[i for i in arr[i : i + size]],
                event_version=version,
                send_time=datetime.now(timezone.utc),
                source=self.source,
                type=request_type,
            )
            self._send("sink/batch", request.to_json_data(), request_type)

    def send_single_json(self, data: Any, request_type: str) -> None:
        internal_logger.debug("Sending request", data={"type": request_type})
        request = SendRequest(
            event_version=getattr(events, request_type).get_version(),
            send_time=datetime.now(timezone.utc),
            source=self.source,
            type=request_type,
            raw=data,
        )
        self._send("sink/send", request.to_json_data(), request_type)

    def send_fatal_error(self, fatal_error: FatalErrorRequest.FatalErrorData) -> None:
        internal_logger.debug("Sending request", data={"type": "FatalError"})
        request = FatalErrorRequest(
            fatal_error,
            send_time=datetime.now(timezone.utc),
            token=self.api_key,
            service=self.service,
        )
        self._send("sink/redline", request.to_json_data(), "FatalError")

    def keepalive(self) -> None:
        internal_logger.debug("Sending request", data={"type": "Keepalive"})
        request = Ping(
            send_time=datetime.now(timezone.utc),
        )
        self._send("sink/ping", request.to_json_data(), "Keepalive")


def get_client(
    is_async: bool, user_identity: "UserOptions | str"
) -> Client[HandlerReturnType]:

    client_type = config.client_type
    if client_type == "console":
        return ConsoleClient()
    if client_type == "json":
        return JSONClient(config.json_path)
    if client_type == "http":
        host = config.host
        if not host:
            internal_logger.warning("HUD_HOST is not set")
            raise HudClientException("HUD_HOST is not set")
        if is_async:
            return AsyncHttpClient(host, user_identity)
        return SyncHttpClient(host, user_identity)
    raise HudClientException("Unknown client type: {}".format(client_type))
