import inspect
import os
import warnings
from pydantic import BaseModel, Field
from functools import wraps

class Agent(BaseModel):
    name: str = Field(..., description="name of the agent")
    description: str = Field(..., description="description of what the agent does")
    file_name: str = Field(..., description="the name of the file without the full path")
    file_path: str = Field(..., description="the name of the file including the full path")
    code: str = Field(..., description="the all of the code in the file for the agent")

    class ConfigDict:
        extra = "forbid"

class ToolRegistry:
    """Manages function metadata and references registration."""

    def __init__(self):
        self.tool_schemas = {}
        self.tool_functions = {}
        self.agents = {}

    def tool(self, tags=None):
        """Decorator factory to register a function as a tool with optional tags."""
        if callable(tags):
            func = tags
            tags = None
            return self.tool(tags)(func)
        def decorator(func):
            print(f"[REGISTER] from {__name__}: {func.__name__}")
            sig = inspect.signature(func)

            param_details = {
                param: {"type": self._get_json_type(sig.parameters[param].annotation)}
                for param in sig.parameters
            }

            return_type = self._get_json_type(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "null"

            self.tool_schemas[func.__name__] = {
                "name": func.__name__,
                "description": func.__doc__ or "No description provided.",
                "parameters": {
                    "type": "object",
                    "properties": param_details,
                    "required": list(param_details.keys())
                },
                "return_type": return_type,
                "tags": tags or []
            }

            frame = inspect.currentframe().f_back
            file_path = frame.f_code.co_filename
            file_name = os.path.basename(file_path)

            # Read the entire content of the file where the function is defined
            with open(file_path, 'r') as file:
                code = file.read()

            self.agents[func.__name__] = {
                "name": func.__name__,
                "description": func.__doc__ or "No description provided.",
                "file_name": file_name,
                "file_path": file_path,
                "code": code,
            }

            # Store the actual function reference
            self.tool_functions[func.__name__] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        
        return decorator

    def get_tool_schemas(self, tags=None):
        """Returns metadata schemas for registered tools, optionally filtered by tags."""
        schemas = list(self.tool_schemas.values())
        if tags is None:
            return schemas
        return [schema for schema in schemas if any(tag in schema.get("tags", []) for tag in tags)]

    def get_tool_function(self, name):
        """Returns the function reference by name."""
        return self.tool_functions.get(name)

    def _get_json_type(self, python_type):
        """Converts Python type annotations to JSON Schema types."""
        type_mapping = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_mapping.get(python_type, "string")  # Default to string if unknown
    
    def get_agents(self):
        """Returns a list of Agent instances for all registered agents."""
        return [Agent(**data) for data in self.agents.values()]
    
    def clear(self):
        """Clears all registered tools and agents."""
        self.tool_schemas.clear()
        self.tool_functions.clear()
        self.agents.clear()


# Create a singleton instance
tool_registry = ToolRegistry()

# Expose functions
tool = tool_registry.tool
get_tool_schemas = tool_registry.get_tool_schemas
get_tool_function = tool_registry.get_tool_function
get_agents = tool_registry.get_agents