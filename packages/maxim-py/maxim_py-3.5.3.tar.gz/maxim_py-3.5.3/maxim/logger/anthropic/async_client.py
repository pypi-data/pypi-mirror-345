import logging
from typing import Any, AsyncGenerator, AsyncIterator, Dict, Iterable, List, Optional, Union, Iterator
from uuid import uuid4

from anthropic import Anthropic, AsyncAnthropic, AsyncMessageStreamManager
from anthropic.types import (
    Message,
    MessageParam,
    MessageStreamEvent
)

from ..logger import (
    Generation,
    GenerationConfig,
    Logger,
    Trace,
    TraceConfig,
)
from .utils import AnthropicUtils
from anthropic import MessageStreamManager  # Add to imports at top


class MaximAnthropicAsyncClient:
    def __init__(self, client: AsyncAnthropic, logger: Logger):
        self._client = client
        self._logger = logger

    async def messages_stream(
        self,
        messages: Iterable[MessageParam],
        system:Optional[str] = None,
        *,
        model: str,
        max_tokens: int,
        trace_id: Optional[str] = None,
        generation_name: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[MessageStreamEvent,None]: #type:ignore
        is_local_trace = trace_id is None
        final_trace_id = trace_id or str(uuid4())
        generation: Optional[Generation] = None
        trace: Optional[Trace] = None
        
        try:
            openai_style_messages = None
            if system is not None:
                openai_style_messages = [{"role": "system", "content": system}] + list(messages)
            trace = self._logger.trace(TraceConfig(id=final_trace_id))
            gen_config = GenerationConfig(
                id=str(uuid4()),
                model=model,
                provider="anthropic",
                name=generation_name,
                model_parameters=AnthropicUtils.get_model_params(
                    max_tokens=max_tokens,
                    **kwargs
                ),
                messages=AnthropicUtils.parse_message_param(
                    openai_style_messages if openai_style_messages is not None else messages  #type:ignore
                ),
            )
            generation = trace.generation(gen_config)
        except Exception as e:
            logging.error(f"Error in generating content: {str(e)}")

        response = self._client.messages.stream(
            **({'system': system} if system is not None else {}),
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            **kwargs
        )

        try:
            if generation is not None:
                async with response as stream:
                    async for event in stream:
                        if event.type == "message_stop":
                            print(event.message)
                            generation.result(event.message)
                            if is_local_trace and trace is not None:
                                trace.end()
                        yield event #type:ignore
            # if is_local_trace and trace is not None:
            #     trace.end()
        except Exception as e:
            logging.error(f"Error in logging generation: {str(e)}")


    async def messages(
        self,
        messages: Iterable[MessageParam],
        system:Optional[str] = None,
        *,
        model: str,
        max_tokens:int,
        trace_id: Optional[str] = None,
        generation_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Message:
        is_local_trace = trace_id is None
        final_trace_id = trace_id or str(uuid4())
        generation: Optional[Generation] = None
        trace: Optional[Trace] = None
        
        try:
            openai_style_messages = None
            if system is not None:
                openai_style_messages = [{"role": "system", "content": system}] + list(messages)
            trace = self._logger.trace(TraceConfig(id=final_trace_id))
            gen_config = GenerationConfig(
                id=str(uuid4()),
                model=model,
                provider="anthropic",
                name=generation_name,
                model_parameters=AnthropicUtils.get_model_params(
                    max_tokens=max_tokens,
                    **kwargs
                ),
                messages=AnthropicUtils.parse_message_param(
                    openai_style_messages if openai_style_messages is not None else messages # type: ignore
                ),
            )
            generation = trace.generation(gen_config)
        except Exception as e:
            logging.error(f"Error in generating content: {str(e)}")

        response = await self._client.messages.create(
            **({'system': system} if system is not None else {}),
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            **kwargs
        )

        try:
            if generation is not None:
                generation.result(response)
            if is_local_trace and trace is not None:
                if response is not None:
                    trace.set_output(str(response.content))
                trace.end()
        except Exception as e:
            logging.error(f"Error in logging generation: {str(e)}")

        return response