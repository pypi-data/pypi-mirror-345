import contextlib
import json
import pytest
from agent_tooling.tool import tool_registry
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def clear_tool_registry():
    """Automatically clears the tool registry before and after every test."""
    tool_registry.clear()
    yield
    tool_registry.clear()

@pytest.fixture
def mock_openai_no_tool_calls():
    """Mocks OpenAI to return a response with no tool_calls."""
    with patch("agent_tooling.openai_client.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = type("obj", (), {
            "choices": [type("choice", (), {
                "message": type("message", (), {"tool_calls": None})
            })]
        })()
        yield mock_openai

@pytest.fixture
def mock_openai_tool_call():
    """Factory that returns a context manager to mock OpenAI tool_call behavior."""
    @contextlib.contextmanager
    def _mock(tool_name: str, arguments: dict):
        with patch("agent_tooling.openai_client.OpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = type("obj", (), {
                "choices": [type("choice", (), {
                    "message": type("message", (), {
                        "tool_calls": [
                            type("tool_call", (), {
                                "function": type("function", (), {
                                    "name": tool_name,
                                    "arguments": json.dumps(arguments)
                                }),
                                "id": "call_id_123"
                            })
                        ]
                    })
                })]
            })()
            yield mock_openai
    return _mock
