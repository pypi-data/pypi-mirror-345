# MCP Proxy Adapter

## Обзор

MCP Proxy Adapter — это специализированный адаптер для интеграции Command Registry с MCP Proxy (Model Control Protocol Proxy). Он позволяет использовать команды из Command Registry как инструменты (tools) для моделей искусственного интеллекта, предоставляя унифицированный JSON-RPC интерфейс для взаимодействия с командами.

## Основные возможности

- **JSON-RPC интерфейс** для выполнения команд из реестра
- **Автоматическая генерация конфигурации** для MCPProxy
- **Оптимизация OpenAPI схемы** для работы с моделями ИИ
- **Расширенная обработка ошибок** с детальным логированием
- **Валидация типов параметров** для предотвращения ошибок во время выполнения
- **Интеграция с любыми FastAPI приложениями**

## Установка

```bash
pip install mcp-proxy-adapter
```

## Быстрый старт

### Базовая интеграция

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter

# Создаем приложение FastAPI
app = FastAPI()

# Создаем реестр команд
registry = CommandRegistry()

# Регистрируем команды
registry.register_command("search_by_text", search_function, 
                          description="Поиск по текстовому запросу")

# Создаем MCP Proxy адаптер
adapter = MCPProxyAdapter(registry)

# Регистрируем эндпоинты в FastAPI приложении
adapter.register_endpoints(app)

# Сохраняем конфигурацию MCP Proxy в файл
adapter.save_config_to_file("mcp_proxy_config.json")
```

### Работа с внешними логгерами

```python
import logging
from mcp_proxy_adapter.adapter import configure_logger

# Создаем логгер приложения
app_logger = logging.getLogger("my_application")
app_logger.setLevel(logging.DEBUG)

# Настраиваем обработчик для логгера
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app_logger.addHandler(handler)

# Интегрируем логгер приложения с адаптером
adapter_logger = configure_logger(app_logger)

# Теперь все сообщения от адаптера будут проходить через логгер приложения
```

## Архитектура

### Основные компоненты

MCP Proxy Adapter состоит из следующих компонентов:

1. **MCPProxyAdapter** — основной класс, обеспечивающий интеграцию с Command Registry и FastAPI
2. **JsonRpcRequest/JsonRpcResponse** — модели для работы с JSON-RPC запросами и ответами
3. **SchemaOptimizer** — оптимизатор OpenAPI схемы для работы с MCP Proxy
4. **MCPProxyConfig/MCPProxyTool** — модели для формирования конфигурации MCP Proxy

### Технические детали реализации

На основании анализа кода было обнаружено:

1. **Дублирование реализации** — MCPProxyAdapter представлен в двух файлах:
   - `src/adapter.py` (394 строки) — основная реализация адаптера
   - `src/adapters/mcp_proxy_adapter.py` — специализированная версия

2. **Схемы OpenAPI** — значительную часть кодовой базы составляют схемы OpenAPI:
   - `src/openapi_schema/rest_schema.py` (506 строк)
   - `src/openapi_schema/rpc_schema.py` (414 строк)

3. **Цепочки вызовов методов**:
   - `__init__` вызывает `_generate_router` для настройки FastAPI маршрутизатора
   - `save_config_to_file` использует `generate_mcp_proxy_config`
   - `get_openapi_schema` использует `_generate_basic_schema`
   - `execute_command` использует `_validate_param_types` для проверки типов

### Диаграмма взаимодействия

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│    МСР Proxy    │      │  MCPProxyAdapter   │      │ CommandRegistry │
│                 │◄─────┤                    │◄─────┤                 │
└─────────────────┘      └────────────────────┘      └─────────────────┘
        ▲                         ▲                          ▲
        │                         │                          │
        │                ┌────────┴───────┐                  │
        │                │                │                  │
        └────────────────┤  FastAPI App   │──────────────────┘
                         │                │
                         └────────────────┘
```

## API адаптера

### Инициализация

```python
def __init__(
    self, 
    registry: CommandRegistry,
    cmd_endpoint: str = "/cmd",
    include_schema: bool = True,
    optimize_schema: bool = True
)
```

* **registry** — экземпляр CommandRegistry для интеграции
* **cmd_endpoint** — путь для эндпоинта выполнения команд 
* **include_schema** — включить ли генерацию схемы OpenAPI
* **optimize_schema** — оптимизировать ли схему для MCP Proxy

### Основные методы

* **register_endpoints(app: FastAPI)** — регистрирует эндпоинты в приложении FastAPI
* **generate_mcp_proxy_config()** — генерирует конфигурацию для MCP Proxy
* **save_config_to_file(filename: str)** — сохраняет конфигурацию в файл
* **_generate_router()** — внутренний метод для генерации маршрутизатора FastAPI
* **_validate_param_types(command, params)** — проверяет типы параметров перед выполнением команды
* **_generate_basic_schema()** — создает базовую схему OpenAPI при отсутствии генератора
* **_optimize_schema(schema)** — оптимизирует схему OpenAPI для MCP Proxy

## Особенности реализации

Анализ кода показал следующие важные аспекты реализации:

1. **Валидация параметров** происходит в несколько этапов:
   - Сначала проверяется наличие команды в реестре
   - Затем проверяется наличие всех обязательных параметров
   - После этого проверяются типы всех переданных параметров

2. **Обработка ошибок** реализована с помощью обширного механизма try/except, который:
   - Перехватывает специфические исключения (TypeError, KeyError)
   - Обрабатывает общие исключения через блок Exception
   - Форматирует все ошибки в формат JSON-RPC с соответствующими кодами

3. **Оптимизация схемы** включает несколько шагов:
   - Удаление избыточной информации из схемы OpenAPI
   - Добавление JSON-RPC компонентов
   - Подготовка схемы для использования с MCP Proxy

## JSON-RPC протокол

### Формат запроса

```json
{
  "jsonrpc": "2.0",
  "method": "имя_команды",
  "params": {
    "параметр1": "значение1",
    "параметр2": "значение2"
  },
  "id": "идентификатор_запроса"
}
```

### Формат успешного ответа

```json
{
  "jsonrpc": "2.0",
  "result": {
    // Результат выполнения команды
  },
  "id": "идентификатор_запроса"
}
```

### Формат ответа с ошибкой

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Описание ошибки"
  },
  "id": "идентификатор_запроса"
}
```

## Обработка ошибок

Адаптер обрабатывает и логирует следующие типы ошибок:

1. **Несуществующая команда** (-32601) — вызов команды, которая не зарегистрирована в реестре
2. **Отсутствие обязательных параметров** (-32602) — не указаны обязательные параметры команды
3. **Ошибки типов параметров** (-32602) — тип параметра не соответствует ожидаемому
4. **Ошибки при выполнении команды** (-32603) — исключения, возникающие в процессе выполнения
5. **Внутренние ошибки сервера** (-32603) — непредвиденные ошибки в работе адаптера

## Примеры использования

### Интеграция с существующим FastAPI приложением

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter, configure_logger

# Создаем основное приложение
app = FastAPI(title="My Application API")

# Создаем реестр команд
registry = CommandRegistry()

# Регистрируем команды из разных модулей
registry.scan_module("myapp.commands.search")
registry.scan_module("myapp.commands.analytics")

# Настраиваем логгер проекта и интегрируем его с адаптером
logger = logging.getLogger("myapp")
adapter_logger = configure_logger(logger)

# Создаем MCP Proxy адаптер
adapter = MCPProxyAdapter(registry)

# Регистрируем эндпоинты в приложении
adapter.register_endpoints(app)

# Сохраняем конфигурацию для MCP Proxy
adapter.save_config_to_file("config/mcp_proxy_config.json")
```

### Валидация типов параметров

MCP Proxy Adapter автоматически проверяет типы параметров перед выполнением команды:

```python
# Определение команды с типизированными параметрами
def search_documents(query: str, max_results: int = 10, filters: dict = None) -> list:
    """
    Поиск документов по запросу.
    
    Args:
        query: Поисковый запрос
        max_results: Максимальное количество результатов
        filters: Фильтры для уточнения поиска
        
    Returns:
        Список найденных документов
    """
    # Реализация поиска...
    
# Пример JSON-RPC запроса с некорректным типом
# {
#   "jsonrpc": "2.0",
#   "method": "search_documents",
#   "params": {
#     "query": "test query",
#     "max_results": "not_a_number"  # Должно быть числом
#   },
#   "id": 1
# }
#
# Ответ с ошибкой:
# {
#   "jsonrpc": "2.0",
#   "error": {
#     "code": -32602,
#     "message": "Invalid parameter types: Параметр 'max_results' должен быть целым числом"
#   },
#   "id": 1
# }
```

## Тестирование адаптера

Для тестирования MCP Proxy Adapter рекомендуется использовать следующий подход:

```python
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter

# Тестовая команда
def test_command(value: int = 1) -> dict:
    """Тестовая команда."""
    return {"result": value * 2}

@pytest.fixture
def test_app():
    """Создает тестовое приложение с настроенным адаптером."""
    # Создаем реестр команд
    registry = CommandRegistry()
    registry.register_command("test", test_command)
    
    # Создаем адаптер
    adapter = MCPProxyAdapter(registry)
    
    # Создаем приложение FastAPI
    app = FastAPI()
    adapter.register_endpoints(app)
    
    # Возвращаем тестовый клиент
    return TestClient(app)

def test_successful_command_execution(test_app):
    """Тест успешного выполнения команды."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "test",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
```

## Интеграция с MCP Proxy

### Конфигурация MCP Proxy

MCP Proxy Adapter автоматически генерирует конфигурацию для MCP Proxy:

```json
{
  "version": "1.0",
  "tools": [
    {
      "name": "mcp_search_documents",
      "description": "Поиск документов по запросу",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Поисковый запрос"
          },
          "max_results": {
            "type": "integer",
            "description": "Максимальное количество результатов"
          },
          "filters": {
            "type": "object",
            "description": "Фильтры для уточнения поиска"
          }
        },
        "required": ["query"]
      }
    }
  ],
  "routes": [
    {
      "path": "/cmd",
      "type": "json_rpc",
      "method_field": "method",
      "params_field": "params"
    }
  ]
}
```

### Запуск с MCP Proxy

1. Запустите ваше FastAPI приложение с MCPProxyAdapter
2. Запустите MCP Proxy с сгенерированной конфигурацией:
   ```bash
   mcp-proxy --config mcp_proxy_config.json
   ```
3. Настройте модель ИИ для работы с MCP Proxy

## Известные проблемы и ограничения

Анализ кода показал следующие моменты, о которых следует знать:

1. **Дублирование реализации** — адаптер реализован в двух разных файлах, что может привести к несогласованности при обновлениях. Рекомендуется использовать версию из `mcp_proxy_adapter.adapter`.

2. **Большой размер схем** — схемы OpenAPI довольно объемные (более 400 строк), что может повлиять на производительность при обработке большого количества команд.

3. **Ограничения обнаружения типов** — валидация типов работает только с базовыми типами Python и может иметь ограничения при работе со сложными пользовательскими типами.

## Заключение

MCP Proxy Adapter — это мощный инструмент для интеграции Command Registry с моделями искусственного интеллекта через MCP Proxy. Он предоставляет унифицированный JSON-RPC интерфейс, автоматически генерирует конфигурацию для MCP Proxy и обеспечивает надежную обработку ошибок и валидацию параметров. 