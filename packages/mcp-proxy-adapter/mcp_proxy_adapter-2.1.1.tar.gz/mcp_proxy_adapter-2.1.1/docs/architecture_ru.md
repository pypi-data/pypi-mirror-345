# Архитектура Command Registry

Данный документ описывает архитектуру системы Command Registry, ее ключевые компоненты, их взаимодействие и принципы расширения.

## Обзор архитектуры

Command Registry - это модульная система, построенная вокруг концепции централизованного хранения и управления командами. Архитектура обеспечивает гибкость, расширяемость и соблюдение принципов SOLID.

Ключевые возможности системы:

1. **Определение команд как Python-функций** с использованием типизации и докстрингов
2. **Извлечение метаданных** из сигнатур функций и их документации
3. **Регистрация команд** в центральном реестре
4. **Предоставление унифицированного интерфейса** для выполнения команд
5. **Генерация документации API** на основе метаданных команд
6. **Экспорт команд** через различные протоколы (REST, JSON-RPC, CLI и т.д.)

## Компоненты системы

![Диаграмма компонентов](../diagrams/command_registry_components.png)

### Основные компоненты:

1. **Command Definition** - Определение команды (функция Python с типизацией и докстрингами)
2. **Dispatcher Component** - Диспетчер команд, отвечающий за их регистрацию и выполнение
3. **Metadata Extractor** - Извлекатель метаданных из докстрингов и сигнатур функций
4. **Protocol Adapter** - Адаптер для экспорта команд через различные протоколы

### CommandRegistry

Центральный компонент системы, который:

- Инициализирует и конфигурирует диспетчеры
- Предоставляет интерфейс для регистрации команд
- Управляет метаданными команд
- Координирует взаимодействие между компонентами

## Жизненный цикл команды

### 1. Определение команды

```python
def calculate_total(
    prices: List[float], 
    discount: float = 0.0,
    tax_rate: float = 0.0
) -> float:
    """
    Рассчитывает общую стоимость с учетом скидки и налога.
    
    Args:
        prices: Список цен товаров
        discount: Скидка в процентах (0-100)
        tax_rate: Налоговая ставка в процентах (0-100)
        
    Returns:
        Общая стоимость с учетом скидки и налога
    """
    subtotal = sum(prices)
    discounted = subtotal * (1 - discount / 100)
    total = discounted * (1 + tax_rate / 100)
    return round(total, 2)
```

### 2. Регистрация команды

```python
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher

# Создание реестра команд
registry = CommandRegistry(CommandDispatcher())

# Регистрация команды
registry.register_command("calculate_total", calculate_total)
```

### 3. Выполнение команды

```python
# Выполнение команды
result = registry.execute(
    "calculate_total", 
    {
        "prices": [10.0, 20.0, 30.0],
        "discount": 10.0,
        "tax_rate": 7.0
    }
)
print(result)  # 57.33
```

### 4. Экспорт через API

```python
from fastapi import FastAPI
from command_registry.adapters import RESTAdapter

app = FastAPI()
adapter = RESTAdapter(registry)
adapter.register_endpoints(app)
```

## Диаграммы потока данных

### Процесс регистрации команды

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Python функция ├─────►│  Metadata Extractor ├─────►│  Метаданные     │
│                 │      │                    │      │                 │
└─────────────────┘      └────────────────────┘      └────────┬────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  CommandRegistry│◄─────┤  Валидация данных  │◄─────┤  Параметры      │
│                 │      │                    │      │                 │
└────────┬────────┘      └────────────────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Dispatcher     │
│                 │
└─────────────────┘
```

### Процесс выполнения команды

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Имя команды    │      │                    │      │  Валидация      │
│  + параметры    ├─────►│  CommandRegistry   ├─────►│  параметров     │
│                 │      │                    │      │                 │
└─────────────────┘      └────────────────────┘      └────────┬────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Результат      │◄─────┤  Обработка ошибок  │◄─────┤  Dispatcher     │
│                 │      │                    │      │  (выполнение)   │
└─────────────────┘      └────────────────────┘      └─────────────────┘
```

### Генерация документации API

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Метаданные     │      │  Schema Generator  │      │  OpenAPI/       │
│  команд         ├─────►│                    ├─────►│  JSON Schema    │
│                 │      │                    │      │                 │
└─────────────────┘      └────────────────────┘      └────────┬────────┘
                                                              │
                                                              ▼
                                                     ┌─────────────────┐
                                                     │                 │
                                                     │  API Docs UI    │
                                                     │  (Swagger/      │
                                                     │   ReDoc)        │
                                                     └─────────────────┘
```

## Расширение системы

### Создание собственного диспетчера

```python
from command_registry.dispatchers import BaseDispatcher
from typing import Dict, Any, List, Optional, Callable

class MyCustomDispatcher(BaseDispatcher):
    def __init__(self):
        self._commands = {}
        self._info = {}
        
    def register_handler(
        self, 
        command_name: str,
        handler: Callable,
        description: str = None,
        summary: str = None,
        params: Dict[str, Any] = None
    ) -> None:
        self._commands[command_name] = handler
        self._info[command_name] = {
            "description": description,
            "summary": summary,
            "params": params or {}
        }
        
    def execute(self, command_name: str, params: Dict[str, Any] = None) -> Any:
        if command_name not in self._commands:
            raise ValueError(f"Command '{command_name}' not found")
        
        handler = self._commands[command_name]
        return handler(**params or {})
    
    def get_valid_commands(self) -> List[str]:
        return list(self._commands.keys())
    
    def get_command_info(self, command_name: str) -> Optional[Dict[str, Any]]:
        return self._info.get(command_name)
    
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        return self._info
```

### Создание собственного адаптера протокола

```python
from command_registry import CommandRegistry
from typing import Dict, Any

class GraphQLAdapter:
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
        
    def generate_schema(self) -> str:
        """Генерирует GraphQL схему на основе метаданных команд."""
        commands_info = self.registry.get_all_commands_info()
        schema_types = []
        query_fields = []
        
        for cmd_name, info in commands_info.items():
            # Генерация типов для входных и выходных данных
            input_type = self._generate_input_type(cmd_name, info["params"])
            output_type = self._generate_output_type(cmd_name, info.get("returns"))
            
            schema_types.extend([input_type, output_type])
            
            # Добавление поля в Query
            query_fields.append(
                f"{cmd_name}(input: {cmd_name}Input): {cmd_name}Output"
            )
        
        # Формирование итоговой схемы
        schema = "\n".join(schema_types)
        schema += f"\ntype Query {{\n  {chr(10).join(query_fields)}\n}}"
        
        return schema
    
    def _generate_input_type(self, cmd_name: str, params: Dict[str, Any]) -> str:
        fields = []
        for name, param_info in params.items():
            field_type = self._map_type(param_info.get("type", "String"))
            required = "!" if param_info.get("required", False) else ""
            fields.append(f"  {name}: {field_type}{required}")
        
        return f"input {cmd_name}Input {{\n{chr(10).join(fields)}\n}}"
    
    def _generate_output_type(self, cmd_name: str, returns_info: Dict[str, Any]) -> str:
        return_type = "String"
        if returns_info:
            return_type = self._map_type(returns_info.get("type", "String"))
        
        return (
            f"type {cmd_name}Output {{\n"
            f"  result: {return_type}\n"
            f"  error: String\n"
            f"}}"
        )
    
    def _map_type(self, python_type: str) -> str:
        """Преобразует типы Python в типы GraphQL."""
        type_mapping = {
            "str": "String",
            "int": "Int",
            "float": "Float",
            "bool": "Boolean",
            "list": "List",
            "dict": "JSON",
            # Добавьте другие маппинги по необходимости
        }
        return type_mapping.get(python_type, "String")
```

## Лучшие практики

### Организация команд в модули

Рекомендуется группировать связанные команды в модули по их функциональности:

```
commands/
  ├── __init__.py
  ├── user_commands.py    # Команды для работы с пользователями
  ├── product_commands.py # Команды для работы с товарами
  └── order_commands.py   # Команды для работы с заказами
```

### Регистрация команд

Автоматическая регистрация из модуля:

```python
registry.scan_module("myapp.commands")
```

Ручная регистрация отдельных функций:

```python
from myapp.commands.user_commands import create_user, update_user, delete_user

registry.register_command("create_user", create_user)
registry.register_command("update_user", update_user)
registry.register_command("delete_user", delete_user)
```

### Обработка ошибок

```python
def divide_numbers(a: float, b: float) -> float:
    """
    Делит число a на число b.
    
    Args:
        a: Делимое
        b: Делитель (не должен быть равен 0)
        
    Returns:
        Результат деления a на b
        
    Raises:
        ValueError: Если делитель равен 0
    """
    if b == 0:
        raise ValueError("Делитель не может быть равен 0")
    return a / b
```

## Заключение

Архитектура Command Registry обеспечивает:

1. **Четкое разделение ответственности** между компонентами системы
2. **Расширяемость** через добавление новых диспетчеров и адаптеров
3. **Простоту использования** для разработчиков команд
4. **Автоматизацию** извлечения метаданных и валидации
5. **Интероперабельность** с различными протоколами и форматами 