import sys
import traceback
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterator

from .exporter.manager.errors import ManagerException

if TYPE_CHECKING:
    from types import TracebackType  # noqa: F401
    from typing import Optional, Type, Union  # noqa: F401

original_logging = None
if "logging" in sys.modules:
    original_logging = sys.modules["logging"]
    del sys.modules["logging"]

from logging import (  # noqa: E402
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    Handler,
    Logger,
    LoggerAdapter,
    LogRecord,
    StreamHandler,
    getLogger,
)

if original_logging:
    sys.modules["logging"] = original_logging
else:
    del sys.modules["logging"]

from typing import (  # noqa: E402
    TYPE_CHECKING,
    Any,
    List,  # noqa: F401
    MutableMapping,
    Tuple,
)

from .config import config  # noqa: E402
from .forkable import ForksafeRLock, ForksafeSequence, ForksafeWrapper  # noqa: E402
from .schemas.events import ExceptionInfo, Log  # noqa: E402
from .schemas.requests import Logs  # noqa: E402
from .schemas.schema import JSON  # noqa: E402, F401


class SendToClientHandler(Handler):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self._logs = ForksafeSequence(
            lambda: deque(maxlen=config.logs_queue_size)
        )  # type: ForksafeSequence[deque[LogRecord]]

    def createLock(self) -> None:
        self.lock = ForksafeRLock()  # type: ignore[assignment]

    def get_and_clear_logs(self) -> Logs:
        logs_count = len(self._logs)
        logs = []  # type: List[Log]
        while logs_count > 0:
            logs.append(self._record_to_log_event(self._logs.popleft()))
            logs_count -= 1
        return Logs(logs, datetime.now(timezone.utc))

    @staticmethod
    def _record_to_log_event(log_record: LogRecord) -> "Log":
        try:
            exc = None
            if log_record.exc_info:
                exc_type, exc_value, exc_traceback = log_record.exc_info
                tb_lines = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                exc = ExceptionInfo(
                    name=str(getattr(exc_type, "__name__", "")),
                    value=str(exc_value),
                    stack_trace="".join(tb_lines),
                )

            return Log(
                message=log_record.getMessage(),
                data=getattr(log_record, ExtraDataAdapter.DATA, {}),
                timestamp=log_record.created * 1000,  # time in ms
                level=log_record.levelname,
                pathname=log_record.pathname,
                lineno=log_record.lineno,
                exception=exc,
            )
        except Exception as e:
            return Log(
                message="Failed to serialize log record",
                data={"original_message": log_record.getMessage(), "exception": str(e)},
                timestamp=log_record.created * 1000,  # time in ms
                level="ERROR",
                pathname=log_record.pathname,
                lineno=log_record.lineno,
            )

    def emit(self, record: LogRecord) -> None:
        self._logs.append(record)

    def handleError(self, record: LogRecord) -> None:
        return None


class SafeStreamHandler(StreamHandler):  # type: ignore[type-arg]
    def createLock(self) -> None:
        self.lock = ForksafeRLock()  # type: ignore[assignment]


if TYPE_CHECKING:
    _LoggerAdapter = LoggerAdapter[Logger]
else:
    _LoggerAdapter = LoggerAdapter


class ExtraDataAdapter(_LoggerAdapter):
    DATA = "data"

    def __init__(self, logger: Logger):
        super().__init__(logger, {})
        self.component = None  # type: Optional[str]
        self.stage = None  # type: Optional[str]

    def set_component(self, component: str) -> None:
        self.component = component

    def set_stage(self, stage: str) -> None:
        self.stage = stage

    @contextmanager
    def stage_context(self, stage: str) -> Iterator[None]:
        original_stage = self.stage
        self.set_stage(stage)
        try:
            yield
        finally:
            self.stage = original_stage

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        extra = kwargs.get("extra", {})
        data = kwargs.pop("data", None)

        if data is not None:
            extra[self.DATA] = data  # Add the custom data to extra

        if self.component:
            if not extra.get(self.DATA):
                extra[self.DATA] = {}
            extra[self.DATA]["component"] = self.component

        if self.stage:
            if not extra.get(self.DATA):
                extra[self.DATA] = {}
            extra[self.DATA]["stage"] = self.stage

        kwargs["extra"] = extra
        return msg, kwargs

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]

        _exc_info = (
            sys.exc_info()
        )  # type: Union[Tuple[Type[BaseException], BaseException, TracebackType], Tuple[None, None, None], BaseException | None]
        if isinstance(_exc_info, tuple) and isinstance(_exc_info[1], ManagerException):
            if hasattr(_exc_info[1], "__context__"):
                _exc_info = _exc_info[1].__context__

            if not kwargs.get("data"):
                kwargs["data"] = {}
            kwargs["data"]["manager_exception"] = True

            self.error(msg, exc_info=_exc_info, *args, **kwargs)
            return

        super().exception(msg, *args, **kwargs)


class MainProcessAdapter(_LoggerAdapter):
    def __init__(self, logger: Logger):
        super().__init__(logger, {})
        self.is_main_process = True
        self._had_error = False

    def set_is_main_process(self, is_main_process: bool) -> None:
        self.is_main_process = is_main_process

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        extra = kwargs.get("extra", {})
        extra["postfix"] = (
            "[pid=%(process)d]" if self.is_main_process else "[forked pid=%(process)d]"
        )
        kwargs["extra"] = extra
        return msg, kwargs

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        if level >= ERROR:
            if self._had_error:
                return
            self._had_error = True
        super().log(level, msg, *args, **kwargs)


def init_logging(logger_name: str) -> ExtraDataAdapter:
    logger = getLogger(logger_name)
    logger.handlers = []

    adapter = ExtraDataAdapter(logger)

    logger.propagate = False  # We don't want the internal logs to be propagated to get to the customer's loggers

    logger.setLevel(DEBUG)
    logger.addHandler(send_logs_handler)  # type: ignore[arg-type]

    def get_stream_handler() -> SafeStreamHandler:
        handler = SafeStreamHandler()
        if config.debug_logs:
            handler.setLevel(DEBUG)
        else:
            handler.setLevel(config.log_level)
        FormatterClass = ColorsFormatter if config.pretty_logs else ConsoleFormatter
        handler.setFormatter(
            FormatterClass(
                "{}:%(process)d %(asctime)s.%(msecs)03d [%(levelname)s] %(message)s".format(
                    config.debug_prefix
                ),
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        return handler

    if config.debug_logs or config.verbose_logs:
        logger.addHandler(ForksafeWrapper(get_stream_handler))  # type: ignore[arg-type]
    return adapter


def init_user_logging(logger_name: str) -> MainProcessAdapter:
    user_logger = getLogger(logger_name)
    user_logger.handlers = []
    adapter = MainProcessAdapter(user_logger)

    user_logger.propagate = False
    user_logger.setLevel(INFO)

    def get_stream_handler() -> SafeStreamHandler:
        handler = SafeStreamHandler()
        handler.setLevel(INFO)
        formatter = UserFormatter("Hud: %(message)s %(postfix)s")
        handler.setFormatter(formatter)
        return handler

    user_logger.addHandler(ForksafeWrapper(get_stream_handler))  # type: ignore[arg-type]

    return adapter


class UserFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        if hasattr(record, "postfix"):
            # We want to format the process id inside the postfix
            record.postfix = record.postfix % record.__dict__
        return super().format(record)


class ConsoleFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        data = getattr(record, ExtraDataAdapter.DATA, {})
        component = data.pop("component", None)
        stage = data.pop("stage", None)

        exception_data = record.exc_info
        return "[%s] [%s] %s %s %s" % (
            component,
            stage,
            super().format(record),
            str(data) if data else "",
            exception_data if exception_data else "",
        )


class ColorsFormatter(ConsoleFormatter):
    COLORS = {
        DEBUG: "\033[34m",  # Blue
        INFO: "\033[32m",  # Green
        WARNING: "\033[33m",  # Yellow
        ERROR: "\033[31m",  # Red
        CRITICAL: "\033[41m",  # Red background
    }
    RESET = "\033[0m"  # Reset color code

    def format(self, record: LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        return "%s%s%s" % (color, super().format(record), self.RESET)


def _init_logs_handler() -> SendToClientHandler:
    handler = SendToClientHandler()
    handler.setLevel(config.log_level)
    return handler


send_logs_handler = ForksafeWrapper(_init_logs_handler)
internal_logger = init_logging("{}.internal".format(config.sdk_name))
user_logger = init_user_logging("{}.user".format(config.sdk_name))
