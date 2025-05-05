# Agent Tooling

[![PyPI version](https://img.shields.io/pypi/v/agent_tooling.svg)](https://pypi.org/project/agent_tooling/)
[![License](https://img.shields.io/github/license/danielstewart77/agent_tooling.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/agent_tooling.svg)](https://pypi.org/project/agent_tooling/)

A lightweight Python package for registering, discovering, and managing function metadata for OpenAI agents. Includes support for tagging, streaming, auto-discovery, and tool schema generation.

---

## Installation

```bash
pip install agent_tooling
```

## Highlights

* ✅ Register tools with structured metadata and tags
* ✅ Auto-discover tools across packages with `discover_tools()`
* ✅ Generate OpenAI-compatible tool schemas
* ✅ Call tools with OpenAI's API using `OpenAITooling`
* ✅ Supports streaming (SSE-style) and non-streaming responses
* ✅ Expose registered agents and their code metadata

---

## Quick Start

```python
from agent_tooling import tool, get_tool_function, get_tool_schemas

@tool(tags=["math"])
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

schemas = get_tool_schemas()
func = get_tool_function("add")
print(func(5, 3))  # 8
```

---

## Example with OpenAITooling

```python
from agent_tooling import tool, OpenAITooling
import os

@tool(tags=["weather"])
def get_weather(location: str, unit: str = "celsius") -> str:
    """Returns mock weather for a location."""
    return f"The weather in {location} is sunny and 25\u00b0{unit[0].upper()}"

@tool(tags=["finance"])
def calculate_mortgage(principal: float, interest_rate: float, years: int) -> str:
    """Returns estimated monthly mortgage payment."""
    p, r, n = principal, interest_rate / 12, years * 12
    payment = (p * r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return f"Monthly payment: ${payment:.2f}"

openai = OpenAITooling(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
messages = [{"role": "user", "content": "What's the weather in Paris and mortgage for $300,000 at 4.5% for 30 years?"}]

messages = openai.call_tools(messages, tags=["weather", "finance"])
for message in messages:
    if message["role"] == "function":
        print(f"{message['name']} → {message['content']}")
```

---

## API Reference

### `@tool(tags=None)`

Registers a function with introspected JSON schema + optional tags.

### `get_tool_schemas(tags=None)`

Returns OpenAI-compatible tool metadata (filtered by tag if provided).

### `get_tool_function(name)`

Returns function reference by name.

### `get_agents()`

Returns metadata + source code for each registered tool.

### `discover_tools(folders: list[str])`

Recursively imports all modules in specified package folders, auto-registering tools.

---

### `OpenAITooling`

A helper class for integrating OpenAI tool-calling flows.

```python
OpenAITooling(api_key=None, model=None, tool_choice="auto")
```

#### Methods:

* `call_tools(messages, api_key=None, model=None, tool_choice="auto", tags=None)`
* `stream_tools(messages, api_key=None, model=None, tool_choice="auto", tags=None)`

---

## Manual Integration with OpenAI

```python
from openai import OpenAI
from agent_tooling import tool, get_tool_schemas, get_tool_function
import json

@tool(tags=["weather"])
def get_weather(location: str) -> str:
    return f"Weather in {location}: 25°C"

tools, _ = get_tool_schemas(tags=["weather"]), get_tool_function
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto",
)

for call in response.choices[0].message.tool_calls:
    name = call.function.name
    args = json.loads(call.function.arguments)
    func = get_tool_function(name)
    print(func(**args))
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Repo

[https://github.com/danielstewart77/agent\_tooling](https://github.com/danielstewart77/agent_tooling)
