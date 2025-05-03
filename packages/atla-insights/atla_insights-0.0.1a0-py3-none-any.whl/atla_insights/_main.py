"""Core functionality for the atla_package."""

import os
from typing import Optional, Sequence

import logfire
from opentelemetry.sdk.trace import SpanProcessor

from ._span_processors import (
    AtlaRootSpanProcessor,
    get_atla_root_span_processor,
    get_atla_span_processor,
)


class AtlaInsights:
    """Atla insights."""

    def __init__(self) -> None:
        """Initialize Atla insights."""
        self._root_span_processor: Optional[AtlaRootSpanProcessor] = None

    def configure(
        self,
        token: str,
        additional_span_processors: Sequence[SpanProcessor] | None = None,
    ) -> None:
        """Configure Atla insights.

        :param token (str): The write access token.
        :param additional_span_processors (Sequence[SpanProcessor] | None): Additional
            span processors. Defaults to `None`.
        """
        additional_span_processors = list(additional_span_processors or [])

        self._root_span_processor = get_atla_root_span_processor()

        span_processors = [
            get_atla_span_processor(token),
            self._root_span_processor,
            *additional_span_processors,
        ]

        logfire.configure(
            additional_span_processors=span_processors,
            console=False,
            environment=os.getenv("_ATLA_ENV", "prod"),
            send_to_logfire=False,
        )

    def mark_success(self) -> None:
        """Mark the root span in the current trace as successful."""
        if self._root_span_processor is None:
            raise ValueError(
                "Cannot mark trace before running the atla `configure` method."
            )
        self._root_span_processor.mark_root(value=1)

    def mark_failure(self) -> None:
        """Mark the root span in the current trace as failed."""
        if self._root_span_processor is None:
            raise ValueError(
                "Cannot mark trace before running the atla `configure` method."
            )
        self._root_span_processor.mark_root(value=0)


_ATLA = AtlaInsights()

configure = _ATLA.configure
mark_success = _ATLA.mark_success
mark_failure = _ATLA.mark_failure
