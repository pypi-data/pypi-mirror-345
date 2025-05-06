import json
import time
import os
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timezone, timedelta
from typing import Any, AsyncGenerator, ClassVar, Sequence, Tuple

# Try to import the gemini library.
try:
    from google import genai
    from google.genai import types
    from google.oauth2 import service_account
    from google.auth import default  # noqa: F401
    import google.auth.transport.requests  # noqa: F401
except ImportError:
    raise ImportError(
        "The gemini library is required for the GeminiClient. Pip install something for it idk"
    )

from flexai.llm.client import Client
from flexai.llm.openai import AsyncOpenAI, OpenAIClient
from flexai.message import (
    AIMessage,
    DataBlock,
    ImageBlock,
    Message,
    MessageContent,
    SystemMessage,
    TextBlock,
    ToolCall,
    ToolResult,
    Usage,
)
from flexai.tool import Tool, TYPE_MAP


@dataclass(frozen=True)
class GeminiClient(OpenAIClient):
    """Client for Gemini, using the OpenAI API. To be use as a fallback in case the Gemini API client has any issue."""

    # The API key to use for interacting with the model.
    api_key: InitVar[str] = field(default=os.environ.get("GEMINI_API_KEY", ""))

    # The base URL for the Gemini API.
    base_url: InitVar[str] = field(
        default=os.environ.get(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    )

    def __post_init__(self, api_key, base_url, **kwargs):
        object.__setattr__(
            self, "client", AsyncOpenAI(api_key=api_key, base_url=base_url)
        )

    # The model to use for the client.
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-03-25")


def get_tool_call(function_call) -> ToolCall:
    return ToolCall(
        id=function_call.id,
        name=function_call.name,
        input=function_call.args,
    )


@dataclass(frozen=True)
class NewGeminiClient(Client):
    """Client for the Gemini API."""

    # The API key to use for interacting with the model.
    api_key: InitVar[str] = field(default=os.environ.get("GEMINI_API_KEY", ""))

    # The client to use for interacting with the model.
    client: genai.Client | None = None

    # The base URL for the Gemini API.
    base_url: InitVar[str] = field(
        default=os.environ.get(
            "GEMINI_BASE_URL",
            "https://www.googleapis.com/auth/generative-language",
        )
    )

    # The model to use for the client.
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-03-25")

    _shared_cache_store: ClassVar[dict[str, Tuple[str, int]]] = {}

    # Instance-level reference to shared cache
    cache_name_store: dict[str, Tuple[str, int]] = field(init=False)

    def __post_init__(self, api_key, base_url, **kwargs):
        use_vertex = kwargs.get("use_vertex", False)
        credential_file_path = kwargs.get("credential_file_path", "")
        if use_vertex:
            scopes = [
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language",
            ]
            if not os.path.exists(credential_file_path):
                raise ValueError(
                    f"The credential path {credential_file_path} does not exist."
                )
            creds = service_account.Credentials.from_service_account_file(
                credential_file_path, scopes=scopes
            )
            object.__setattr__(
                self, "cache_name_store", self.__class__._shared_cache_store
            )
            object.__setattr__(
                self,
                "client",
                genai.Client(vertexai=True, credentials=creds, location="us-central1"),
            )
        else:
            object.__setattr__(
                self,
                "client",
                genai.Client(api_key=api_key),
            )

    @staticmethod
    def format_tool(tool: Tool) -> dict:
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {
                    param[0]: {"type": TYPE_MAP.get(str(param[1]), param[1])}
                    for param in tool.params
                },
            },
        }

    @staticmethod
    def _extract_content_from_part_object(part_object: types.Part):
        value = next(
            ((k, v) for k, v in vars(part_object).items() if v is not None), None
        )
        if not value:
            raise ValueError("Gemini did not respond with any content.")
        if value[0] == "text":
            return TextBlock(
                text=value[1],
            )
        if value[0] == "function_call":
            return get_tool_call(value[1])
        raise ValueError(
            f"Gemini responded with an unsupported content type: {value[0]}"
        )

    @classmethod
    def _format_message_content(
        cls,
        content: str | MessageContent | Sequence[MessageContent],
        name_context: dict = {},
    ):
        if isinstance(content, str):
            return [{"text": content}]

        if isinstance(content, Sequence):
            formatted_contents = [
                cls._format_message_content(item, name_context=name_context)
                for item in content
            ]
            # Just a list flatten. I don't like itertools.chain.from_iterable personally
            formatted_contents = [
                [item] if not isinstance(item, list) else item
                for item in formatted_contents
            ]
            return sum(formatted_contents, [])

        if isinstance(content, ImageBlock):
            return {
                "inlineData": {
                    "mimeType": content.mime_type,
                    "data": content.image,
                }
            }
        if isinstance(content, TextBlock):
            return {
                "text": content.text,
            }
        if isinstance(content, DataBlock):
            return [
                cls._format_message_content(item, name_context=name_context)
                for item in content.into_text_and_image_blocks()
            ]
        if isinstance(content, ToolCall):
            name_context[content.id] = content.name
            return {
                "functionCall": {
                    "id": content.id,
                    "name": content.name,
                    "args": content.input,
                }
            }
        if isinstance(content, ToolResult):
            formatted_result = content.result
            if isinstance(formatted_result, str):
                formatted_result = {
                    "result": formatted_result,
                }
            if not isinstance(formatted_result, dict):
                raise ValueError(
                    f"Expected tool reuslt to be of type str or dict, instead got {type(formatted_result)}"
                )
            if content.tool_call_id not in name_context:
                raise ValueError(
                    f"Tool call {content.tool_call_id} not found in context, but a result for it was found."
                )
            return {
                "functionResponse": {
                    "id": content.tool_call_id,
                    "name": name_context[content.tool_call_id],
                    "response": formatted_result,
                }
            }
        raise ValueError(f"Unsupported content type: {type(content)}")

    def _get_params(
        self,
        messages: list[Message],
        system: str | SystemMessage,
        tools: list[Tool] | None,
        force_tool: bool,
        cache_system: bool,
        disable_thinking: bool,
    ):
        name_context = {}

        formatted_messages = [
            {
                "role": "model" if message.role == "assistant" else "user",
                "parts": self._format_message_content(
                    message.content, name_context=name_context
                ),
            }
            for message in messages
        ]

        if isinstance(system, str):
            system = SystemMessage(content=system)

        formatted_system = json.dumps(
            self._format_message_content(
                system.normalize().content, name_context=name_context
            )
        )

        config_args: dict[str, Any] = {
            "system_instruction": formatted_system,
        }

        if disable_thinking:
            config_args["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        if tools:
            # Create a formatted tool list
            formatted_tool_list = types.Tool(
                function_declarations=[self.format_tool(tool) for tool in tools]  # type: ignore
            )

            # Create a tool config object
            tool_config = None
            if force_tool:
                tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=types.FunctionCallingConfigMode.ANY,
                    ),
                )
            config_args.update(
                {
                    "tools": [formatted_tool_list],
                    "tool_config": tool_config,
                }
            )

        if cache_system:
            config_args = {
                "cached_content": self.get_prompt_cache_name(
                    prompt_text=formatted_system,
                    tools=tools,
                ),
            }

        config = types.GenerateContentConfig(
            **config_args,
        )
        return {
            "model": self.model,
            "contents": formatted_messages,
            "config": config,
        }

    def get_cache_expiration_timestamp(self):
        # For now, default to 1 hour from now
        return datetime.now(timezone.utc) + timedelta(hours=1)

    def get_prompt_cache_name(self, prompt_text: str, tools: list[Tool] | None) -> str:
        if prompt_text in self.cache_name_store:
            cache_name, expiration_ts = self.cache_name_store[prompt_text]
            # See if the cache will exist 1 minute from now, and only if it does use that by name
            if (
                datetime.now(timezone.utc) + timedelta(minutes=1)
            ).timestamp() < expiration_ts:
                return cache_name
        return self.construct_system_and_tool_cache(prompt_text, tools)

    def construct_system_and_tool_cache(
        self,
        system: str | SystemMessage,
        tools: list[Tool] | None,
    ) -> str:
        if not self.client:
            raise ValueError(
                "GeminiClient: Attempting to set a system cache with no client set."
            )
        if isinstance(system, SystemMessage):
            system = json.dumps(
                self._format_message_content(system.normalize().content)
            )
        formatted_tool_list = types.Tool(
            function_declarations=[self.format_tool(tool) for tool in tools]  # type: ignore
        )
        expiration_ts = self.get_cache_expiration_timestamp()
        cache_object = self.client.caches.create(
            model=self.model,
            config=types.CreateCachedContentConfig(
                system_instruction=system,
                tools=[formatted_tool_list],
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=types.FunctionCallingConfigMode.ANY,
                    ),
                ),
                expire_time=expiration_ts,
            ),
        )
        if not cache_object.name:
            raise ValueError("GeminiClient: Failed to create system cache.")
        self.cache_name_store[system] = (
            cache_object.name,
            int(expiration_ts.timestamp()),
        )
        return cache_object.name

    async def get_chat_response(
        self,
        messages: list[Message],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        force_tool: bool = True,
        cache_system: bool = True,
        disable_thinking: bool = False,
        **kwargs,
    ) -> AIMessage:
        if not self.client:
            raise ValueError("GeminiClient is not initialized.")

        params = self._get_params(
            messages=messages,
            system=system,
            tools=tools,
            force_tool=force_tool,
            cache_system=cache_system,
            disable_thinking=disable_thinking,
        )
        start = time.time()
        response_object = self.client.models.generate_content(
            **params,
        )
        usage_metadata = response_object.usage_metadata
        if not usage_metadata:
            raise ValueError("Gemini did not respond with any usage metadata.")
        input_tokens = usage_metadata.prompt_token_count or 0
        output_tokens = (usage_metadata.total_token_count or 0) - input_tokens
        cache_read = usage_metadata.cached_content_token_count or 0
        usage = Usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_tokens=cache_read,
            cache_write_tokens=0,  # Currently not accounted for
            generation_time=time.time() - start,
        )
        try:
            response_content_parts = response_object.candidates[0].content.parts  # type: ignore
            if not response_content_parts:
                raise ValueError("Gemini did not respond with any content.")
            formatted_content_parts = [
                self._extract_content_from_part_object(part)
                for part in response_content_parts
            ]
            return AIMessage(
                content=formatted_content_parts,
                usage=usage,
            )
        except Exception as e:
            return AIMessage(
                content=f"An error occurred while processing the response: {e}",
                usage=usage,
            )

    async def stream_chat_response(  # type: ignore
        self,
        messages: list[Message],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        allow_tool: bool = True,
        force_tool: bool = True,
        cache_system: bool = True,
        disable_thinking: bool = False,
        **kwargs,
    ) -> AsyncGenerator[MessageContent | AIMessage, None]:
        if not self.client:
            raise ValueError("GeminiClient is not initialized.")

        usage = Usage(
            input_tokens=0,
            output_tokens=0,
            cache_read_tokens=0,
            cache_write_tokens=0,
            generation_time=0,
        )
        params = self._get_params(
            messages=messages,
            system=system,
            tools=tools,
            force_tool=force_tool,
            cache_system=cache_system,
            disable_thinking=disable_thinking,
        )
        start = time.time()
        response_object = self.client.models.generate_content_stream(
            **params,
        )
        text_buffer = None
        total_content_list = []

        for chunk in response_object:
            chunk_parts = chunk.candidates[0].content.parts  # type: ignore
            usage_metadata = chunk.usage_metadata
            if not usage_metadata:
                raise ValueError("Gemini did not respond with any usage metadata.")
            input_tokens = usage_metadata.prompt_token_count or 0
            output_tokens = (usage_metadata.total_token_count or 0) - input_tokens
            cache_read = usage_metadata.cached_content_token_count or 0
            usage.input_tokens += input_tokens
            usage.output_tokens += output_tokens
            usage.cache_read_tokens += cache_read
            if isinstance(chunk_parts, list):
                for part in chunk_parts:
                    to_yield = self._extract_content_from_part_object(part)
                    if isinstance(to_yield, TextBlock):
                        if not text_buffer:
                            text_buffer = TextBlock(text="")
                        text_buffer = text_buffer.append(to_yield.text)
                        yield to_yield
                    elif isinstance(to_yield, ToolCall):
                        total_content_list.append(to_yield)
                        yield to_yield

        usage.generation_time = time.time() - start
        if text_buffer:
            total_content_list.append(text_buffer)

        yield AIMessage(
            content=total_content_list,
            usage=usage,
        )
