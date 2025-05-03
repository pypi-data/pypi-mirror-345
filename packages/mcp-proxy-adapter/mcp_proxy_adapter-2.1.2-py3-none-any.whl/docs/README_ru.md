# Command Registry

## Обзор

Command Registry - это высокоуровневая система для централизованного управления командами в приложении. Она предоставляет унифицированный механизм определения, регистрации, выполнения и документирования команд через различные интерфейсы.

## Основные возможности

- **Единая точка доступа** к командам приложения
- **Автоматическое извлечение метаданных** из докстрингов и типизации Python
- **Интеграция с различными протоколами** (REST, JSON-RPC, WebSockets)
- **Генерация документации API** на основе метаданных команд
- **Валидация входных параметров** и выходных значений
- **Проверка соответствия метаданных** фактической сигнатуре функций
- **Расширяемость** через интерфейсы для диспетчеров, адаптеров и генераторов схем
- **Интеграция с моделями ИИ** через MCP Proxy Adapter

## Начало работы

### Установка

```bash
pip install command-registry
```

Для работы с MCP Proxy также установите:

```bash
pip install mcp-proxy-adapter
```

### Простой пример

```python
from command_registry import CommandRegistry

# Создание экземпляра реестра команд
registry = CommandRegistry()

# Определение команды
def add_numbers(a: int, b: int) -> int:
    """Складывает два числа.
    
    Args:
        a: Первое число
        b: Второе число
        
    Returns:
        Сумма чисел a и b
    """
    return a + b

# Регистрация команды
registry.register_command("add", add_numbers)

# Выполнение команды
result = registry.execute("add", {"a": 5, "b": 3})  # Вернёт 8
```

### Экспорт через FastAPI

```python
from fastapi import FastAPI
from command_registry.adapters import RESTAdapter

app = FastAPI()
adapter = RESTAdapter(registry)
adapter.register_endpoints(app)
```

### Интеграция с MCP Proxy для моделей ИИ

```python
from fastapi import FastAPI
from mcp_proxy_adapter.adapter import MCPProxyAdapter

app = FastAPI()
adapter = MCPProxyAdapter(registry)
adapter.register_endpoints(app)

# Создание конфигурации для MCP Proxy
adapter.save_config_to_file("mcp_proxy_config.json")
```

### Автоматическая регистрация команд из модуля

```python
# Сканирование модуля и регистрация всех найденных команд
registry.scan_module("myapp.commands")
```

## Документация

- [Архитектура](architecture.md) - подробное описание компонентов
- [Руководство по разработке команд](command_development.md) - лучшие практики
- [Примеры](examples.md) - примеры использования для различных сценариев
- [Валидация](validation.md) - механизмы проверки команд
- [MCP Proxy Adapter](mcp_proxy_adapter.md) - интеграция с моделями ИИ через MCP Proxy

## Структура проекта

```
command_registry/
  ├── __init__.py            # Основные публичные API
  ├── core.py                # Основная логика CommandRegistry
  ├── dispatchers/           # Диспетчеры команд
  │   ├── __init__.py
  │   ├── base_dispatcher.py  # Абстрактный базовый класс
  │   └── command_dispatcher.py  # Основная реализация
  ├── metadata/              # Извлечение метаданных
  │   ├── __init__.py
  │   ├── docstring_parser.py  # Парсер докстрингов
  │   └── type_analyzer.py   # Анализатор типов
  ├── validators/            # Валидаторы
  │   ├── __init__.py
  │   └── parameter_validator.py  # Валидация параметров
  ├── adapters/              # Адаптеры протоколов
  │   ├── __init__.py
  │   ├── rest_adapter.py    # REST API
  │   └── json_rpc_adapter.py  # JSON-RPC
  └── schema/                # Генераторы схем
      ├── __init__.py
      ├── openapi_generator.py  # OpenAPI
      └── json_schema_generator.py  # JSON Schema
```

## Интеграция с существующими системами

Command Registry спроектирован для легкой интеграции с существующими системами и фреймворками:

- **FastAPI** - через RESTAdapter
- **Flask** - через RESTAdapter с модификациями
- **aiohttp** - через адаптер для WebSockets
- **Click** - через CLI адаптер
- **GraphQL** - через GraphQL адаптер
- **MCP Proxy** - через MCPProxyAdapter для интеграции с моделями ИИ

## Примеры использования

### REST API

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from command_registry.adapters import RESTAdapter

app = FastAPI()
registry = CommandRegistry()
registry.scan_module("myapp.commands")

adapter = RESTAdapter(registry)
adapter.register_endpoints(app)
```

### JSON-RPC через MCP Proxy Adapter

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter

app = FastAPI()
registry = CommandRegistry()
registry.scan_module("myapp.commands")

adapter = MCPProxyAdapter(registry)
adapter.register_endpoints(app)
```

## Лицензия

MIT 