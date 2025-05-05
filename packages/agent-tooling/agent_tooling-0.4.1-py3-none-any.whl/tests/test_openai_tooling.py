import json
import sys
import warnings
from unittest.mock import patch, MagicMock
import pytest
from agent_tooling import tool, get_tool_schemas, get_tool_function, discover_tools
from agent_tooling.openai_client import OpenAITooling


# ---------------------------------------
# Tool registration and discovery tests
# ---------------------------------------

def test_direct_decorator_registration():
    @tool(tags=["test"])
    def double(x: int) -> int:
        return x * 2

    schemas = get_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "double"

    fn = get_tool_function("double")
    assert fn(3) == 6

def test_dynamic_discovery(tmp_path, monkeypatch):
    pkg = tmp_path / "pkg_agents"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "mymod.py").write_text(
        "from agent_tooling import tool\n"
        "@tool\ndef greet(name: str) -> str:\n"
        "    return 'Hello ' + name\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    if "agent_tooling" in sys.modules:
        del sys.modules["agent_tooling"]

    import importlib
    import agent_tooling
    importlib.import_module("pkg_agents")

    agent_tooling.discover_tools(["pkg_agents"])
    schemas = agent_tooling.get_tool_schemas()
    assert any(s["name"] == "greet" for s in schemas)

def test_openai_client_importable():
    import importlib
    try:
        m = importlib.import_module("agent_tooling.openai_client")
    except ModuleNotFoundError:
        m = importlib.import_module("agent_tooling.openai")
    assert hasattr(m, "OpenAITooling")

# ---------------------------------------
# Tool filtering and execution
# ---------------------------------------

@tool(tags=["alpha"])
def alpha_tool(question: str, messages: list[dict]) -> str:
    return "alpha response"

@tool(tags=["beta"])
def beta_tool(question: str, messages: list[dict]) -> str:
    return "beta response"

@tool(tags=["gamma"])
def gamma_tool(question: str, messages: list[dict]) -> str:
    return "gamma response"

@patch("agent_tooling.openai_client.get_tools")
def test_call_tools_tag_filtering(mock_get_tools, mock_openai_tool_call):
    with mock_openai_tool_call("alpha_tool", {
        "question": "Test Alpha",
        "messages": [{"role": "user", "content": "Test Alpha"}]
    }):
        mock_get_tools.return_value = (
            [{
                "type": "function",
                "function": {
                    "name": "alpha_tool",
                    "description": "Alpha tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "messages": {"type": "array"},
                        },
                        "required": ["question", "messages"],
                    },
                    "return_type": "string",
                }
            }],
            {"alpha_tool": alpha_tool}
        )

        tooling = OpenAITooling(api_key="fake", model="gpt-4o")
        result = tooling.call_tools(messages=[{"role": "user", "content": "Test Alpha"}], tags=["alpha"])
        assert result[0][-1]["content"] == "alpha response"

# ---------------------------------------
# Fallback behavior
# ---------------------------------------

def test_explicit_fallback_used(mock_openai_no_tool_calls):
    fallback = MagicMock(return_value="fallback-response")
    tooling = OpenAITooling(api_key="test", model="gpt-4", fallback_tool=fallback)

    result = tooling.call_tools(messages=[{"role": "user", "content": "Hello"}])
    assert fallback.called
    assert result[0]["content"] == "fallback-response"

def test_streaming_fallback_yields(mock_openai_no_tool_calls):
    def fallback_stream(messages):
        yield {"text": "streamed-fallback"}

    tooling = OpenAITooling(api_key="test", model="gpt-4", fallback_tool=fallback_stream)
    result = list(tooling.call_tools(messages=[{"role": "user", "content": "Hi"}], stream=True))

    assert any("streamed-fallback" in chunk for chunk in result)

@patch("agent_tooling.openai_client.get_tools")
def test_fallback_tag_discovery(mock_get_tools, mock_openai_no_tool_calls):
    fallback_fn = MagicMock(return_value="auto-response")

    mock_get_tools.return_value = (
        [{"type": "function", "function": {
            "name": "auto_fallback", "description": "Auto fallback", "parameters": {}, "return_type": "string"
        }}],
        {"auto_fallback": fallback_fn}
    )

    tooling = OpenAITooling(api_key="test", model="gpt-4")
    result = tooling.call_tools(messages=[{"role": "user", "content": "Yo"}])

    assert fallback_fn.called
    assert result[0]["content"] == "auto-response"

@patch("agent_tooling.openai_client.get_tools")
def test_warn_on_multiple_fallbacks(mock_get_tools, mock_openai_no_tool_calls):
    f1 = MagicMock(return_value="f1 response")
    f2 = MagicMock(return_value="f2 response")

    mock_get_tools.return_value = (
        [
            {"type": "function", "function": {"name": "f1", "description": "", "parameters": {}, "return_type": "string"}},
            {"type": "function", "function": {"name": "f2", "description": "", "parameters": {}, "return_type": "string"}}
        ],
        {"f1": f1, "f2": f2}
    )

    tooling = OpenAITooling(api_key="test", model="gpt-4")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = tooling.call_tools(messages=[{"role": "user", "content": "Hi"}])

        assert f1.called
        assert not f2.called
        assert any("Multiple tools tagged as 'fallback'" in str(warn.message) for warn in w)
        assert result[0]["content"] == "f1 response"

def test_no_fallback_raises(mock_openai_no_tool_calls):
    tooling = OpenAITooling(api_key="test", model="gpt-4")
    with pytest.raises(ValueError, match="No tool calls found"):
        tooling.call_tools(messages=[{"role": "user", "content": "Hi"}])
