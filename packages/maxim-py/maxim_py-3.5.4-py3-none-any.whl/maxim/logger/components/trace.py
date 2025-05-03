import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict, Union

from typing_extensions import deprecated

from ..parsers import validate_type
from ..writer import LogWriter
from .base import EventEmittingBaseContainer
from .error import Error, ErrorConfig
from .feedback import Feedback, FeedbackDict, get_feedback_dict
from .generation import (
    Generation,
    GenerationConfig,
    GenerationConfigDict,
)
from .retrieval import (
    Retrieval,
    RetrievalConfig,
    RetrievalConfigDict,
    get_retrieval_config_dict,
)
from .tool_call import (
    ToolCall,
    ToolCallConfig,
    ToolCallConfigDict,
    get_tool_call_config_dict,
)
from .types import Entity

if TYPE_CHECKING:
    from .span import Span, SpanConfig, SpanConfigDict  # Type checking only


@deprecated("Use TraceConfigDict instead. This will be removed in a future version.")
@dataclass
class TraceConfig:
    id: str
    name: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    input: Optional[str] = None


class TraceConfigDict(TypedDict, total=False):
    id: str
    name: Optional[str]
    session_id: Optional[str]
    tags: Optional[Dict[str, str]]
    input: Optional[str]


def get_trace_config_dict(
    config: Union[TraceConfig, TraceConfigDict],
) -> TraceConfigDict:
    return (
        TraceConfigDict(
            id=config.id,
            name=config.name,
            session_id=config.session_id,
            tags=config.tags,
            input=config.input,
        )
        if isinstance(config, TraceConfig)
        else config
    )


class Trace(EventEmittingBaseContainer):
    def __init__(self, config: Union[TraceConfig, TraceConfigDict], writer: LogWriter):
        self.output = None
        final_config = get_trace_config_dict(config)
        super().__init__(Entity.TRACE, dict(final_config), writer)
        payload_to_send = {
            **self.data(),
            "sessionId": final_config.get("session_id", None),
        }
        if input_to_send := final_config.get("input", None):
            payload_to_send["input"] = input_to_send
        self._commit("create", payload_to_send)

    def set_input(self, input: str):
        try:
            validate_type(input, str, "input")
        except ValueError:
            logging.error("[MaximSDK] Input must be of type string")
            return
        self._commit("update", {"input": input})

    @staticmethod
    def set_input_(writer: LogWriter, trace_id: str, input: str):
        try:
            validate_type(input, str, "input")
        except ValueError:
            logging.error("[MaximSDK] Input must be of type string")
            return
        Trace._commit_(writer, Entity.TRACE, trace_id, "update", {"input": input})

    def set_output(self, output: str):
        try:
            validate_type(output, str, "output")
        except ValueError:
            logging.error("[MaximSDK] Output must be of type string")
            return
        self.output = output
        self._commit("update", {"output": output})

    @staticmethod
    def set_output_(writer: LogWriter, trace_id: str, output: str):
        try:
            validate_type(output, str, "output")
        except ValueError:
            logging.error("[MaximSDK] Output must be of type string")
            return
        Trace._commit_(writer, Entity.TRACE, trace_id, "update", {"output": output})

    def generation(
        self, config: Union[GenerationConfig, GenerationConfigDict]
    ) -> Generation:
        generation = Generation(config, self.writer)
        self._commit(
            "add-generation",
            {
                **generation.data(),
                "id": generation.id,
            },
        )
        return generation

    def tool_call(self, config: Union[ToolCallConfig, ToolCallConfigDict]) -> ToolCall:
        final_config = get_tool_call_config_dict(config)
        tool_call = ToolCall(final_config, self.writer)
        self._commit(
            "add-tool-call",
            {
                **tool_call.data(),
                "id": tool_call.id,
            },
        )
        return tool_call

    @staticmethod
    def tool_call_(
        writer: LogWriter,
        trace_id: str,
        config: Union[ToolCallConfig, ToolCallConfigDict],
    ) -> ToolCall:
        final_config = get_tool_call_config_dict(config)
        tool_call = ToolCall(final_config, writer)
        Trace._commit_(
            writer,
            Entity.TRACE,
            trace_id,
            "add-tool-call",
            {
                **tool_call.data(),
                "id": tool_call.id,
            },
        )
        return tool_call

    @staticmethod
    def generation_(
        writer: LogWriter,
        trace_id: str,
        config: Union[GenerationConfig, GenerationConfigDict],
    ) -> Generation:
        generation = Generation(config, writer)
        Trace._commit_(
            writer,
            Entity.TRACE,
            trace_id,
            "add-generation",
            {
                **generation.data(),
                "id": generation.id,
            },
        )
        return generation

    def add_error(self, config: ErrorConfig) -> Error:
        error = Error(config, self.writer)
        self._commit("add-error", error.data())
        return error

    @staticmethod
    def error_(writer: LogWriter, trace_id: str, config: ErrorConfig) -> Error:
        error = Error(config, writer)
        Trace._commit_(
            writer,
            Entity.TRACE,
            trace_id,
            "add-error",
            error.data(),
        )
        return error

    def retrieval(self, config: Union[RetrievalConfig, RetrievalConfigDict]):
        final_config = get_retrieval_config_dict(config)
        retrieval = Retrieval(config, self.writer)
        self._commit(
            "add-retrieval",
            {
                "id": final_config.get("id"),
                **retrieval.data(),
            },
        )
        return retrieval

    @staticmethod
    def retrieval_(
        writer: LogWriter,
        trace_id: str,
        config: Union[RetrievalConfig, RetrievalConfigDict],
    ):
        final_config = get_retrieval_config_dict(config)
        retrieval = Retrieval(config, writer)
        Trace._commit_(
            writer,
            Entity.TRACE,
            trace_id,
            "add-retrieval",
            {
                "id": final_config.get("id"),
                **retrieval.data(),
            },
        )
        return retrieval

    def span(self, config: Union["SpanConfig", "SpanConfigDict"]) -> "Span":
        from .span import Span, get_span_config_dict

        final_config = get_span_config_dict(config)
        span = Span(config, self.writer)
        self._commit(
            "add-span",
            {
                "id": final_config.get("id"),
                **span.data(),
            },
        )
        return span

    @staticmethod
    def span_(
        writer: LogWriter,
        trace_id: str,
        config: Union["SpanConfig", "SpanConfigDict"],
    ) -> "Span":
        from .span import Span, get_span_config_dict

        final_config = get_span_config_dict(config)
        span = Span(config, writer)
        Trace._commit_(
            writer,
            Entity.TRACE,
            trace_id,
            "add-span",
            {
                "id": final_config.get("id"),
                **span.data(),
            },
        )

        return span

    def feedback(self, feedback: Union[Feedback, FeedbackDict]):
        self._commit("add-feedback", dict(get_feedback_dict(feedback)))

    @staticmethod
    def feedback_(
        writer: LogWriter, trace_id: str, feedback: Union[Feedback, FeedbackDict]
    ):
        Trace._commit_(
            writer,
            Entity.TRACE,
            trace_id,
            "add-feedback",
            dict(get_feedback_dict(feedback)),
        )

    @staticmethod
    def add_tag_(writer: LogWriter, id: str, key: str, value: str):
        EventEmittingBaseContainer._add_tag_(writer, Entity.TRACE, id, key, value)

    @staticmethod
    def end_(writer: LogWriter, trace_id: str, data: Optional[Dict[str, str]] = None):
        if data is None:
            data = {}
        return EventEmittingBaseContainer._end_(
            writer,
            Entity.TRACE,
            trace_id,
            {
                "endTimestamp": datetime.now(timezone.utc),
                **data,
            },
        )

    @staticmethod
    def event_(
        writer: LogWriter,
        trace_id: str,
        id: str,
        event: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        return EventEmittingBaseContainer._event_(
            writer, Entity.TRACE, trace_id, id, event, tags, metadata
        )

    def data(self) -> Dict[str, Any]:
        return {
            **super().data(),
            "output": self.output,
        }
