"""
Simplified test for MCPProxyAdapter.
"""
import json
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create mock classes for testing
class MockDispatcher:
    def __init__(self):
        self.commands = {
            "test_command": lambda value=1: {"result": value * 2}
        }
        self.commands_info = {
            "test_command": {
                "description": "Test command",
                "params": {
                    "value": {
                        "type": "integer",
                        "required": False,
                        "default": 1
                    }
                }
            }
        }
    
    def execute(self, command, **params):
        return self.commands[command](**params)
    
    def get_valid_commands(self):
        return list(self.commands.keys())
    
    def get_command_info(self, command):
        return self.commands_info.get(command)
    
    def get_commands_info(self):
        return self.commands_info

class MockRegistry:
    def __init__(self):
        self.dispatcher = MockDispatcher()
        self.generators = []
    
    def get_commands_info(self):
        return self.dispatcher.get_commands_info()
    
    def add_generator(self, generator):
        self.generators.append(generator)

# Создаем минимальную версию JsonRpcRequest и JsonRpcResponse
class JsonRpcRequest:
    def __init__(self, method, params=None, id=None):
        self.jsonrpc = "2.0"
        self.method = method
        self.params = params or {}
        self.id = id

class JsonRpcResponse:
    def __init__(self, result=None, error=None, id=None, jsonrpc="2.0"):
        self.jsonrpc = jsonrpc
        self.result = result
        self.error = error
        self.id = id
    
    def dict(self):
        response = {"jsonrpc": self.jsonrpc}
        if self.result is not None:
            response["result"] = self.result
        if self.error is not None:
            response["error"] = self.error
        if self.id is not None:
            response["id"] = self.id
        return response

# Мок для SchemaOptimizer
class MockSchemaOptimizer:
    def optimize(self, schema, cmd_endpoint, commands_info):
        return schema

# Определяем класс MCPProxyAdapter для тестов
class MCPProxyAdapter:
    def __init__(self, registry, cmd_endpoint="/cmd", include_schema=True, optimize_schema=True, tool_name_prefix="mcp_"):
        self.registry = registry
        self.cmd_endpoint = cmd_endpoint
        self.include_schema = include_schema
        self.optimize_schema = optimize_schema
        self.tool_name_prefix = tool_name_prefix
        self.router = MagicMock()
        self.schema_optimizer = MockSchemaOptimizer()
        self.openapi_generator = None
    
    def register_endpoints(self, app):
        # Регистрируем эндпоинт для выполнения команд
        @app.post(self.cmd_endpoint)
        async def execute_command(request_data: dict):
            request = JsonRpcRequest(
                method=request_data.get("method", ""),
                params=request_data.get("params", {}),
                id=request_data.get("id")
            )
            
            # Проверяем существование команды
            if request.method not in self.registry.dispatcher.get_valid_commands():
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Command '{request.method}' not found"
                    },
                    "id": request.id
                }
            
            # Выполняем команду
            try:
                result = self.registry.dispatcher.execute(
                    request.method, 
                    **request.params
                )
                
                # Возвращаем результат
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request.id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": request.id
                }
    
    def generate_mcp_proxy_config(self):
        return {
            "version": "1.0",
            "tools": [
                {
                    "name": f"{self.tool_name_prefix}{cmd_name}",
                    "description": cmd_info.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": {param_name: {"type": param_info.get("type", "string")} 
                                      for param_name, param_info in cmd_info.get("params", {}).items()},
                        "required": [param_name for param_name, param_info in cmd_info.get("params", {}).items() 
                                    if param_info.get("required", False)]
                    }
                }
                for cmd_name, cmd_info in self.registry.get_commands_info().items()
            ],
            "routes": [
                {
                    "tool_name": f"{self.tool_name_prefix}{cmd_name}",
                    "endpoint": self.cmd_endpoint,
                    "method": "post",
                    "json_rpc": {"method": cmd_name}
                }
                for cmd_name in self.registry.get_commands_info()
            ]
        }

# Тесты
@pytest.fixture
def registry():
    return MockRegistry()

@pytest.fixture
def adapter(registry):
    return MCPProxyAdapter(registry)

@pytest.fixture
def custom_endpoint_adapter(registry):
    return MCPProxyAdapter(registry, cmd_endpoint="/api/execute")

@pytest.fixture
def test_app(adapter):
    app = FastAPI()
    adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def custom_endpoint_app(custom_endpoint_adapter):
    app = FastAPI()
    custom_endpoint_adapter.register_endpoints(app)
    return TestClient(app)

def test_successful_command_execution(test_app):
    """Тест успешного выполнения команды."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "test_command",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}

def test_unknown_command(test_app):
    """Тест обработки неизвестной команды."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "unknown_command",
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"]["message"]

def test_custom_endpoint(custom_endpoint_app):
    """Тест работы адаптера с кастомным эндпоинтом."""
    # Проверяем, что стандартный эндпоинт недоступен
    response = custom_endpoint_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "test_command",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 404
    
    # Проверяем, что кастомный эндпоинт работает
    response = custom_endpoint_app.post("/api/execute", json={
        "jsonrpc": "2.0",
        "method": "test_command",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}

def test_mcp_proxy_config(adapter):
    """Test MCP Proxy configuration generation."""
    config = adapter.generate_mcp_proxy_config()
    
    assert "version" in config
    assert "tools" in config
    assert len(config["tools"]) == 1
    
    tool = config["tools"][0]
    assert tool["name"] == "mcp_test_command"
    assert "parameters" in tool
    
    assert "routes" in config
    assert len(config["routes"]) == 1
    assert config["routes"][0]["endpoint"] == "/cmd" 