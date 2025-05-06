# IMPORTANT: Don't import this file!
import threading
import time
from typing import TYPE_CHECKING, Any

from django.utils.deprecation import MiddlewareMixin

from ...flow_metrics import EndpointMetric
from ...format_utils import format_path_metric, strip_regex
from ...logging import internal_logger
from ...native import set_flow_id
from . import endpoint_manager
from .django_endpoint_extraction import (
    DjangoEndpointExtraction,
    _should_aggregate_patterns,
    convert_pattern_to_string,
)

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse
    from django.urls import ResolverMatch
    from django.views.generic.base import View

ENDPOINT_METRIC_ATTR = "__hud_metric"


class HudMiddleware(MiddlewareMixin):
    def __init__(self, get_response: Any) -> None:
        self.has_extracted_endpoints = threading.Event()
        self.has_started_processing_endpoints = False

        super().__init__(get_response)

    def _extract_endpoint(self, resolver_match: "ResolverMatch") -> str:
        if _should_aggregate_patterns():
            # The last tried path is the one that was matched.
            # Each resolver in the tried list is a pattern that was resolved, so concatenating them gives us the full path.
            matched_resolvers = resolver_match.tried[-1]  # type: ignore[index]
            route = ""
            for resolver in matched_resolvers:
                route += convert_pattern_to_string(resolver.pattern)
            current_endpoint = route
        else:
            current_endpoint = resolver_match.route
        current_endpoint = strip_regex(current_endpoint)
        return current_endpoint

    def process_request(self, request: "HttpRequest") -> None:
        # This code runs at the start of each request

        try:
            metric = EndpointMetric()
            setattr(
                request, ENDPOINT_METRIC_ATTR, metric
            )  # We need the metric object to be available in the process_view method
            metric.start()
            # We set the request attributes here because the process_view method is not called if we get a 404
            path = request.path
            method = request.method
            if path and method:
                metric.set_request_attributes(path, method)
        except Exception:
            internal_logger.exception(
                "An error occurred in setting the request attributes",
                data={
                    "path": format_path_metric(request.path),
                    "method": request.method,
                },
            )

    def process_view(
        self,
        request: "HttpRequest",
        view_func: "View",
        view_args: Any,
        view_kwargs: Any,
    ) -> None:
        # This code runs before the user's function is called.
        # This is needed in order to set the flow_id, which is only available after the URL resolution.
        try:
            if not self.has_started_processing_endpoints:
                start_time = time.time()
                self.has_started_processing_endpoints = True
                internal_logger.info("Received first view, extracting django endpoints")
                from django.urls import get_resolver

                try:
                    DjangoEndpointExtraction().extract_and_save_endpoints(
                        get_resolver().url_patterns
                    )
                except Exception:
                    internal_logger.exception("Error while extracting endpoints")
                finally:
                    internal_logger.info(
                        "Endpoints extraction completed",
                        data={"duration": time.time() - start_time},
                    )
                self.has_extracted_endpoints.set()

            if not self.has_extracted_endpoints.is_set():
                if not self.has_extracted_endpoints.wait(timeout=0.5):
                    internal_logger.warning(
                        "Timeout reached while waiting for endpoint extraction"
                    )
                self.has_extracted_endpoints.set()  # to avoid waiting again
            if not request.resolver_match:
                return None
            current_endpoint = self._extract_endpoint(request.resolver_match)
            current_method = request.method
            if current_endpoint is None or current_method is None:
                internal_logger.warning(
                    "Endpoint or method not found",
                    data={"endpoint": current_endpoint, "method": current_method},
                )
                return None

            current_flow_id = endpoint_manager.get_endpoint_id(
                current_endpoint, current_method
            )
            if current_flow_id is None:
                internal_logger.warning(
                    "Endpoint not found: {} with method: {}".format(
                        current_endpoint, current_method
                    )
                )
                return None

            try:
                set_flow_id(current_flow_id)
            except Exception:
                internal_logger.exception("An error occurred in setting the flow_id")

            metric = getattr(request, ENDPOINT_METRIC_ATTR, None)
            if not metric:
                internal_logger.warning(
                    "Endpoint metric not found",
                    data={"endpoint": current_endpoint, "method": current_method},
                )
                return None

            metric.flow_id = current_flow_id
        except Exception:
            internal_logger.exception(
                "An error occurred in processing the view",
                data={
                    "path": format_path_metric(request.path),
                    "method": request.method,
                },
            )
        finally:
            return None  # We don't want to interrupt the request flow

    def process_response(
        self, request: "HttpRequest", response: "HttpResponse"
    ) -> "HttpResponse":
        # Code to run after the view is called
        try:
            metric = getattr(request, ENDPOINT_METRIC_ATTR, None)
            if metric:
                metric.stop()
                metric.set_response_attributes(response.status_code)
                metric.save()

            try:
                set_flow_id(None)
            except Exception:
                internal_logger.exception(
                    "An error occurred in setting the flow_id to None"
                )
        except Exception:
            internal_logger.exception("An error occurred in saving the metric")
        return response
