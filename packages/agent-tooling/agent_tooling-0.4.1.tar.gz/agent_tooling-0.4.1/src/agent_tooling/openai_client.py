import json
import warnings
from openai import OpenAI
from typing import Any, Dict, List, Tuple, Generator, Union, Callable, Optional
from .tool import get_tool_schemas, get_tool_function

def get_tools(tags: list[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Callable]]:
    """OpenAI tool schema wrapper with optional tag filtering."""
    functions = get_tool_schemas()
    tools = []
    available_functions = {}

    for function in functions:
        function_tags = function.get("tags", [])
        if tags and not any(tag in function_tags for tag in tags):
            continue

        tools.append({
            "type": "function",
            "function": {
                "name": function["name"],
                "description": function["description"],
                "parameters": function["parameters"],
                "return_type": function.get("return_type", "string"),
            },
        })

        func_name = function["name"]
        available_functions[func_name] = get_tool_function(func_name)

    return tools, available_functions


class OpenAITooling:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        tool_choice: str = "auto",
        fallback_tool: Optional[Callable[[List[dict]], Union[str, Generator]]] = None
    ):
        """
        :param api_key: Your OpenAI API key.
        :param model: Model to use (e.g., 'gpt-4').
        :param tool_choice: OpenAI `tool_choice` option ('auto', specific tool name, or 'none').
        :param fallback_tool: Optional function to call when no tools match. Should accept `messages` and return a string or generator.
        """
        self.api_key = api_key
        self.model = model
        self.tool_choice = tool_choice
        self.fallback_tool = fallback_tool
        self._discovered_fallback: Optional[Callable] = None  # auto-discovered if needed

    def call_tools(
        self,
        messages: List[dict],
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        tool_choice: str = "auto",
        tags: Optional[List[str]] = None,
        stream: bool = False
    ) -> Union[List[dict], Generator[str, None, None]]:
        """
        Unified method for invoking tools.

        :param messages: Chat message history (dicts with 'role' and 'content').
        :param api_key: Override API key (defaults to instance key).
        :param model: Override model name.
        :param tool_choice: OpenAI tool_choice value.
        :param tags: Filter tool list by tags.
        :param stream: If True, yields results as a generator.
        :return: List of messages or streaming generator of responses.
        """
        if stream:
            return self._call_tools_streaming(messages, api_key, model, tool_choice, tags)
        else:
            return self._call_tools(messages, api_key, model, tool_choice, tags)


    def _resolve_fallback_tool(self) -> Optional[Callable]:
        """Returns fallback tool: either user-defined or auto-discovered via `tags=["fallback"]`."""
        if self.fallback_tool:
            return self.fallback_tool

        if self._discovered_fallback:
            return self._discovered_fallback

        tools, available_functions = get_tools(tags=["fallback"])

        if available_functions:
            if len(available_functions) > 1:
                warnings.warn(
                    f"Multiple tools tagged as 'fallback' were found: "
                    f"{', '.join(available_functions.keys())}. Using the first one.",
                    UserWarning
                )
            self._discovered_fallback = next(iter(available_functions.values()))
            return self._discovered_fallback

        return None

    def _call_tools(
        self,
        messages: List[dict],
        api_key: Optional[str],
        model: Optional[str],
        tool_choice: str,
        tags: Optional[List[str]]
    ) -> List[dict]:
        """Non-streaming: returns list of results."""

        api_key = api_key or self.api_key
        model = model or self.model
        client = OpenAI(api_key=api_key)

        tools, available_functions = get_tools(tags=tags)

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )

        response = completion.choices[0].message
        tool_calls = response.tool_calls

        if not tool_calls:
            fallback = self._resolve_fallback_tool()
            if fallback:
                result = fallback(messages=messages)
                if isinstance(result, Generator):
                    return list(result)
                return [{
                    "role": "function",
                    "name": getattr(fallback, '__name__', 'fallback_tool'),
                    "content": result
                }]
            else:
                raise ValueError("No tool calls found, and no fallback tool available.")

        results = []
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            function_to_call = available_functions[name]
            args.pop("messages", None)

            result = function_to_call(**args, messages=messages)
            if isinstance(result, Generator):
                results.extend(list(result))
            else:
                messages.append({
                    "role": "function",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result
                })
                results.append(messages)

        return results

    def _call_tools_streaming(
        self,
        messages: List[dict],
        api_key: Optional[str],
        model: Optional[str],
        tool_choice: str,
        tags: Optional[List[str]]
    ) -> Generator[str, None, None]:
        """Streaming: yields partial results as Server-Sent Events (SSE)."""

        api_key = api_key or self.api_key
        model = model or self.model
        client = OpenAI(api_key=api_key)

        tools, available_functions = get_tools(tags=tags)

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )

        response = completion.choices[0].message
        tool_calls = response.tool_calls

        if not tool_calls:
            fallback = self._resolve_fallback_tool()
            if fallback:
                result = fallback(messages=messages)
                if isinstance(result, Generator):
                    for item in result:
                        yield f"data: {json.dumps(item)}\n\n"
                else:
                    yield f"data: {json.dumps({'response': result})}\n\n"
            else:
                yield f"data: {json.dumps({'error': 'No tool calls found, and no fallback tool available.'})}\n\n"
            return

        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            function_to_call = available_functions[name]
            args.pop("messages", None)

            result = function_to_call(**args, messages=messages)
            if isinstance(result, Generator):
                for item in result:
                    yield f"data: {json.dumps(item)}\n\n" if not isinstance(item, str) else \
                          (f"data: {item}\n\n" if item.startswith("{") else f"data: {json.dumps({'response': item})}\n\n")
            else:
                yield f"data: {json.dumps({'response': result})}\n\n"
