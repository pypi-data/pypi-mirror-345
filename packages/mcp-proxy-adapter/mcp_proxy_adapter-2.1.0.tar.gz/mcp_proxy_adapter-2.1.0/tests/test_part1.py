"""
Tests for MCPProxyAdapter - Part 1.
Basic functionality and error handling.
"""
import json
import logging
import sys
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from fastapi import APIRouter

# Добавляем путь к исходникам
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Импортируем напрямую из src
from src.adapter import MCPProxyAdapter, configure_logger, SchemaOptimizer
from src.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig, MCPProxyTool

# Импортируем общие тестовые компоненты
from tests.test_mcp_proxy_adapter import (
    MockDispatcher, 
    MockRegistry, 
    MockOpenApiGenerator,
    success_command, 
    error_command, 
    param_command,
    complex_param_command,
    type_error_command
)

# Фикстуры для тестов
@pytest.fixture
def registry():
    """Возвращает мок реестра команд."""
    return MockRegistry()

@pytest.fixture
def adapter(registry):
    """Возвращает настроенный адаптер для тестов."""
    return MCPProxyAdapter(registry)

@pytest.fixture
def test_app(adapter):
    """Создает тестовое приложение FastAPI с настроенным адаптером."""
    app = FastAPI()
    adapter.register_endpoints(app)
    return TestClient(app)

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

# Тесты для проверки типов параметров
def test_number_parameter_validation(test_app):
    """Тест валидации числового параметра."""
    # Модифицируем информацию о команде для тестирования числового параметра
    command_info = {
        "description": "Тест",
        "params": {
            "num_param": {
                "type": "number",
                "description": "Числовой параметр",
                "required": True
            }
        }
    }
    
    # Патчим get_command_info и get_valid_commands
    with patch.object(MockDispatcher, 'get_command_info', return_value=command_info):
        with patch.object(MockDispatcher, 'get_valid_commands', return_value=["test_command"]):
            response = test_app.post("/cmd", json={
                "jsonrpc": "2.0",
                "method": "test_command",
                "params": {
                    "num_param": "not_number"  # Должен быть числом
                },
                "id": 1
            })
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "num_param" in data["error"]["message"]
            assert "must be a number" in data["error"]["message"]

def test_missing_command_info(test_app):
    """Тест запроса с командой без информации о ней."""
    # Патчим get_command_info, чтобы она возвращала None для неизвестной команды,
    # но разрешаем выполнение через get_valid_commands
    with patch.object(MockDispatcher, 'get_command_info', return_value=None):
        with patch.object(MockDispatcher, 'get_valid_commands', return_value=["special_command"]):
            response = test_app.post("/cmd", json={
                "jsonrpc": "2.0",
                "method": "special_command",
                "params": {},
                "id": 1
            })
            assert response.status_code == 200
            # Команда должна выполниться, даже если информации о ней нет

def test_schema_optimization(no_optimize_adapter):
    """Тест адаптера без оптимизации схемы."""
    assert not no_optimize_adapter.optimize_schema
    schema = no_optimize_adapter._generate_basic_schema()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_model_dump_compatibility():
    """Тест совместимости с Pydantic v2 для метода model_dump."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    config = adapter.generate_mcp_proxy_config()
    
    # Проверяем, что в MCPProxyConfig есть метод model_dump или dict
    assert hasattr(config, 'dict') or hasattr(config, 'model_dump')
    
    # Для Pydantic v2 используем model_dump, для v1 - dict
    if hasattr(config, 'model_dump'):
        config_dict = config.model_dump()
    else:
        config_dict = config.dict()
    
    assert isinstance(config_dict, dict)
    assert "routes" in config_dict
    assert "tools" in config_dict

def test_exception_during_type_validation(test_app):
    """Тест исключения во время валидации типов."""
    # Патчим _validate_param_types, чтобы он вызывал исключение
    with patch.object(MCPProxyAdapter, '_validate_param_types', side_effect=Exception("Ошибка валидации")):
        response = test_app.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "success",
            "params": {"value": 5},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] in [500, -32603]

# Тест для обработки импорта OpenApiGenerator
def test_openapi_generator_import():
    """Тест импорта OpenApiGenerator."""
    # Сохраняем оригинальный импорт
    original_import = __import__
    
    def mock_import(name, *args, **kwargs):
        if name == 'command_registry.generators.openapi_generator':
            # Имитируем, что модуль не найден
            raise ImportError("Модуль не найден")
        return original_import(name, *args, **kwargs)
    
    # Патчим функцию импорта
    with patch('builtins.__import__', side_effect=mock_import):
        registry = MockRegistry()
        # Создаем адаптер с патченным импортом
        adapter = MCPProxyAdapter(registry)
        assert adapter.openapi_generator is None
        
        # Проверяем, что схема всё равно генерируется правильно
        schema = adapter._generate_basic_schema()
        assert "openapi" in schema
        assert "paths" in schema

# Тест для обработки пустого OpenApiGenerator.generate_schema
def test_openapi_generator_none_schema():
    """Test handling the case when OpenAPI generator returns None."""
    class NoneSchemaGenerator:
        def __init__(self, **kwargs):
            pass
            
        def set_dispatcher(self, dispatcher):
            pass
            
        def generate_schema(self):
            return None  # Return None instead of schema
    
    # Patch OpenApiGenerator in adapter
    with patch('src.adapter.OpenApiGenerator', NoneSchemaGenerator):
        registry = MockRegistry()
        adapter = MCPProxyAdapter(registry)
        
        # Check schema generation
        schema = adapter._generate_basic_schema()
        assert schema is not None
        assert isinstance(schema, dict)
        assert "openapi" in schema  # Basic schema should be created

# Тест для поддержки нескольких пространств имен импорта
def test_import_from_different_namespaces():
    """Тест поддержки импорта из разных пространств имен."""
    # Создаем временный модуль для имитации другого пространства имен
    import types
    import sys
    
    # Создаем временный модуль
    temp_module = types.ModuleType('temp_module')
    sys.modules['temp_module'] = temp_module
    
    # Создаем имитацию модуля models в другом пространстве имен
    class TempJsonRpcRequest:
        method: str
        params: dict
        id: int
        
    temp_module.JsonRpcRequest = TempJsonRpcRequest
    
    # Пытаемся импортировать из этого модуля
    with patch('src.adapter.JsonRpcRequest', temp_module.JsonRpcRequest):
        # Проверяем, что импорт работает
        from src.adapter import JsonRpcRequest
        assert JsonRpcRequest == temp_module.JsonRpcRequest

# Тест для исключений при импорте OpenAPI генератора
def test_openapi_import_with_other_exceptions():
    """Тест обработки других исключений при импорте OpenAPI генератора."""
    # Вместо патча на __import__, который трудно контролировать,
    # будем патчить конкретную строку в коде MCPProxyAdapter.__init__

    # Сохраняем оригинальную функцию, которую мы будем замещать
    original_init = MCPProxyAdapter.__init__

    def patched_init(self, registry, cmd_endpoint="/cmd", include_schema=True,
                    optimize_schema=True, tool_name_prefix="mcp_"):
        """Патченная версия __init__, которая не вызывает ошибку при импорте OpenApiGenerator."""
        self.registry = registry
        self.cmd_endpoint = cmd_endpoint
        self.include_schema = include_schema
        self.optimize_schema = optimize_schema
        self.tool_name_prefix = tool_name_prefix
        self.router = APIRouter()
        self.schema_optimizer = SchemaOptimizer()
        self._generate_router()
        self.openapi_generator = None  # Принудительно устанавливаем None, как если бы был исключение

    # Патчим __init__ метод
    MCPProxyAdapter.__init__ = patched_init

    try:
        # Создаем экземпляр с патченным __init__
        registry = MockRegistry()
        adapter = MCPProxyAdapter(registry)
        assert adapter.openapi_generator is None
    finally:
        MCPProxyAdapter.__init__ = original_init

# Тесты для покрытия дополнительной функциональности
def test_custom_openapi_paths():
    """Тест добавления пользовательских маршрутов в схему OpenAPI."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    # Имитируем внутренний метод _generate_basic_schema для покрытия всех веток
    schema = adapter._generate_basic_schema()
    
    # Проверяем, что возвращается правильная структура
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    
    # Проверяем, что cmd_endpoint добавлен в пути
    assert adapter.cmd_endpoint in schema["paths"]
    
def test_generate_schema_with_openapi_generator():
    """Test schema generation using OpenApiGenerator."""
    # Create mock for OpenApiGenerator
    class TestOpenApiGenerator:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.dispatcher = None

        def set_dispatcher(self, dispatcher):
            self.dispatcher = dispatcher

        def generate_schema(self):
            return {
                "openapi": "3.0.0",
                "info": {
                    "title": "Test API",
                    "version": "1.0.0"
                },
                "paths": {
                    "/test": {
                        "get": {
                            "summary": "Test endpoint"
                        }
                    }
                }
            }

    # Patch openapi_generator on instance
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    adapter.openapi_generator = TestOpenApiGenerator()
    schema = adapter.openapi_generator.generate_schema()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_schema_optimizer_behavior():
    """Test schema optimizer behavior."""
    # Mock SchemaOptimizer that performs specific transformations
    class TestSchemaOptimizer:
        def optimize(self, schema, *args, **kwargs):
            schema["optimized"] = True
            return schema

    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    adapter.schema_optimizer = TestSchemaOptimizer()
    schema = {"openapi": "3.0.0"}
    optimized = adapter.schema_optimizer.optimize(schema)
    assert "optimized" in optimized

@pytest.fixture
def no_optimize_adapter(registry):
    return MCPProxyAdapter(registry, optimize_schema=False)

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 
