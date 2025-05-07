import importlib
from functools import wraps
from typing import Any

from ...config import config
from ...logging import internal_logger
from ..base_instrumentation import BaseInstrumentation


def get_middleware_module() -> str:
    module_path = __name__.rsplit(".", 1)[0]
    return "{}.django_middleware.HudMiddleware".format(module_path)


MIDDLEWARE_MODULE = get_middleware_module()


class DjangoInstrumentation(BaseInstrumentation):
    def __init__(self) -> None:
        super().__init__("django", "django", "2.2.0", None)

    def is_enabled(self) -> bool:
        return config.instrument_django

    def _instrument(self) -> None:
        import django

        if not self._is_middleware_exists():
            internal_logger.error(
                "Couldn't find our middleware module. Skipping instrumentation",
                data={"middleware_module": MIDDLEWARE_MODULE},
            )
            return

        original_setup = django.setup

        @wraps(original_setup)
        def django_setup_wrapper(*args: Any, **kwargs: Any) -> Any:
            from django.conf import settings

            result = original_setup(*args, **kwargs)
            try:
                if MIDDLEWARE_MODULE not in settings.MIDDLEWARE:
                    internal_logger.info(
                        "Adding our middleware module during django.setup"
                    )
                    self._insert_middleware()
                else:
                    internal_logger.info(
                        "Our middleware module already in django.settings during django.setup"
                    )
            except Exception:
                internal_logger.exception(
                    "Failed to add our middleware module during django.setup"
                )
            return result

        django.setup = django_setup_wrapper

    def _insert_middleware(self) -> None:
        from django.conf import settings

        try:
            if isinstance(settings.MIDDLEWARE, tuple):
                settings.MIDDLEWARE = (MIDDLEWARE_MODULE,) + settings.MIDDLEWARE
            elif isinstance(settings.MIDDLEWARE, list):
                settings.MIDDLEWARE.insert(
                    0,
                    MIDDLEWARE_MODULE,
                )
            else:
                internal_logger.error(
                    "Couldn't add our middleware module due to invalid MIDDLEWARE type",
                    data={"middleware_type": type(settings.MIDDLEWARE)},
                )
        except Exception as e:
            internal_logger.error(
                "Couldn't add our middleware module", data={"error": str(e)}
            )

    def _is_middleware_exists(self) -> bool:
        try:
            package_name = MIDDLEWARE_MODULE.rsplit(".", 1)[0]
            class_name = MIDDLEWARE_MODULE.rsplit(".", 1)[1]
            package = importlib.import_module(package_name)
            if not hasattr(package, class_name):
                return False
        except ImportError:
            return False

        return True
