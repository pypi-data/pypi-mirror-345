# Быстрый старт Command Registry

Это руководство поможет вам быстро начать работу с системой Command Registry и интегрировать её в ваше приложение.

## Установка

Установите пакет с помощью pip:

```bash
pip install command-registry
```

## Базовое использование

### 1. Определение команды

Создайте файл `commands.py` с вашими командами:

```python
from typing import List, Dict, Any, Optional

def add_item(
    item_name: str,
    quantity: int = 1,
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Добавляет новый товар в систему.
    
    Args:
        item_name: Название товара
        quantity: Количество товара (по умолчанию 1)
        properties: Дополнительные свойства товара
        
    Returns:
        Информация о созданном товаре
    """
    # В реальном приложении здесь был бы код для
    # сохранения товара в базе данных
    item_id = "item_" + str(hash(item_name))
    item = {
        "id": item_id,
        "name": item_name,
        "quantity": quantity,
        "properties": properties or {}
    }
    return item

def get_items(
    search_term: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Получает список товаров с возможностью поиска и пагинации.
    
    Args:
        search_term: Строка для поиска по названию (опционально)
        limit: Максимальное количество возвращаемых товаров
        offset: Смещение для пагинации результатов
        
    Returns:
        Список товаров, соответствующих критериям поиска
    """
    # В реальном приложении здесь был бы код для
    # получения товаров из базы данных
    items = [
        {"id": f"item_{i}", "name": f"Товар {i}", "quantity": i % 10}
        for i in range(offset, offset + limit)
    ]
    
    if search_term:
        items = [item for item in items if search_term.lower() in item["name"].lower()]
        
    return items
```

### 2. Создание Command Registry

Создайте файл `app.py` с инициализацией Command Registry:

```python
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
import commands

# Создание экземпляра диспетчера
dispatcher = CommandDispatcher()

# Создание реестра команд
registry = CommandRegistry(dispatcher)

# Регистрация команд
registry.register_command("add_item", commands.add_item)
registry.register_command("get_items", commands.get_items)

# Автоматическая регистрация всех команд из модуля (альтернативный способ)
# registry.scan_module(commands)
```

### 3. Выполнение команд

Добавьте в `app.py` код для выполнения команд:

```python
# Выполнение команды add_item
result = registry.execute(
    "add_item", 
    {
        "item_name": "Ноутбук",
        "quantity": 5,
        "properties": {"brand": "SuperLaptop", "color": "silver"}
    }
)
print("Результат add_item:", result)

# Выполнение команды get_items
items = registry.execute(
    "get_items", 
    {
        "search_term": "Товар",
        "limit": 5
    }
)
print(f"Найдено {len(items)} товаров:")
for item in items:
    print(f"- {item['name']} (ID: {item['id']}, Количество: {item['quantity']})")
```

### 4. Информация о командах

```python
# Получение списка доступных команд
commands = registry.get_valid_commands()
print("Доступные команды:", commands)

# Получение информации о конкретной команде
info = registry.get_command_info("add_item")
print("Информация о команде add_item:")
print(f"- Описание: {info['description']}")
print(f"- Параметры: {list(info['params'].keys())}")
```

## Интеграция с веб-фреймворками

### FastAPI

```python
from fastapi import FastAPI
from command_registry.adapters import RESTAdapter

app = FastAPI(title="Command Registry API")

# Создание адаптера REST
rest_adapter = RESTAdapter(registry)

# Регистрация эндпоинтов в FastAPI
rest_adapter.register_endpoints(app)

# Запуск приложения
# uvicorn app:app --reload
```

### Flask

```python
from flask import Flask
from command_registry.adapters import FlaskRESTAdapter

app = Flask(__name__)

# Создание адаптера REST для Flask
flask_adapter = FlaskRESTAdapter(registry)

# Регистрация эндпоинтов в Flask
flask_adapter.register_endpoints(app)

# Запуск приложения
# app.run(debug=True)
```

### aiohttp

```python
from aiohttp import web
from command_registry.adapters import AioHttpAdapter

app = web.Application()

# Создание адаптера aiohttp
aiohttp_adapter = AioHttpAdapter(registry)

# Регистрация эндпоинтов
aiohttp_adapter.register_endpoints(app)

# Запуск приложения
# web.run_app(app)
```

## Использование JSON-RPC

```python
from fastapi import FastAPI
from command_registry.adapters import JSONRPCAdapter

app = FastAPI(title="Command Registry JSON-RPC API")

# Создание адаптера JSON-RPC
jsonrpc_adapter = JSONRPCAdapter(registry)

# Регистрация эндпоинта JSON-RPC
jsonrpc_adapter.register_endpoint(app, "/api/jsonrpc")

# Запуск приложения
# uvicorn app:app --reload
```

## Интеграция с командной строкой

```python
from command_registry.adapters import ClickAdapter
import click

# Создание адаптера для Click
cli_adapter = ClickAdapter(registry)

# Создание CLI приложения
cli = click.Group()

# Регистрация команд
cli_adapter.register_commands(cli)

# Запуск CLI
if __name__ == "__main__":
    cli()
```

## Обработка ошибок

```python
from command_registry.exceptions import (
    CommandNotFoundError,
    ValidationError,
    CommandExecutionError
)

try:
    result = registry.execute("non_existent_command", {})
except CommandNotFoundError as e:
    print(f"Ошибка: Команда не найдена - {e}")
    
try:
    result = registry.execute("add_item", {"wrong_param": "value"})
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
    print(f"Детали: {e.errors()}")
    
try:
    result = registry.execute("add_item", {"item_name": None})
except CommandExecutionError as e:
    print(f"Ошибка выполнения: {e}")
    print(f"Исходное исключение: {e.__cause__}")
```

## Валидация параметров

Включение проверки типов и валидации:

```python
# При создании диспетчера
dispatcher = CommandDispatcher(validate_types=True)

# Или при создании реестра
registry = CommandRegistry(dispatcher, validate_types=True)
```

## Генерация документации

```python
from command_registry.generators import OpenAPIGenerator

# Создание генератора OpenAPI
generator = OpenAPIGenerator(registry)

# Генерация документа OpenAPI
openapi_schema = generator.generate_schema(
    title="Command Registry API",
    version="1.0.0",
    description="API для управления товарами"
)

# Сохранение схемы в файл
import json
with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)
```

## Полное демо-приложение

```python
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
from command_registry.adapters import RESTAdapter
from fastapi import FastAPI
import uvicorn
from typing import Dict, Any, List, Optional

# Определение команд
def add_item(
    item_name: str,
    quantity: int = 1,
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Добавляет новый товар в систему.
    
    Args:
        item_name: Название товара
        quantity: Количество товара (по умолчанию 1)
        properties: Дополнительные свойства товара
        
    Returns:
        Информация о созданном товаре
    """
    item_id = "item_" + str(hash(item_name))
    item = {
        "id": item_id,
        "name": item_name,
        "quantity": quantity,
        "properties": properties or {}
    }
    return item

def get_items(
    search_term: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Получает список товаров с возможностью поиска и пагинации.
    
    Args:
        search_term: Строка для поиска по названию (опционально)
        limit: Максимальное количество возвращаемых товаров
        offset: Смещение для пагинации результатов
        
    Returns:
        Список товаров, соответствующих критериям поиска
    """
    items = [
        {"id": f"item_{i}", "name": f"Товар {i}", "quantity": i % 10}
        for i in range(offset, offset + limit)
    ]
    
    if search_term:
        items = [item for item in items if search_term.lower() in item["name"].lower()]
        
    return items

# Создание реестра команд
dispatcher = CommandDispatcher(validate_types=True)
registry = CommandRegistry(dispatcher)

# Регистрация команд
registry.register_command("add_item", add_item)
registry.register_command("get_items", get_items)

# Создание FastAPI приложения
app = FastAPI(title="Inventory API")

# Создание REST адаптера и регистрация эндпоинтов
rest_adapter = RESTAdapter(registry)
rest_adapter.register_endpoints(app)

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Запустите приложение:

```bash
python app.py
```

После запуска вы можете:

1. Открыть документацию API по адресу: http://localhost:8000/docs
2. Тестировать эндпоинты через Swagger UI
3. Отправлять запросы к API с помощью curl или Postman

## Что дальше?

- Изучите [архитектуру системы](architecture.md) для лучшего понимания её компонентов
- Прочитайте [руководство по разработке команд](command_development.md) для изучения лучших практик
- Познакомьтесь с возможностями [валидации](validation.md)
- Изучите [примеры использования](examples.md) для различных сценариев 