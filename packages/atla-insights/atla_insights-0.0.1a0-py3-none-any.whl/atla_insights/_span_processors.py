from typing import Optional

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, _Span
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.util import types

from ._constants import LOGFIRE_OTEL_TRACES_ENDPOINT, SUCCESS_MARK


class AtlaRootSpanProcessor(SpanProcessor):
    """An Atla root span processor."""

    def __init__(self) -> None:
        self._root_span: Optional[_Span] = None

    def on_start(self, span, parent_context) -> None:  # type: ignore
        if span.parent is None:
            self._root_span = span
            self._root_span.set_attribute(SUCCESS_MARK, -1)  # type: ignore

    def on_end(self, span: ReadableSpan) -> None:
        self._root_span = None

    def mark_root(self, value: types.AttributeValue) -> None:
        """Mark the root span in the current trace with a value.

        Args:
            value: The value to mark the root span with.

        Raises:
            ValueError: If the root span is not found or is already marked.
        """
        if self._root_span is None:
            raise ValueError("No root span found in current trace.")
        if self._root_span.attributes is None:
            raise ValueError("Root span attributes are not set.")
        if self._root_span.attributes.get(SUCCESS_MARK) != -1:
            raise ValueError("Cannot mark root span twice.")

        self._root_span.set_attribute(SUCCESS_MARK, value)


def get_atla_span_processor(token: str) -> SpanProcessor:
    """Get an Atla span processor.

    :param token (str): The write access token.
    :return (SpanProcessor): An Atla span processor.
    """
    span_exporter = OTLPSpanExporter(
        endpoint=LOGFIRE_OTEL_TRACES_ENDPOINT,
        headers={"Authorization": f"Bearer {token}"},
    )
    return SimpleSpanProcessor(span_exporter)


def get_atla_root_span_processor() -> AtlaRootSpanProcessor:
    """Get an Atla root span processor.

    :return (AtlaRootSpanProcessor): An Atla root span processor.
    """
    return AtlaRootSpanProcessor()
