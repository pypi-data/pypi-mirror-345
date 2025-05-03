# MCP Proxy Adapter

Adapter for integrating [Command Registry](docs/README.md) with MCP Proxy, allowing you to use commands as tools for AI models.

## Overview

MCP Proxy Adapter transforms commands registered in the Command Registry into a format compatible with MCP Proxy. This enables:

1. Using existing commands as tools for AI models
2. Creating a hybrid REST/JSON-RPC API for command execution
3. Automatic generation of OpenAPI schemas optimized for MCP Proxy
4. Managing tool metadata for better AI system integration

## Installation

```bash
pip install mcp-proxy-adapter
```

## Quick Start

```python
from mcp_proxy_adapter import MCPProxyAdapter, CommandRegistry
from fastapi import FastAPI

# Create a command registry instance
registry = CommandRegistry()

# Register commands
@registry.command
def calculate_total(prices: list[float], discount: float = 0.0) -> float:
    """
    Calculates the total price with discount.
    Args:
        prices: List of item prices
        discount: Discount percentage (0-100)
    Returns:
        Total price with discount
    """
    subtotal = sum(prices)
    return subtotal * (1 - discount / 100)

# Create FastAPI app
app = FastAPI()

# Create and configure MCP Proxy adapter
adapter = MCPProxyAdapter(registry)

# Register endpoints in FastAPI app
adapter.register_endpoints(app)

# Generate and save MCP Proxy config
adapter.save_config_to_file("mcp_proxy_config.json")
```

## Supported Request Formats

The adapter supports three request formats for command execution:

### 1. JSON-RPC format

```json
{
  "jsonrpc": "2.0",
  "method": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "id": 1
}
```

Example request to `/cmd` endpoint:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "method": "calculate_total",
  "params": {
    "prices": [100, 200, 300],
    "discount": 10
  },
  "id": 1
}' http://localhost:8000/cmd
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": 540.0,
  "id": 1
}
```

### 2. MCP Proxy format

```json
{
  "command": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

Example request:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "command": "calculate_total",
  "params": {
    "prices": [100, 200, 300],
    "discount": 10
  }
}' http://localhost:8000/cmd
```

Response:

```json
{
  "result": 540.0
}
```

### 3. Params-only format

```json
{
  "params": {
    "command": "command_name",
    "param1": "value1",
    "param2": "value2"
  }
}
```

or

```json
{
  "params": {
    "query": "command_name",
    "param1": "value1",
    "param2": "value2"
  }
}
```

Example request:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "params": {
    "command": "calculate_total",
    "prices": [100, 200, 300],
    "discount": 10
  }
}' http://localhost:8000/cmd
```

Response:

```json
{
  "result": 540.0
}
```

## Full Example: Integration with FastAPI

```python
import logging
from fastapi import FastAPI, APIRouter
from mcp_proxy_adapter import CommandRegistry, MCPProxyAdapter, configure_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
project_logger = logging.getLogger("my_project")

# Create FastAPI app
app = FastAPI(title="My API with MCP Proxy Integration")

# Create existing API router
router = APIRouter()

@router.get("/items")
async def get_items():
    """Returns a list of items."""
    return [
        {"id": 1, "name": "Smartphone X", "price": 999.99},
        {"id": 2, "name": "Laptop Y", "price": 1499.99},
    ]

app.include_router(router)

# Register commands
registry = CommandRegistry()

@registry.command
def get_discounted_price(price: float, discount: float = 0.0) -> float:
    """
    Returns the price after applying a discount.
    """
    return price * (1 - discount / 100)

# Create and register MCP Proxy adapter
adapter = MCPProxyAdapter(registry)
adapter.register_endpoints(app)

# Save MCP Proxy config
adapter.save_config_to_file("mcp_proxy_config.json")
```

## Features
- Universal JSON-RPC endpoint for command execution
- Automatic OpenAPI schema generation and optimization for MCP Proxy
- Tool metadata for AI models
- Customizable endpoints and logging
- Full test coverage and examples

## License
MIT

## Documentation
See [docs/](docs/) for detailed guides, architecture, and examples.

## 📦 Примеры (examples/)

- `help_usage.py` — базовое использование help-команды
- `help_best_practices.py` — best practices для help
- `project_structure_example.py` — структура проекта с MCPProxyAdapter
- `docstring_and_schema_example.py` — как документировать команды для схемы
- `testing_example.py` — как тестировать команды и интеграцию
- `extension_example.py` — как расширять и кастомизировать команды и help

## ✅ Чеклист для добавления новой команды

1. **Реализовать функцию-команду** с подробным docstring (EN)
2. **Добавить описание параметров** (type, description, required)
3. **Добавить описание возврата** (docstring, тип)
4. **Зарегистрировать команду** в registry/dispatcher
5. **Добавить описание в get_commands_info** (использовать docstring)
6. **Покрыть тестами** (unit/integration, edge-cases, ошибки)
7. **Добавить пример использования** в examples/
8. **Проверить интеграцию с help** (и с параметром, и без)
9. **Проверить генерацию схемы/OpenAPI**
10. **Документировать в README.md** (EN/RU)

## 📦 Examples (EN)

- `help_usage.py` — basic help command usage
- `help_best_practices.py` — best practices for help
- `project_structure_example.py` — project structure with MCPProxyAdapter
- `docstring_and_schema_example.py` — how to document commands for schema
- `testing_example.py` — how to test commands and integration
- `extension_example.py` — how to extend/customize commands and help

## ✅ Checklist for adding a new command

1. **Implement the command function** with detailed docstring (EN)
2. **Describe parameters** (type, description, required)
3. **Describe return value** (docstring, type)
4. **Register the command** in registry/dispatcher
5. **Add description to get_commands_info** (use docstring)
6. **Cover with tests** (unit/integration, edge-cases, errors)
7. **Add usage example** to examples/
8. **Check help integration** (with/without param)
9. **Check schema/OpenAPI generation**
10. **Document in README.md** (EN/RU)

## ❓ FAQ

### Ошибка: got multiple values for argument 'command' при вызове команды help

**Проблема:**

Если в JSON-RPC запросе к endpoint `/cmd` используется команда `help` с параметром `command`, может возникнуть ошибка:

```
TypeError: help_command() got multiple values for argument 'command'
```

**Причина:**

В Python, если метод `execute(self, command, **params)` получает параметр `command` и в `params` также есть ключ `command`, возникает конфликт имён.

**Решение:**

Переименуйте первый аргумент метода `execute` в классе `MockDispatcher` (и аналогичных) с `command` на `command_name`:

```python
def execute(self, command_name, **params):
    if command_name not in self.commands:
        raise KeyError(f"Unknown command: {command_name}")
    return self.commands[command_name](**params)
```

Это устранит конфликт и позволит корректно вызывать команду help с параметром `command` через JSON-RPC. 

## 🚀 Deployment & Packaging FAQ

### Как собрать, проверить и опубликовать пакет (wheel/sdist) с примерами и документацией

1. **Перенесите каталоги `examples` и `docs` внутрь основного пакета** (например, `mcp_proxy_adapter/examples`, `mcp_proxy_adapter/docs`).
2. **Обновите `setup.py`:**
    - Укажите `include_package_data=True`.
    - В `package_data` добавьте:
      ```python
      package_data={
          'mcp_proxy_adapter': ['examples/*.py', 'examples/*.json', 'docs/*.md', '../README.md'],
      },
      ```
3. **Обновите `MANIFEST.in`:**
    - Убедитесь, что включены нужные файлы:
      ```
      include README.md
      include LICENSE
      include requirements.txt
      include pyproject.toml
      include code_index.yaml
      recursive-include mcp_proxy_adapter/examples *.py *.json
      recursive-include mcp_proxy_adapter/docs *.md
      ```
4. **Соберите пакет:**
    ```bash
    rm -rf dist build mcp_proxy_adapter.egg-info
    python3 -m build
    ```
5. **Создайте новое виртуальное окружение и установите пакет:**
    ```bash
    python3 -m venv ../mcp_proxy_adapter_test_env
    source ../mcp_proxy_adapter_test_env/bin/activate
    pip install --upgrade pip
    pip install dist/mcp_proxy_adapter-*.whl
    ```
6. **Проверьте, что примеры и документация попали в пакет:**
    ```bash
    ls -l ../mcp_proxy_adapter_test_env/lib/python*/site-packages/mcp_proxy_adapter/examples
    ls -l ../mcp_proxy_adapter_test_env/lib/python*/site-packages/mcp_proxy_adapter/docs
    ```
7. **Запустите пример сервера:**
    ```bash
    python ../mcp_proxy_adapter_test_env/lib/python*/site-packages/mcp_proxy_adapter/examples/openapi_server.py
    ```
8. **Проверьте работоспособность через curl:**
    ```bash
    curl http://localhost:8000/openapi.json | jq .
    ```
9. **Публикация на PyPI:**
    - Проверьте, что у вас настроен `~/.pypirc` и установлен twine:
      ```bash
      pip install twine
      twine upload dist/*
      ```

### Типовые проблемы и решения
- **Примеры или документация не попадают в пакет:**
  - Убедитесь, что они находятся внутри основного пакета и правильно указаны в `package_data` и `MANIFEST.in`.
- **Каталог docs не виден в wheel:**
  - Проверьте расширения файлов и шаблоны в `package_data`/`MANIFEST.in`.
- **Проверяйте установку только через wheel, а не через sdist!**

**Best practice:**
- Для публикации документации используйте GitHub и PyPI project page (README.md).
- Для примеров — всегда размещайте их внутри пакета, если хотите распространять с wheel. 