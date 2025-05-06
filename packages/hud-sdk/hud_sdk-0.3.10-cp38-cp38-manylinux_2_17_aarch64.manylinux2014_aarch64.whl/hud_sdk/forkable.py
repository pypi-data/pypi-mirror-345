__all__ = [
    "ForksafeSequence",
    "ForksafeMapping",
    "ForksafeLock",
    "ForksafeWrapper",
    "ForksafeCM",
]

import os
import typing
from functools import wraps
from threading import Lock, RLock
from typing import (
    Any,
    Callable,
    ContextManager,
    Dict,
    MutableSequence,
    Optional,
    Tuple,
    TypeVar,
    cast,
)


class ForkCallbacks:
    def __init__(self) -> None:
        self.callbacks = []  # type: list[Callable[..., Any]]
        self.resources = []  # type: list[Callable[..., Any]]

    def register_callback(self, func: Callable[..., Any]) -> Callable[..., Any]:
        self.callbacks.append(func)
        return func

    def register_resource(self, func: Callable[..., Any]) -> Callable[..., Any]:
        self.resources.append(func)
        return func

    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        raise NotImplementedError("Use register_callback or register_resource")

    def execute_all(self) -> None:
        try:
            for func in self.resources:
                func()
            for func in self.callbacks:
                func()
        except Exception:
            from .native import set_hud_running_mode
            from .run_mode import HudRunningMode
            from .utils import send_fatal_error

            # TODO: Try to use another identifier, or make key and service global.
            set_hud_running_mode(HudRunningMode.DISABLED)
            send_fatal_error(
                message="Failed to execute fork callbacks"
            )  # Do we want to send fatal here?


before_fork = ForkCallbacks()
after_fork_in_parent = ForkCallbacks()
after_fork_in_child = ForkCallbacks()

did_set = False


def register_fork_callbacks() -> None:
    global did_set
    if did_set:
        return
    did_set = True
    try:
        from .config import config

        if config.run_after_fork:
            return _register_fork_callbacks(
                before_fork.execute_all,
                after_fork_in_parent.execute_all,
                after_fork_in_child.execute_all,
            )

        def _disable_hud_after_fork() -> None:
            from .logging import internal_logger
            from .native import set_hud_running_mode
            from .run_mode import HudRunningMode

            internal_logger.info(
                "Disabling HUD in child process"
            )  # It will print to the console if HUD_DEBUG is set
            set_hud_running_mode(HudRunningMode.DISABLED)
            # We don't clear the memory of main thread like the queue, aggs and logger, because of COW.
            # If we don't touch the memory, that's still "shared", but if we clear it, it copied and actually consomes more memory

        return _register_fork_callbacks(
            lambda: None, lambda: None, _disable_hud_after_fork
        )
    except Exception:
        from .logging import internal_logger

        internal_logger.exception("Failed to register fork callbacks")


def _register_fork_callbacks(
    before: Callable[[], None],
    after_in_parent: Callable[[], None],
    after_in_child: Callable[[], None],
) -> None:
    try:
        import uwsgi

        if getattr(uwsgi, "post_fork_hook", None):
            previous_uwsgi_fork_hook = uwsgi.post_fork_hook

            @wraps(previous_uwsgi_fork_hook)
            def combined_post_fork_hook() -> None:
                after_in_child()
                previous_uwsgi_fork_hook()

            uwsgi.post_fork_hook = combined_post_fork_hook
        else:
            uwsgi.post_fork_hook = after_in_child
        return  # We don't need to register regular fork hooks if we have uwsgi
    except ImportError:
        pass

    if hasattr(os, "register_at_fork"):
        os.register_at_fork(
            before=before,
            after_in_parent=after_in_parent,
            after_in_child=after_in_child,
        )
    else:
        if hasattr(os, "fork"):
            original_fork = os.fork

            @wraps(original_fork)
            def fork(*args: Any, **kwargs: Any) -> int:
                try:
                    before()
                except Exception:
                    pass
                pid = original_fork(*args, **kwargs)
                if pid == 0:
                    try:
                        after_in_child()
                    except Exception:
                        pass
                else:
                    try:
                        after_in_parent()
                    except Exception:
                        pass
                return pid

            os.fork = fork
        if hasattr(os, "forkpty"):
            original_forkpty = os.forkpty

            @wraps(original_forkpty)
            def wrapped_forkpty(*args: Any, **kwargs: Any) -> Tuple[int, int]:
                try:
                    before()
                except Exception:
                    pass
                result = original_forkpty(*args, **kwargs)
                if result[0] == 0:
                    try:
                        after_in_child()
                    except Exception:
                        pass
                else:
                    try:
                        after_in_parent()
                    except Exception:
                        pass
                return result

            os.forkpty = wrapped_forkpty


@before_fork.register_callback
def _before_fork() -> None:
    from .logging import internal_logger

    internal_logger.info("Process is about to fork")


T = TypeVar("T")
W = TypeVar("W")


class ForksafeWrapper(typing.Generic[T]):
    def __init__(self, factory: Callable[[], T]) -> None:
        self.factory = factory
        after_fork_in_child.register_resource(self.reset_wrapped)
        self.reset_wrapped()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.obj, name)

    def get_wrapped(self) -> T:
        return self.obj

    def reset_wrapped(self) -> None:
        self.obj = self.factory()


class ForksafeCM(ForksafeWrapper[ContextManager[T]]):
    def __enter__(self) -> T:
        return self.obj.__enter__()

    def __exit__(self, *args: Any) -> Any:
        return self.obj.__exit__(*args)


class ForksafeSequence(ForksafeWrapper[MutableSequence[T]]):
    def __len__(self) -> int:
        return len(self.obj)

    def __getitem__(self, key: Any) -> Any:
        return self.obj.__getitem__(key)

    def __setitem__(self, key: Any, value: T) -> None:
        self.obj.__setitem__(key, value)


class ForksafeMapping(ForksafeWrapper[Dict[T, W]]):
    def __len__(self) -> int:
        return len(self.obj)

    def __getitem__(self, key: T) -> W:
        return self.obj.__getitem__(key)

    def __setitem__(self, key: T, value: W) -> None:
        self.obj.__setitem__(key, value)


class ForksafeLock(ForksafeCM[bool]):
    def __init__(self) -> None:
        super().__init__(Lock)


class ForksafeRLock(ForksafeCM[bool]):
    def __init__(self) -> None:
        super().__init__(RLock)


class ScopedForksafeResource(ContextManager[T]):
    def __init__(self, object: ContextManager[T]) -> None:
        self.obj: Optional[ContextManager[T]] = object
        after_fork_in_child.register_resource(self.release)

    def __enter__(self) -> T:
        return cast(ContextManager[T], self.obj).__enter__()

    def __exit__(self, *args: Any) -> Any:
        if self.obj is None:
            return
        obj = self.obj
        self.obj = None
        return obj.__exit__(*args)

    def release(self) -> None:
        self.__exit__(None, None, None)
