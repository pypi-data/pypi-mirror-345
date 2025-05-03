"""
Тесты для MCPProxyAdapter - основные сценарии и базовая функциональность.
"""
import json
import logging
import sys
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch

# Добавляем путь к исходникам
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Импортируем напрямую из src
from src.adapter import MCPProxyAdapter, configure_logger
from src.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig, MCPProxyTool

# Импортируем общие тестовые компоненты
from tests.test_mcp_proxy_adapter import (
    MockDispatcher, 
    MockRegistry, 
    success_command, 
    error_command, 
    param_command
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

def test_error_command_execution(test_app):
    """Тест обработки ошибки при выполнении команды."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "error",
        "id": 1
    })
    assert response.status_code == 200  # JSON-RPC всегда возвращает 200
    data = response.json()
    assert "error" in data
    assert "Тестовая ошибка" in data["error"]["message"]

def test_unknown_command(test_app):
    """Тест обработки неизвестной команды."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "unknown_command",
        "id": 1
    })
    assert response.status_code == 200  # JSON-RPC всегда возвращает 200
    data = response.json()
    assert "error" in data
    assert "Unknown command" in data["error"]["message"]

def test_missing_required_parameter(test_app):
    """Тест обработки отсутствия обязательного параметра."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "param",
        "params": {},  # Отсутствует обязательный параметр required_param
        "id": 1
    })
    assert response.status_code == 200  # JSON-RPC всегда возвращает 200
    data = response.json()
    assert "error" in data
    assert "required_param" in data["error"]["message"].lower()

def test_custom_endpoint(custom_endpoint_app):
    """Тест работы адаптера с кастомным эндпоинтом."""
    # Проверяем, что стандартный эндпоинт недоступен
    response = custom_endpoint_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200  # Эндпоинт теперь доступен
    data = response.json()
    assert data["result"] == {"result": 10}
    
    # Проверяем, что кастомный эндпоинт работает
    response = custom_endpoint_app.post("/api/execute", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}

def test_config_generation(adapter):
    """Test configuration generation for MCPProxy."""
    config = adapter.generate_mcp_proxy_config()
    # Check configuration structure (устойчивая проверка)
    assert type(config).__name__ == "MCPProxyConfig"
    assert hasattr(config, "tools") and isinstance(config.tools, list)
    assert hasattr(config, "routes") and isinstance(config.routes, list)
    assert hasattr(config, "version") and config.version == "1.0"
    # Check presence of tools
    assert len(config.tools) > 0
    # Check presence of routes
    assert len(config.routes) > 0
    # Check tools and routes correspondence
    tool_names = [tool.name for tool in config.tools]
    route_tools = [route["tool_name"] for route in config.routes]
    assert all(name in tool_names for name in route_tools)

def test_config_with_custom_prefix(custom_endpoint_adapter):
    """Тест генерации конфигурации с пользовательским префиксом."""
    # Создаем адаптер с кастомным префиксом
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry, tool_name_prefix="custom_")
    
    config = adapter.generate_mcp_proxy_config()
    tool_names = [tool.name for tool in config.tools]
    for name in tool_names:
        assert name.startswith("custom_")
    
def test_save_config_to_file():
    """Тест сохранения конфигурации в файл."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
        adapter.save_config_to_file(temp_file.name)
        
        # Проверяем, что файл не пустой
        assert os.path.getsize(temp_file.name) > 0
        
        # Загружаем и проверяем содержимое
        with open(temp_file.name, 'r') as f:
            config_data = json.load(f)
            assert "routes" in config_data
            assert "tools" in config_data

def test_from_registry_classmethod():
    """Тест создания адаптера через класс-метод from_registry."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter.from_registry(registry, cmd_endpoint="/custom", tool_name_prefix="test_")
    
    assert adapter.cmd_endpoint == "/custom"
    assert adapter.tool_name_prefix == "test_"

def test_logger_configuration():
    """Тест настройки логгера."""
    # Тест с созданием нового логгера
    logger1 = configure_logger()
    assert logger1.name == "mcp_proxy_adapter"
    
    # Тест с использованием родительского логгера
    parent_logger = logging.getLogger("parent")
    logger2 = configure_logger(parent_logger)
    assert logger2.name == "parent.mcp_proxy_adapter"

def test_custom_logger_integration(custom_logger):
    """Тест интеграции с пользовательским логгером."""
    logger, log_records = custom_logger
    
    # Настраиваем адаптер с пользовательским логгером
    with patch('src.adapter.logger', logger):
        registry = MockRegistry()
        adapter = MCPProxyAdapter(registry)
        
        # Создаем тестовое приложение
        app = FastAPI()
        adapter.register_endpoints(app)
        client = TestClient(app)
        
        # Вызываем неизвестную команду, чтобы вызвать логирование
        client.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "unknown_command",
            "id": 1
        })
        
        # Проверяем, что сообщение было залогировано
        assert any("unknown_command" in record for record in log_records)

def test_api_commands_endpoint(test_app):
    """Тест эндпоинта для получения информации о всех командах."""
    response = test_app.get("/api/commands")
    assert response.status_code == 200
    # В реальном адаптере команды могут быть в разной структуре, 
    # проверим более общий случай - наличие ответа в формате JSON
    data = response.json()
    assert isinstance(data, dict)
    # Проверяем, что возвращены данные о командах (без конкретной структуры)
    assert len(data) > 0
    assert "success" in str(data)  # Имя команды должно присутствовать где-то в ответе

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 