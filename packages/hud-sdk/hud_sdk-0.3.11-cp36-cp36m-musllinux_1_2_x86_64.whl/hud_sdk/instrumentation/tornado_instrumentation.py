import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Union

from ..config import config
from ..endpoint_manager import EndpointManager
from ..flow_metrics import EndpointMetric
from ..format_utils import strip_regex
from ..logging import internal_logger
from ..native import (
    set_flow_id,
)
from ..utils import mark_linked_function
from .base_instrumentation import BaseInstrumentation

URLMapping = NamedTuple(
    "URLMapping",
    [("path", str), ("handler", Any), ("methods", Set[Tuple[str, Callable[..., Any]]])],
)


class NoEndpointWarning(Exception):
    pass


class TornadoInstrumentation(BaseInstrumentation):
    def __init__(self) -> None:
        super().__init__("tornado", "tornado", "4.5", "6.4.2")
        self.base_request_handler_methods = {}  # type: Dict[str, Any]
        self.handler_to_url_path = {}  # type: Dict[Any, List[str]]
        self.endpoint_manager = EndpointManager()

    def is_enabled(self) -> bool:
        return config.instrument_tornado

    def _instrument(self) -> None:
        from tornado.web import Application, RequestHandler

        original_application_init = Application.__init__
        original_application_add_handler = Application.add_handlers
        original_requestHandler_init = RequestHandler.__init__

        @wraps(original_application_init)
        def _application_init_wrapper(
            self_: Any, handlers: List[Any], *args: Any, **kwargs: Any
        ) -> Any:
            internal_logger.debug("Instrumenting tornado application init")
            application_init_result = original_application_init(
                self_, handlers, *args, **kwargs
            )
            try:
                url_mappings = self._extract_url_mappings(handlers)
                self._save_url_mappings_to_endpoints(url_mappings)
            except Exception:
                internal_logger.exception(
                    "An error occurred in extracting and saving URL mappings to endpoints during application init"
                )
            return application_init_result

        @wraps(original_application_add_handler)
        def _application_add_handler_wrapper(
            self_: Any, host_pattern: Any, host_handlers: List[Any]
        ) -> Any:
            internal_logger.debug("Instrumenting tornado application add handler")
            add_handler_result = original_application_add_handler(
                self_, host_pattern, host_handlers
            )
            try:
                url_mappings = self._extract_url_mappings(host_handlers)
                self._save_url_mappings_to_endpoints(url_mappings)
            except Exception:
                internal_logger.exception(
                    "An error occurred in extracting and saving URL mappings to endpoints during application add handler"
                )
            return add_handler_result

        @wraps(original_requestHandler_init)
        def _requestHandler_init_wrapper(self_: Any, *args: Any, **kwargs: Any) -> Any:
            init_result = original_requestHandler_init(self_, *args, **kwargs)
            if getattr(self_, "_HUD_wrapped", False):
                internal_logger.debug("already instrumented the request handler init")
                return init_result

            internal_logger.debug("Instrumenting tornado request handler init")
            setattr(self_, "_HUD_wrapped", True)

            original_prepare = self_.prepare
            original_on_finish = self_.on_finish

            metric = None

            @wraps(original_prepare)
            def _prepare_wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                This function is called before each request.
                """
                internal_logger.debug("Instrumenting tornado request handler prepare")
                try:
                    current_endpoint = self_.request.uri
                    current_method = self_.request.method
                    current_flow_id = self._get_matching_flow_id(
                        type(self_), current_method
                    )
                    if current_flow_id is None:
                        internal_logger.warning(
                            "Endpoint not found",
                            data={
                                "endpoint": current_endpoint,
                                "method": current_method,
                            },
                        )
                        raise NoEndpointWarning("Endpoint not found")

                    set_flow_id(current_flow_id)
                    nonlocal metric
                    metric = EndpointMetric(current_flow_id)

                    if metric is not None:
                        metric.set_request_attributes(current_endpoint, current_method)
                        metric.start()
                    else:
                        internal_logger.warning(
                            "Metric not initialized for the current request",
                            data={"current_flow_id": current_flow_id},
                        )
                except NoEndpointWarning:
                    pass
                except Exception:
                    internal_logger.exception(
                        "An error occurred during prepare instrumentation"
                    )

                return original_prepare(*args, **kwargs)

            @wraps(original_on_finish)
            def _on_finish_wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                This function is called after each request.
                """
                internal_logger.debug("Instrumenting tornado request handler on_finish")
                on_finish_result = original_on_finish(*args, **kwargs)

                try:
                    nonlocal metric
                    if metric is not None:
                        metric.stop()
                        metric.set_response_attributes(self_.get_status())
                        metric.save()
                    else:
                        internal_logger.debug("Metric is None")

                    set_flow_id(None)
                except Exception:
                    internal_logger.exception(
                        "An error occurred in setting the flow_id to None and stopping the metric"
                    )

                return on_finish_result

            self_.prepare = _prepare_wrapper
            self_.on_finish = _on_finish_wrapper

            return init_result

        Application.__init__ = _application_init_wrapper  # type: ignore[method-assign, assignment]
        Application.add_handlers = _application_add_handler_wrapper  # type: ignore[method-assign, assignment]
        RequestHandler.__init__ = _requestHandler_init_wrapper  # type: ignore[method-assign, assignment]

    def _extract_url_mappings(self, rule_handlers: List[Any]) -> List[URLMapping]:
        from tornado.routing import PathMatches, Rule
        from tornado.web import RequestHandler

        self.base_request_handler_methods = self.get_request_handler_methods(
            RequestHandler
        )

        def traverse_rules(
            rules_list: List[Any],
            url_mappings: Optional[List[URLMapping]] = None,
        ) -> List[URLMapping]:
            if url_mappings is None:
                url_mappings = []
            if not rules_list:
                return url_mappings

            for rule in rules_list:
                if isinstance(rule, Rule):
                    if isinstance(rule.matcher, PathMatches):
                        url_mappings.append(
                            self._create_url_mapping(rule.matcher.regex, rule.target)
                        )
                    else:
                        internal_logger.warning(
                            "Unknown rule matcher type",
                            data={"matcher_type": type(rule.matcher)},
                        )
                elif isinstance(rule, tuple) and len(rule) >= 2:
                    rule_path, sub_rule_handler = rule[:2]
                    if isinstance(rule_path, PathMatches):
                        url_mappings.append(
                            self._create_url_mapping(rule_path.regex, sub_rule_handler)
                        )
                    elif isinstance(rule_path, str):
                        if isinstance(sub_rule_handler, list):
                            internal_logger.warning(
                                "Sub rule handler type list is not supported"
                            )
                        else:
                            url_mappings.append(
                                self._create_url_mapping(rule_path, sub_rule_handler)
                            )
                    else:
                        internal_logger.warning(
                            "Unknown rule_path type",
                            data={"rule_path_type": type(rule_path)},
                        )
                else:
                    internal_logger.warning(
                        "Unknown rule type", data={"rule_type": type(rule)}
                    )

            return url_mappings

        return traverse_rules(rule_handlers)

    def _save_url_mappings_to_endpoints(self, url_mappings: List[URLMapping]) -> None:
        internal_logger.debug(
            "Saving Tornado URL mappings to endpoints",
            data={"url_mappings": url_mappings},
        )
        count = 0
        for url_mapping in url_mappings:
            count += 1
            if url_mapping.handler in self.handler_to_url_path:
                self.handler_to_url_path[url_mapping.handler].append(url_mapping.path)
            else:
                self.handler_to_url_path[url_mapping.handler] = [url_mapping.path]
            for method_name, method_function in url_mapping.methods:
                self.endpoint_manager.save_endpoint_declaration(
                    path=url_mapping.path,
                    methods=[method_name],
                    framework=self.module_name,
                )
                mark_linked_function(method_function)
        internal_logger.info(
            "Extracted Tornado endpoints",
            data={"count": count},
        )

    def _create_url_mapping(self, pattern: Union[Any, str], handler: Any) -> URLMapping:
        pattern = self._get_pattern_path(pattern)
        current_handler_methods = self.get_request_handler_methods(handler)
        implemented_methods = self.get_implemented_handler_methods(
            current_handler_methods
        )

        return URLMapping(path=pattern, handler=handler, methods=implemented_methods)

    def _get_pattern_path(self, pattern: Union[str, Any]) -> str:
        pattern_path = str(pattern)
        try:
            if isinstance(pattern, str):
                pattern_path = strip_regex(pattern)
            else:
                pattern_path = strip_regex(pattern.pattern)
        except Exception:
            internal_logger.warning(
                "Unknown pattern type", data={"pattern_type": type(pattern)}
            )

        return pattern_path

    def _get_matching_flow_id(self, handler: Any, method: str) -> Union[str, None]:
        matching_flow_id = None
        matching_endpoint = self._get_matching_endpoint(handler)
        if matching_endpoint is not None:
            matching_flow_id = self.endpoint_manager.get_endpoint_id(
                matching_endpoint, method
            )
        return matching_flow_id

    def _get_matching_endpoint(self, handler: Any) -> Union[str, None]:
        matching_endpoint = None
        if handler in self.handler_to_url_path:
            if len(self.handler_to_url_path[handler]) > 1:
                internal_logger.warning(
                    "Multiple endpoint paths found for the handler",
                    data={
                        "handler": handler,
                        "paths": self.handler_to_url_path[handler],
                    },
                )
            else:
                matching_endpoint = self.handler_to_url_path[handler][0]
        return matching_endpoint

    def get_request_handler_methods(self, handler_cls: Any) -> Dict[str, Any]:
        return {
            name: function
            for name, function in inspect.getmembers(
                handler_cls, predicate=inspect.isfunction
            )
            if name in ("get", "head", "post", "delete", "patch", "put", "options")
        }

    def get_implemented_handler_methods(
        self, current_handler_methods: Dict[str, Any]
    ) -> Set[Tuple[str, Callable[..., Any]]]:
        return set(
            [
                (name, function)
                for name, function in current_handler_methods.items()
                if function is not self.base_request_handler_methods[name]
            ]
        )
