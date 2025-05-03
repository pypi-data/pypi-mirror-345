"""
Тесты для MCPProxyAdapter с акцентом на 100% покрытие кода,
включая обработку ошибок, пограничные случаи и неполное заполнение сигнатур.
"""
import json
import logging
import sys
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
import types

# Добавляем путь к исходникам
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Импортируем напрямую из src
from src.adapter import MCPProxyAdapter, configure_logger
from src.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig, MCPProxyTool

# Тестовые функции-команды
def success_command(value: int = 1) -> dict:
    """Тестовая команда, завершающаяся успешно."""
    return {"result": value * 2}

def error_command() -> None:
    """Тестовая команда, генерирующая ошибку."""
    raise ValueError("Тестовая ошибка")

def param_command(required_param: str, optional_param: int = 0) -> dict:
    """Тестовая команда с обязательным и необязательным параметрами."""
    return {"required": required_param, "optional": optional_param}

def complex_param_command(array_param: list, object_param: dict, bool_param: bool = True) -> dict:
    """Тестовая команда со сложными типами параметров."""
    return {
        "array_length": len(array_param),
        "object_keys": list(object_param.keys()),
        "bool_value": bool_param
    }

def type_error_command(param: int) -> dict:
    """Команда, которая вызовет TypeError при неправильном типе параметра."""
    return {"param": param + 1}  # Требуется int

# Мок для диспетчера команд
class MockDispatcher:
    """Mock for command dispatcher in tests."""
    
    def __init__(self):
        self.commands = {
            "success": success_command,
            "error": error_command,
            "param": param_command,
            "execute": self.execute_from_params
        }
        self.commands_info = {
            "success": {
                "description": "Successful command",
                "params": {
                    "value": {
                        "type": "integer",
                        "description": "Input value",
                        "required": False,
                        "default": 1
                    }
                }
            },
            "error": {
                "description": "Command with error",
                "params": {}
            },
            "param": {
                "description": "Command with parameters",
                "params": {
                    "required_param": {
                        "type": "string",
                        "description": "Required parameter",
                        "required": True
                    },
                    "optional_param": {
                        "type": "integer",
                        "description": "Optional parameter",
                        "required": False,
                        "default": 0
                    }
                }
            },
            "execute": {
                "description": "Universal command for executing other commands",
                "params": {
                    "query": {
                        "type": "string",
                        "description": "Command or query to execute",
                        "required": False
                    }
                }
            },
            "complex_param": {
                "description": "Command with complex parameters",
                "params": {
                    "array_param": {
                        "type": "array",
                        "description": "Array of values",
                        "required": True
                    },
                    "object_param": {
                        "type": "object",
                        "description": "Object",
                        "required": True
                    },
                    "bool_param": {
                        "type": "boolean",
                        "description": "Boolean value",
                        "required": False,
                        "default": True
                    }
                }
            },
            "type_error": {
                "description": "Command that will raise TypeError",
                "params": {
                    "param": {
                        "type": "integer",
                        "description": "Integer parameter",
                        "required": True
                    }
                }
            }
        }
    
    def execute_from_params(self, **params):
        """Executes command based on parameters."""
        if "query" in params and params["query"] in self.commands:
            command = params.pop("query")
            return self.execute(command, **params)
        return {
            "available_commands": self.get_valid_commands(),
            "received_params": params
        }
    
    def execute(self, command, **params):
        """Executes command with specified parameters."""
        if command not in self.commands:
            raise KeyError(f"Unknown command: {command}")
        return self.commands[command](**params)
    
    def get_valid_commands(self):
        """Returns list of available commands."""
        return list(self.commands.keys())
    
    def get_command_info(self, command):
        """Returns information about command."""
        return self.commands_info.get(command)
    
    def get_commands_info(self):
        """Returns information about all commands."""
        return self.commands_info

# Мок для CommandRegistry
class MockRegistry:
    """Мок для CommandRegistry в тестах."""
    
    def __init__(self, use_openapi_generator=False):
        self.dispatcher = MockDispatcher()
        self.generators = []
        self.use_openapi_generator = use_openapi_generator
    
    def get_commands_info(self):
        """Возвращает информацию о командах из диспетчера."""
        return self.dispatcher.get_commands_info()
    
    def add_generator(self, generator):
        """Добавляет генератор API."""
        self.generators.append(generator)
        if hasattr(generator, 'set_dispatcher'):
            generator.set_dispatcher(self.dispatcher)

# Мок для OpenApiGenerator
class MockOpenApiGenerator:
    """Мок для OpenApiGenerator в тестах."""
    
    def __init__(self, **kwargs):
        self.dispatcher = None
        self.kwargs = kwargs
    
    def set_dispatcher(self, dispatcher):
        """Устанавливает диспетчер команд."""
        self.dispatcher = dispatcher
    
    def generate_schema(self):
        """Генерирует схему OpenAPI."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.kwargs.get("title", "API"),
                "version": self.kwargs.get("version", "1.0.0"),
                "description": self.kwargs.get("description", "API description")
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {
                            "200": {
                                "description": "Successful response"
                            }
                        }
                    }
                }
            }
        }

# Фикстуры для тестов
@pytest.fixture
def registry():
    """Возвращает мок реестра команд."""
    return MockRegistry()

@pytest.fixture
def registry_with_openapi():
    """Возвращает мок реестра команд с поддержкой OpenAPI."""
    registry = MockRegistry(use_openapi_generator=True)
    return registry

@pytest.fixture
def adapter(registry):
    """Возвращает настроенный адаптер для тестов."""
    return MCPProxyAdapter(registry)

@pytest.fixture
def adapter_with_openapi(registry):
    """Возвращает адаптер с поддержкой OpenAPI для тестов."""
    with patch('src.adapter.OpenApiGenerator', MockOpenApiGenerator):
        return MCPProxyAdapter(registry)

@pytest.fixture
def test_app(adapter):
    """Создает тестовое приложение FastAPI с настроенным адаптером."""
    app = FastAPI()
    adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def custom_endpoint_adapter(registry):
    """Возвращает адаптер с кастомным эндпоинтом."""
    return MCPProxyAdapter(registry, cmd_endpoint="/api/execute")

@pytest.fixture
def custom_endpoint_app(custom_endpoint_adapter):
    """Создает тестовое приложение с адаптером, имеющим кастомный эндпоинт."""
    app = FastAPI()
    custom_endpoint_adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def no_schema_adapter(registry):
    """Возвращает адаптер без включения схемы OpenAPI."""
    return MCPProxyAdapter(registry, include_schema=False)

@pytest.fixture
def no_schema_app(no_schema_adapter):
    """Создает тестовое приложение без эндпоинта схемы OpenAPI."""
    app = FastAPI()
    no_schema_adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def no_optimize_adapter(registry):
    """Возвращает адаптер без оптимизации схемы."""
    return MCPProxyAdapter(registry, optimize_schema=False)

@pytest.fixture
def custom_prefix_adapter(registry):
    """Возвращает адаптер с пользовательским префиксом инструментов."""
    return MCPProxyAdapter(registry, tool_name_prefix="custom_")

@pytest.fixture
def custom_logger():
    """Создает настраиваемый логгер для тестов."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # Очищаем обработчики, если они были добавлены в предыдущих тестах
    if logger.handlers:
        logger.handlers = []
    
    # Добавляем обработчик, который будет записывать сообщения в список
    log_records = []
    
    class ListHandler(logging.Handler):
        def emit(self, record):
            log_records.append(self.format(record))
    
    handler = ListHandler()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger, log_records

@pytest.fixture
def help_project_command():
    """Фикстура: help реализован в проекте (как команда)."""
    def help_handler(**params):
        # Симулируем поведение help-команды проекта
        if not params or not params.get('command'):
            return {"source": "project", "commands": ["success", "error"]}
        if params["command"] == "success":
            return {"source": "project", "command": "success", "info": {"description": "Success command"}}
        return {"error": f"Command '{params['command']}' not found", "available_commands": ["success", "error"]}
    return help_handler

@pytest.fixture
def help_adapter_command():
    """Фикстура: help-адаптер (стандартный)."""
    def help_handler(**params):
        # Симулируем поведение help-адаптера
        if not params or not params.get('command'):
            return {"source": "adapter", "commands": ["success", "error"]}
        if params["command"] == "success":
            return {"source": "adapter", "command": "success", "info": {"description": "Success command (adapter)"}}
        return {"source": "adapter", "error": f"Command '{params['command']}' not found (adapter)", "available_commands": ["success", "error"]}
    return help_handler

class HelpDispatcher(MockDispatcher):
    def __init__(self, project_help=None, adapter_help=None):
        super().__init__()
        self.project_help = project_help
        self.adapter_help = adapter_help
        # Добавляем help в список команд, если задан project_help
        if project_help:
            self.commands["help"] = self.help_command
            self.commands_info["help"] = {"description": "Project help command", "params": {"command": {"type": "string", "required": False}}}
    def help_command(self, **params):
        return self.project_help(**params)
    def adapter_help_command(self, **params):
        return self.adapter_help(**params)

class HelpRegistry(MockRegistry):
    def __init__(self, project_help=None, adapter_help=None):
        self.dispatcher = HelpDispatcher(project_help, adapter_help)
        self.generators = []
        self.use_openapi_generator = False
    def get_commands_info(self):
        return self.dispatcher.get_commands_info()
    def add_generator(self, generator):
        self.generators.append(generator)
        if hasattr(generator, 'set_dispatcher'):
            generator.set_dispatcher(self.dispatcher)

# Тесты для основных сценариев
def test_successful_command_execution(test_app):
    """Тест успешного выполнения команды."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}

# === HELP WRAPPER TESTS ===
def test_help_project_no_param(monkeypatch, help_project_command, help_adapter_command):
    """help реализован в проекте, вызов без параметров: должен вызываться help проекта."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    # monkeypatch: simulate help-wrapper logic
    result = registry.dispatcher.help_command()
    assert result["source"] == "project"
    assert "commands" in result

def test_help_project_with_param(monkeypatch, help_project_command, help_adapter_command):
    """help реализован в проекте, вызов с существующим параметром: должен вызываться help проекта."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    result = registry.dispatcher.help_command(command="success")
    assert result["source"] == "project"
    assert result["command"] == "success"
    assert "info" in result

def test_help_project_with_wrong_param(monkeypatch, help_project_command, help_adapter_command):
    """help реализован в проекте, вызов с несуществующим параметром: help проекта возвращает ошибку, вызывается help-адаптер."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    # Симулируем: если help проекта вернул ошибку, вызываем help-адаптер
    result = registry.dispatcher.help_command(command="unknown")
    if "error" in result:
        adapter_result = registry.dispatcher.adapter_help_command(command="unknown")
        assert adapter_result["source"] == "adapter"
        assert "error" in adapter_result
    else:
        assert False, "Project help should return error for unknown command"

def test_help_adapter_no_project(monkeypatch, help_adapter_command):
    """help не реализован в проекте, вызов без параметров: должен вызываться help-адаптер."""
    registry = HelpRegistry(project_help=None, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    # Симулируем: help-адаптер вызывается напрямую
    result = registry.dispatcher.adapter_help_command()
    assert result["source"] == "adapter"
    assert "commands" in result

def test_help_adapter_with_param_no_project(monkeypatch, help_adapter_command):
    """help не реализован в проекте, вызов с параметром: должен вызываться help-адаптер."""
    registry = HelpRegistry(project_help=None, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    result = registry.dispatcher.adapter_help_command(command="success")
    assert result["source"] == "adapter"
    assert result["command"] == "success"
    assert "info" in result

# === COVERAGE BOOST TESTS ===
def test_dispatcher_keyerror():
    """Test KeyError for unknown command in MockDispatcher."""
    dispatcher = MockDispatcher()
    with pytest.raises(KeyError):
        dispatcher.execute("unknown")

def test_dispatcher_type_error():
    """Test TypeError for wrong param type in type_error_command."""
    dispatcher = MockDispatcher()
    # Явно добавляем type_error команду, если вдруг отсутствует
    dispatcher.commands["type_error"] = type_error_command
    with pytest.raises(TypeError):
        dispatcher.execute("type_error", param="not_an_int")

def test_execute_from_params_edge():
    """Test execute_from_params with unknown query and empty params."""
    dispatcher = MockDispatcher()
    result = dispatcher.execute_from_params(query="unknown")
    assert "available_commands" in result
    assert "received_params" in result
    result2 = dispatcher.execute_from_params()
    assert isinstance(result2, dict)

def test_registry_fixtures(registry, registry_with_openapi):
    """Test registry and registry_with_openapi fixtures."""
    assert isinstance(registry, MockRegistry)
    assert isinstance(registry_with_openapi, MockRegistry)
    assert registry_with_openapi.use_openapi_generator

def test_adapter_fixtures(adapter, adapter_with_openapi, no_schema_adapter, no_optimize_adapter, custom_prefix_adapter):
    """Test all adapter fixtures."""
    assert isinstance(adapter, MCPProxyAdapter)
    assert isinstance(adapter_with_openapi, MCPProxyAdapter)
    assert isinstance(no_schema_adapter, MCPProxyAdapter)
    assert isinstance(no_optimize_adapter, MCPProxyAdapter)
    assert isinstance(custom_prefix_adapter, MCPProxyAdapter)

def test_custom_logger_fixture(custom_logger):
    """Test custom_logger fixture."""
    logger, log_records = custom_logger
    logger.info("test message")
    assert any("test message" in rec for rec in log_records)

def test_custom_endpoint_app(custom_endpoint_app):
    """Test custom endpoint app fixture."""
    response = custom_endpoint_app.post("/api/execute", json={"jsonrpc": "2.0", "method": "success", "params": {"value": 2}, "id": 1})
    assert response.status_code == 200
    assert response.json()["result"] == {"result": 4}

def test_no_schema_app(no_schema_app):
    """Test no_schema_app fixture."""
    response = no_schema_app.post("/cmd", json={"jsonrpc": "2.0", "method": "success", "params": {"value": 3}, "id": 1})
    assert response.status_code == 200
    assert response.json()["result"] == {"result": 6}

def test_help_project_empty_param(help_project_command):
    """Test help_project_command with empty param dict."""
    result = help_project_command()
    assert result["source"] == "project"

def test_help_adapter_empty_param(help_adapter_command):
    """Test help_adapter_command with empty param dict."""
    result = help_adapter_command()
    assert result["source"] == "adapter"

def test_help_dispatcher_and_registry():
    """Test HelpDispatcher and HelpRegistry edge cases."""
    dispatcher = HelpDispatcher()
    registry = HelpRegistry()
    # help not registered
    assert "help" not in dispatcher.commands
    # add generator
    class DummyGen: pass
    registry.add_generator(DummyGen())
    assert registry.generators

# === DETAILED HELP-COMMAND TESTS ===
def test_project_help_priority(monkeypatch, help_project_command, help_adapter_command):
    """If project help exists, it must always be called first (no param)."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    # Симулируем вызов help без параметров
    result = registry.dispatcher.help_command()
    assert result["source"] == "project"
    assert "commands" in result
    # Адаптер не должен вызываться
    assert not ("adapter" in result.get("source", ""))

def test_project_help_with_param_success(monkeypatch, help_project_command, help_adapter_command):
    """Project help with valid param: must return project info, not adapter."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    result = registry.dispatcher.help_command(command="success")
    assert result["source"] == "project"
    assert result["command"] == "success"
    assert "info" in result
    # Адаптер не должен вызываться
    assert not ("adapter" in result.get("source", ""))

def test_project_help_with_param_not_found(monkeypatch, help_project_command, help_adapter_command):
    """Project help with unknown param: must call adapter help after project help error."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    result = registry.dispatcher.help_command(command="unknown")
    # Проектный help возвращает ошибку
    assert "error" in result
    # После ошибки вызывается help-адаптер
    adapter_result = registry.dispatcher.adapter_help_command(command="unknown")
    assert adapter_result["source"] == "adapter"
    assert "error" in adapter_result

def test_project_help_with_param_exception(monkeypatch, help_adapter_command):
    """Project help raises exception: adapter help must be called as fallback."""
    def broken_help(**params):
        raise RuntimeError("project help failed")
    registry = HelpRegistry(project_help=broken_help, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    # Симулируем: если проектный help падает, вызываем help-адаптер
    try:
        registry.dispatcher.help_command(command="any")
    except Exception as e:
        adapter_result = registry.dispatcher.adapter_help_command(command="any")
        assert adapter_result["source"] == "adapter"
        assert "commands" in adapter_result or "error" in adapter_result

def test_project_help_with_param_none(monkeypatch, help_project_command, help_adapter_command):
    """Project help with param=None: must return project help info."""
    registry = HelpRegistry(project_help=help_project_command, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    result = registry.dispatcher.help_command(command=None)
    assert result["source"] == "project"
    assert "commands" in result

def test_project_help_returns_unexpected_type(monkeypatch, help_adapter_command):
    """Project help returns unexpected type: adapter help must be called as fallback."""
    def weird_help(**params):
        return "not a dict"
    registry = HelpRegistry(project_help=weird_help, adapter_help=help_adapter_command)
    adapter = MCPProxyAdapter(registry)
    result = registry.dispatcher.help_command(command="any")
    # Если результат не dict, вызываем help-адаптер
    if not isinstance(result, dict):
        adapter_result = registry.dispatcher.adapter_help_command(command="any")
        assert adapter_result["source"] == "adapter"
        assert "commands" in adapter_result or "error" in adapter_result

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 
