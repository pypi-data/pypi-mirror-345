# Примеры использования Command Registry

В этом разделе приведены практические примеры использования Command Registry для различных сценариев.

## Содержание

- [Базовые примеры](#базовые-примеры)
- [Интеграция с FastAPI](#интеграция-с-fastapi)
- [Интеграция с JSON-RPC](#интеграция-с-json-rpc)
- [Создание CLI](#создание-cli)
- [Полный пример проекта](#полный-пример-проекта)

## Базовые примеры

### Пример 1: Создание и регистрация команды

```python
from typing import Dict, Any, List

# Создаем простую команду
def search_by_keywords(keywords: List[str], limit: int = 10) -> Dict[str, Any]:
    """
    Поиск записей по ключевым словам.
    
    Args:
        keywords: Список ключевых слов
        limit: Максимальное количество результатов
        
    Returns:
        Dict[str, Any]: Результаты поиска
    """
    # Здесь был бы реальный код поиска
    results = [
        {"id": 1, "title": "Результат 1", "score": 0.95},
        {"id": 2, "title": "Результат 2", "score": 0.87}
    ]
    return {"results": results[:limit], "total": len(results)}

# Регистрируем команду
from command_registry import CommandRegistry

registry = CommandRegistry()
registry.register_command("search_by_keywords", search_by_keywords)

# Выполняем команду
result = registry.dispatcher.execute(
    "search_by_keywords", 
    keywords=["python", "api"],
    limit=5
)
print(result)
```

### Пример 2: Использование словаря метаданных

```python
# Команда с явными метаданными
def filter_data(filter_params: Dict[str, Any]) -> Dict[str, Any]:
    """Фильтрация данных по параметрам"""
    # Реализация...
    pass

# Словарь с метаданными команды
COMMAND = {
    "description": "Фильтрация данных по различным параметрам",
    "parameters": {
        "filter_params": {
            "type": "object",
            "description": "Параметры фильтрации",
            "required": True,
            "properties": {
                "date_from": {
                    "type": "string",
                    "format": "date",
                    "description": "Начальная дата (YYYY-MM-DD)"
                },
                "date_to": {
                    "type": "string",
                    "format": "date",
                    "description": "Конечная дата (YYYY-MM-DD)"
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список категорий"
                }
            }
        }
    },
    "responses": {
        "success": {
            "description": "Отфильтрованные данные",
            "schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "total": {"type": "integer"}
                }
            }
        }
    }
}
```

## Интеграция с FastAPI

### Создание REST API на основе команд

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from command_registry.generators import RestApiGenerator

# Создаем приложение FastAPI
app = FastAPI(title="Example API")

# Создаем реестр команд
registry = CommandRegistry()

# Указываем модули для поиска команд
registry.scan_modules(["commands.search", "commands.filter"])

# Регистрируем все команды
registry.register_all_commands()

# Создаем генератор REST API
rest_generator = RestApiGenerator(app)

# Генерируем эндпоинты для всех команд
endpoints = rest_generator.generate_all_endpoints()

# Информация о созданных эндпоинтах
print(f"Created {len(endpoints)} REST endpoints:")
for endpoint in endpoints:
    print(f"- {endpoint}")

# Запускаем приложение
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

Такой подход автоматически создаст REST эндпоинты для всех ваших команд:

```
GET /help                   # Справка по API
POST /search_by_keywords    # Поиск по ключевым словам
POST /filter_data           # Фильтрация данных
```

## Интеграция с JSON-RPC

### Создание JSON-RPC сервера

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from command_registry import CommandRegistry

# Создаем приложение FastAPI
app = FastAPI(title="JSON-RPC API")

# Создаем реестр команд
registry = CommandRegistry()

# Регистрируем команды
registry.scan_modules(["commands"])
registry.register_all_commands()

# Модель для JSON-RPC запроса
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

# Эндпоинт для обработки JSON-RPC запросов
@app.post("/rpc")
async def rpc_endpoint(request: JsonRpcRequest):
    try:
        # Извлекаем параметры запроса
        method = request.method
        params = request.params or {}
        req_id = request.id
        
        # Проверяем, что команда существует
        if method not in registry.dispatcher.get_valid_commands():
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                },
                "id": req_id
            })
        
        # Выполняем команду
        result = registry.dispatcher.execute(method, **params)
        
        # Возвращаем успешный ответ
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "result": result,
            "id": req_id
        })
    except Exception as e:
        # Возвращаем ошибку
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": str(e)
            },
            "id": request.id
        })

# Запускаем приложение
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

Пример использования JSON-RPC API:

```json
// Запрос
{
  "jsonrpc": "2.0",
  "method": "search_by_keywords",
  "params": {
    "keywords": ["python", "api"],
    "limit": 5
  },
  "id": "1"
}

// Ответ
{
  "jsonrpc": "2.0",
  "result": {
    "results": [
      {"id": 1, "title": "Результат 1", "score": 0.95},
      {"id": 2, "title": "Результат 2", "score": 0.87}
    ],
    "total": 2
  },
  "id": "1"
}
```

## Создание CLI

### Создание интерфейса командной строки

```python
from command_registry import CommandRegistry
from command_registry.cli import CommandRunner

# Создаем реестр команд
registry = CommandRegistry()

# Регистрируем команды
registry.scan_modules(["commands"])
registry.register_all_commands()

# Создаем CommandRunner
runner = CommandRunner(registry.dispatcher)

# Запускаем CLI
if __name__ == "__main__":
    import sys
    runner.run(sys.argv[1:])
```

Использование CLI:

```bash
# Получение списка команд
python cli.py

# Справка по конкретной команде
python cli.py help search_by_keywords

# Выполнение команды
python cli.py search_by_keywords --keywords='["python", "api"]' --limit=5
```

## Полный пример проекта

Ниже приведена структура полного проекта, использующего Command Registry:

```
project/
  ├── commands/
  │   ├── __init__.py
  │   ├── search/
  │   │   ├── __init__.py
  │   │   ├── search_by_keywords.py
  │   │   └── search_by_vector.py
  │   └── data/
  │       ├── __init__.py
  │       ├── filter_data.py
  │       └── add_data.py
  ├── api/
  │   ├── __init__.py
  │   ├── rest.py
  │   └── json_rpc.py
  ├── cli/
  │   ├── __init__.py
  │   └── main.py
  ├── app.py
  └── main.py
```

### app.py

```python
from command_registry import CommandRegistry
from command_registry.generators import RestApiGenerator, OpenApiGenerator
from fastapi import FastAPI

# Создаем приложение FastAPI
app = FastAPI(title="API Example", version="1.0.0")

def register_commands(strict: bool = True):
    """
    Регистрирует все команды в диспетчере.
    
    Args:
        strict: Если True, прерывает регистрацию при ошибках в документации
    """
    # Создаем реестр команд
    registry = CommandRegistry(strict=strict)
    
    # Сканируем модули с командами
    registry.scan_modules([
        "commands.search",
        "commands.data"
    ])
    
    # Создаем генератор REST API
    rest_generator = RestApiGenerator(app)
    registry.add_generator(rest_generator)
    
    # Создаем генератор OpenAPI схемы
    openapi_generator = OpenApiGenerator()
    registry.add_generator(openapi_generator)
    
    # Регистрируем все команды
    result = registry.register_all_commands()
    
    # Генерируем REST эндпоинты
    rest_generator.generate_all_endpoints()
    
    # Устанавливаем схему OpenAPI
    app.openapi = lambda: openapi_generator.generate_schema()
    
    return registry, result

# Регистрируем команды при импорте
registry, result = register_commands(strict=True)
```

### main.py

```python
from app import app

if __name__ == "__main__":
    import uvicorn
    
    print("Starting API server...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

### cli/main.py

```python
from app import registry
from command_registry.cli import CommandRunner

def main():
    """
    Запускает интерфейс командной строки.
    """
    runner = CommandRunner(registry.dispatcher)
    
    import sys
    runner.run(sys.argv[1:])

if __name__ == "__main__":
    main()
```

Такой проект предоставляет одновременно REST API, JSON-RPC API и интерфейс командной строки для одного и того же набора команд, что максимально повышает гибкость и переиспользование кода. 