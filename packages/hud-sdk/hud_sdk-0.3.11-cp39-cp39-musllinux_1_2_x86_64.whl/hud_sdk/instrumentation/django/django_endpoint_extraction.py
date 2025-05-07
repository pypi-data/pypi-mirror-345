import inspect
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Union,
)

from ...format_utils import strip_regex
from ...logging import internal_logger
from ...utils import mark_linked_function
from . import endpoint_manager

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver

URLMapping = NamedTuple(
    "URLMapping",
    [("path", str), ("view_func", Callable[..., Any]), ("methods", Set[str])],
)


def _should_aggregate_patterns() -> bool:
    from django import VERSION

    return VERSION >= (3, 2)


def convert_pattern_to_string(pattern: Any) -> str:
    from django.urls.resolvers import (
        LocalePrefixPattern,
        RegexPattern,
        RoutePattern,
    )

    should_aggregate = _should_aggregate_patterns()
    if isinstance(pattern, RoutePattern):
        return pattern._route  # type: ignore[attr-defined, no-any-return]
    elif isinstance(pattern, RegexPattern):
        regex_str = pattern._regex  # type: ignore[attr-defined]
        return strip_regex(regex_str)
    elif isinstance(pattern, LocalePrefixPattern):
        if should_aggregate:
            return "/<lang>/"
        else:
            return str(pattern)
    elif should_aggregate:
        try:
            return f"/<{pattern.__class__.__name__}>/"
        except Exception:
            internal_logger.warning(
                "Failed to convert pattern to string", data={"pattern": pattern}
            )
            return str(pattern)
    else:
        return str(pattern)


class DjangoEndpointExtraction:
    def __init__(self) -> None:
        from django.views import View

        self.supported_http_methods = {
            method.upper() for method in View.http_method_names
        }
        self.module_name = "django"

    def extract_and_save_endpoints(self, url_patterns: List[Any]) -> None:
        url_mappings = self._extract_url_mappings(url_patterns)
        for mapping in url_mappings:
            self._save_endpoint(mapping)

    def _save_endpoint(self, mapping: URLMapping) -> None:
        endpoint_manager.save_endpoint_declaration(
            path=mapping.path,
            methods=list(mapping.methods),
            framework=self.module_name,
        )
        mark_linked_function(mapping.view_func)

    def _extract_url_mappings(self, url_patterns: List[Any]) -> List[URLMapping]:
        from django.urls import URLPattern, URLResolver

        def traverse_patterns(
            pattern_list: List[Any],
            accumulated_path: str = "",
            url_mappings: Optional[List[URLMapping]] = None,
        ) -> List[URLMapping]:
            if url_mappings is None:
                url_mappings = []
            if not pattern_list:
                return url_mappings

            for pattern in pattern_list:
                if isinstance(pattern, URLPattern):
                    mappings = self._create_url_mappings(pattern, accumulated_path)
                    url_mappings.extend(mappings)
                elif isinstance(pattern, URLResolver):
                    sub_accumulated = accumulated_path + self._get_pattern_path(pattern)
                    traverse_patterns(
                        pattern.url_patterns, sub_accumulated, url_mappings
                    )
                else:
                    name = getattr(pattern, "__name__", None)
                    if name is None:
                        name = type(pattern).__name__
                    internal_logger.warning(
                        "Unknown pattern type", data={"pattern_name": name}
                    )
            return url_mappings

        return traverse_patterns(url_patterns)

    def _create_url_mappings(
        self, pattern: "URLPattern", accumulated_path: str
    ) -> List[URLMapping]:
        pattern_path = self._get_pattern_path(pattern)
        full_path = accumulated_path + pattern_path

        view = pattern.callback
        if not callable(view):
            internal_logger.warning(
                "View function is not callable for path", data={"path": full_path}
            )
            return []

        method_handlers = self._get_view_method_handlers(view)
        url_mappings = []

        for handler, methods in method_handlers.items():
            url_mappings.append(
                URLMapping(
                    path=full_path,
                    view_func=handler,
                    methods=methods,
                )
            )
        return url_mappings

    def _get_pattern_path(self, pattern: Union["URLPattern", "URLResolver"]) -> str:

        p = pattern.pattern
        return convert_pattern_to_string(p)

    def _get_view_method_handlers(
        self, view: Callable[..., Any]
    ) -> Dict[Callable[..., Any], Set[str]]:
        func_to_methods = defaultdict(set)  # type: Dict[Callable[..., Any], Set[str]]

        if hasattr(view, "view_class"):
            # Class-based view
            view_class = view.view_class
            method_handlers = self._get_method_handlers_from_class(view_class)
            for method_name, handler in method_handlers.items():
                func_to_methods[handler].add(method_name.upper())
        elif inspect.isfunction(view) or inspect.ismethod(view):
            supported_methods = self._get_supported_methods(view)
            func_to_methods[view] = supported_methods
        elif hasattr(view, "__call__"):
            view_class = view.__class__
            method_handlers = self._get_method_handlers_from_class(view_class)
            for method_name, handler in method_handlers.items():
                func_to_methods[handler].add(method_name.upper())
        else:
            internal_logger.warning("Unknown view type", data={"view": view})
            supported_methods = self.supported_http_methods
            func_to_methods[view] = supported_methods

        return func_to_methods

    def _get_supported_methods(self, view: Callable[..., Any]) -> Set[str]:
        if hasattr(view, "__closure__") and view.__closure__:
            # Using @require_http_methods decorator
            for cell in view.__closure__:
                cell_contents = cell.cell_contents
                if isinstance(cell_contents, list) and set(cell_contents).issubset(
                    self.supported_http_methods
                ):
                    # Assuming the decorator passes request_method_list as a list
                    return set(cell_contents)
        return self.supported_http_methods

    def _get_method_handlers_from_class(
        self, view_class: Any
    ) -> Dict[str, Callable[..., Any]]:
        method_handlers = {}
        for method_name in self.supported_http_methods:
            method_name_lower = method_name.lower()
            # Django class methods are in lower case
            if hasattr(view_class, method_name_lower):
                handler = getattr(view_class, method_name_lower)
                if callable(handler):
                    method_handlers[method_name] = handler
                else:
                    internal_logger.warning(
                        "handler is not callable",
                        data={"method_name": method_name, "handler": handler},
                    )
        return method_handlers
