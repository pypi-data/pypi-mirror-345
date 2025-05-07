"""OpenTelemetry langchain_openai.embeddings instrumentation."""

import importlib
import importlib.metadata
import inspect
import json
import logging
from collections.abc import Awaitable, Collection
from pathlib import Path
from typing import Callable, TypedDict, TypeVar

from opentelemetry import context as context_api
from opentelemetry.instrumentation.instrumentor import (  # type: ignore[attr-defined]
    BaseInstrumentor,
)
from opentelemetry.instrumentation.utils import _SUPPRESS_INSTRUMENTATION_KEY, unwrap
from opentelemetry.semconv_ai import SpanAttributes
from opentelemetry.trace import SpanKind, Tracer, get_tracer
from opentelemetry.trace.status import Status, StatusCode
from wrapt import wrap_function_wrapper  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

GEN_AI_OPERATION_NAME = "gen_ai.operation.name"


class ToWrapper(TypedDict):
    """Define wrap target."""

    object: str
    method: str
    span_name: str


WRAPPED_METHODS: list[ToWrapper] = json.load((Path(__file__).parent / "sync.json").open())
WRAPPED_ASYNC_METHODS: list[ToWrapper] = json.load((Path(__file__).parent / "async.json").open())


class LangchainOpenAIEmbeddingsInstrumentor(BaseInstrumentor):
    """An instrumentor for Qdrant's client library."""

    def __init__(self, *, capture_input: bool = False) -> None:
        """Constructor."""
        self._capture_input = capture_input
        super().__init__()

    def instrumentation_dependencies(self) -> Collection[str]:  # noqa: D102
        return ("langchain_openai",)

    def _instrument(self, **kwargs) -> None:  # noqa: ANN003
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, importlib.metadata.version(__name__), tracer_provider)
        for wrapped_method in WRAPPED_METHODS:
            wrap_method = wrapped_method.get("method")
            wrap_function_wrapper(
                "langchain_openai",
                f"{wrapped_method['object']}.{wrap_method}",
                _wrap(tracer, wrapped_method, capture_input=self._capture_input),
            )
        for wrapped_method in WRAPPED_ASYNC_METHODS:
            wrap_method = wrapped_method["method"]
            wrap_function_wrapper(
                "langchain_openai",
                f"{wrapped_method['object']}.{wrap_method}",
                _awrap(tracer, wrapped_method, capture_input=self._capture_input),
            )

    def _uninstrument(self, **kwargs: dict) -> None:  # noqa: ARG002
        for wrapped_method in WRAPPED_METHODS + WRAPPED_ASYNC_METHODS:
            unwrap(f"langchain_core.{wrapped_method['object']}", wrapped_method["method"])


def _with_tracer_wrapper(func: Callable) -> Callable:
    """Helper for providing tracer for wrapper functions.

    Args:
        func: target function
    """

    def _with_tracer(tracer: Tracer, to_wrap: ToWrapper, *, capture_input: bool) -> Callable:
        def _wrapper(wrapped: Callable, instance: object, args: tuple, kwargs: dict) -> Callable:
            return func(
                tracer, to_wrap, wrapped, instance, args, kwargs, capture_input=capture_input
            )

        return _wrapper

    return _with_tracer


T = TypeVar("T")


@_with_tracer_wrapper
def _wrap(  # noqa: PLR0913
    tracer: Tracer,
    to_wrap: ToWrapper,
    wrapped: Callable[..., T],
    instance: object,  # noqa: ARG001
    args: tuple,
    kwargs: dict,
    *,
    capture_input: bool,
) -> T:
    """Instruments and calls every function defined in TO_WRAP.

    Args:
        tracer: _description_
        to_wrap: _description_
        wrapped: _description_
        instance: _description_
        args: _description_
        kwargs: _description_
        capture_input: _description_

    Returns:
        _description_
    """
    if context_api.get_value(_SUPPRESS_INSTRUMENTATION_KEY):
        return wrapped(*args, **kwargs)
    sig = inspect.signature(wrapped)
    bound = sig.bind(*args, **kwargs)
    with tracer.start_as_current_span(
        to_wrap["span_name"],
        kind=SpanKind.CLIENT,
        attributes={
            GEN_AI_OPERATION_NAME: "embeddings",
            SpanAttributes.LLM_REQUEST_TYPE: "embedding",
        },
    ) as span:
        if capture_input:
            span.set_attribute(
                SpanAttributes.LLM_PROMPTS, json.dumps(bound.arguments, ensure_ascii=False)
            )
        response = wrapped(**bound.arguments)
        if response:
            span.set_status(Status(StatusCode.OK))
    return response


@_with_tracer_wrapper
async def _awrap(  # noqa: PLR0913
    tracer: Tracer,
    to_wrap: ToWrapper,
    wrapped: Callable[..., Awaitable[T]],
    instance: object,  # noqa: ARG001
    args: tuple,
    kwargs: dict,
    *,
    capture_input: bool,
) -> T:
    """Instruments and calls every function defined in TO_WRAP."""
    if context_api.get_value(_SUPPRESS_INSTRUMENTATION_KEY):
        return await wrapped(*args, **kwargs)
    sig = inspect.signature(wrapped)
    bound = sig.bind(*args, **kwargs)
    with tracer.start_as_current_span(
        to_wrap["span_name"],
        kind=SpanKind.CLIENT,
        attributes={
            GEN_AI_OPERATION_NAME: "embeddings",
            SpanAttributes.LLM_REQUEST_TYPE: "embedding",
        },
    ) as span:
        if capture_input:
            span.set_attribute(
                SpanAttributes.LLM_PROMPTS, json.dumps(bound.arguments, ensure_ascii=False)
            )
        response = await wrapped(**bound.arguments)
        if response:
            span.set_status(Status(StatusCode.OK))
    return response
