# Руководство по тестированию команд

В этом руководстве описаны подходы и лучшие практики по тестированию команд, зарегистрированных в Command Registry.

## Почему важно тестировать команды

Команды в Command Registry часто представляют собой ключевые бизнес-операции приложения. Их тестирование имеет следующие преимущества:

1. **Надёжность** - проверка работоспособности команд в различных условиях
2. **Документация** - тесты демонстрируют ожидаемое поведение команд
3. **Регрессия** - предотвращение появления регрессий при изменениях
4. **Рефакторинг** - возможность безопасно улучшать код команд
5. **Валидация** - проверка корректной обработки входных параметров и ошибок

## Уровни тестирования

### 1. Модульное тестирование (Unit Tests)

Тестирование отдельных функций-команд в изоляции от других компонентов.

```python
import pytest
from myapp.commands.math_commands import add_numbers

def test_add_numbers_basic():
    # Базовый сценарий
    result = add_numbers(5, 3)
    assert result == 8
    
def test_add_numbers_negative():
    # Работа с отрицательными числами
    result = add_numbers(-5, 3)
    assert result == -2
    
def test_add_numbers_zero():
    # Работа с нулями
    result = add_numbers(0, 0)
    assert result == 0
```

### 2. Интеграционное тестирование (Integration Tests)

Тестирование команд с реальными зависимостями или их моками.

```python
import pytest
from unittest.mock import MagicMock, patch
from myapp.commands.user_commands import get_user_data

@pytest.fixture
def mock_db():
    """Фикстура для создания мока базы данных."""
    mock = MagicMock()
    mock.users.find_one.return_value = {
        "id": "user123",
        "name": "Test User",
        "email": "test@example.com",
        "created_at": "2023-01-01T00:00:00Z"
    }
    return mock

@patch("myapp.commands.user_commands.get_database")
def test_get_user_data(get_database_mock, mock_db):
    # Настройка мока
    get_database_mock.return_value = mock_db
    
    # Вызов команды
    result = get_user_data("user123")
    
    # Проверки
    assert result["id"] == "user123"
    assert result["name"] == "Test User"
    assert "email" in result
    
    # Проверка вызова БД с правильными параметрами
    mock_db.users.find_one.assert_called_once_with({"id": "user123"})
```

### 3. Тестирование через Command Registry

Тестирование команд через интерфейс Command Registry.

```python
import pytest
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
from myapp.commands.math_commands import add_numbers, subtract_numbers

@pytest.fixture
def registry():
    """Фикстура для создания CommandRegistry с зарегистрированными командами."""
    registry = CommandRegistry(CommandDispatcher())
    registry.register_command("add", add_numbers)
    registry.register_command("subtract", subtract_numbers)
    return registry

def test_registry_add_command(registry):
    # Выполнение команды через реестр
    result = registry.execute("add", {"a": 10, "b": 5})
    assert result == 15
    
def test_registry_subtract_command(registry):
    # Выполнение команды через реестр
    result = registry.execute("subtract", {"a": 10, "b": 5})
    assert result == 5
    
def test_command_not_found(registry):
    # Проверка обработки несуществующей команды
    with pytest.raises(ValueError, match="Command 'multiply' not found"):
        registry.execute("multiply", {"a": 10, "b": 5})
```

### 4. E2E тестирование через API

Тестирование команд через внешние интерфейсы (REST, JSON-RPC и т.д.).

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app  # FastAPI приложение с зарегистрированными командами

client = TestClient(app)

def test_add_numbers_api():
    response = client.post(
        "/api/commands/add",
        json={"a": 10, "b": 5}
    )
    assert response.status_code == 200
    assert response.json() == {"result": 15}
    
def test_invalid_params_api():
    response = client.post(
        "/api/commands/add",
        json={"a": "not_a_number", "b": 5}
    )
    assert response.status_code == 400
    assert "error" in response.json()
```

## Тестирование с использованием параметризации

Параметризация позволяет тестировать множество сценариев с разными входными данными и ожиданиями.

```python
import pytest
from myapp.commands.math_commands import calculate_total

@pytest.mark.parametrize("prices, discount, expected", [
    ([10, 20, 30], 0, 60),       # Без скидки
    ([10, 20, 30], 10, 54),      # Скидка 10%
    ([100], 50, 50),            # Скидка 50%
    ([], 10, 0),                # Пустой список
])
def test_calculate_total(prices, discount, expected):
    result = calculate_total(prices, discount)
    assert result == expected

@pytest.mark.parametrize("invalid_discount", [-10, 110, "invalid"])
def test_calculate_total_invalid_discount(invalid_discount):
    with pytest.raises(ValueError):
        calculate_total([10, 20], invalid_discount)
```

## Тестирование асинхронных команд

Для тестирования асинхронных команд используйте pytest-asyncio.

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from myapp.commands.async_commands import fetch_user_data

@pytest.mark.asyncio
@patch("myapp.commands.async_commands.get_async_database")
async def test_fetch_user_data(mock_get_db):
    # Создаем асинхронный мок
    mock_db = AsyncMock()
    mock_db.users.find_one.return_value = {"id": "user123", "name": "Test User"}
    mock_get_db.return_value = mock_db
    
    # Вызываем асинхронную команду
    result = await fetch_user_data("user123")
    
    # Проверяем результат
    assert result["id"] == "user123"
    assert result["name"] == "Test User"
    
    # Проверяем, что мок был вызван с правильными параметрами
    mock_db.users.find_one.assert_called_once_with({"id": "user123"})
```

## Тестирование обработки ошибок

```python
import pytest
from myapp.commands.user_commands import get_user_data
from myapp.exceptions import UserNotFoundError

@patch("myapp.commands.user_commands.get_database")
def test_get_user_data_not_found(mock_get_db):
    # Настраиваем мок для возврата None (пользователь не найден)
    db_mock = MagicMock()
    db_mock.users.find_one.return_value = None
    mock_get_db.return_value = db_mock
    
    # Проверяем, что команда вызывает ожидаемое исключение
    with pytest.raises(UserNotFoundError, match="User with id 'unknown_user' not found"):
        get_user_data("unknown_user")
```

## Тестирование валидации параметров

```python
import pytest
from myapp.commands.product_commands import update_product_price

def test_update_product_price_negative():
    # Проверка на отрицательную цену
    with pytest.raises(ValueError, match="Price cannot be negative"):
        update_product_price("product123", -10.0)
        
def test_update_product_price_invalid_id():
    # Проверка на пустой идентификатор продукта
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        update_product_price("", 10.0)
```

## Использование фикстур для общих случаев

```python
import pytest
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
import myapp.commands as commands

@pytest.fixture
def registry():
    """Создает CommandRegistry со всеми зарегистрированными командами."""
    registry = CommandRegistry(CommandDispatcher())
    registry.scan_module(commands)
    return registry

@pytest.fixture
def mock_database():
    """Создает мок базы данных с тестовыми данными."""
    db = MagicMock()
    db.users.find_one.return_value = {"id": "user1", "name": "Test User"}
    db.products.find.return_value = [
        {"id": "prod1", "name": "Product 1", "price": 10.0},
        {"id": "prod2", "name": "Product 2", "price": 20.0}
    ]
    return db

@pytest.fixture
def app_client(registry):
    """Создает тестовый клиент для FastAPI с Command Registry."""
    from fastapi import FastAPI
    from command_registry.adapters import RESTAdapter
    
    app = FastAPI()
    adapter = RESTAdapter(registry)
    adapter.register_endpoints(app)
    
    from fastapi.testclient import TestClient
    return TestClient(app)
```

## Мокирование внешних зависимостей

```python
import pytest
from unittest.mock import patch, MagicMock
import requests
from myapp.commands.external_commands import fetch_external_data

@patch("myapp.commands.external_commands.requests.get")
def test_fetch_external_data(mock_get):
    # Настраиваем мок для requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test_data"}
    mock_get.return_value = mock_response
    
    # Вызываем команду
    result = fetch_external_data("https://api.example.com/data")
    
    # Проверяем результат
    assert result == {"data": "test_data"}
    
    # Проверяем, что запрос был отправлен по правильному URL
    mock_get.assert_called_once_with("https://api.example.com/data")

@patch("myapp.commands.external_commands.requests.get")
def test_fetch_external_data_error(mock_get):
    # Настраиваем мок для имитации ошибки
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    # Проверяем, что команда корректно обрабатывает ошибку
    with pytest.raises(ValueError, match="Failed to fetch data"):
        fetch_external_data("https://api.example.com/data")
```

## Тестирование полной интеграции с Command Registry

```python
def test_full_registry_integration(registry):
    """
    Тестирует полную интеграцию с Command Registry, включая:
    - регистрацию команд
    - получение метаданных
    - выполнение команд
    - обработку ошибок
    """
    # Проверка регистрации
    commands = registry.get_valid_commands()
    assert "add_user" in commands
    assert "get_user" in commands
    
    # Проверка метаданных
    add_user_info = registry.get_command_info("add_user")
    assert add_user_info["description"] == "Создает нового пользователя"
    assert "name" in add_user_info["params"]
    assert add_user_info["params"]["name"]["required"] is True
    
    # Выполнение команды
    with patch("myapp.commands.user_commands.get_database") as mock_get_db:
        db_mock = MagicMock()
        mock_get_db.return_value = db_mock
        db_mock.users.insert_one.return_value.inserted_id = "new_user_id"
        
        result = registry.execute("add_user", {
            "name": "New User",
            "email": "new@example.com"
        })
        
        assert result["id"] == "new_user_id"
        assert result["name"] == "New User"
        db_mock.users.insert_one.assert_called_once()
    
    # Проверка обработки ошибок при выполнении
    with pytest.raises(ValueError):
        registry.execute("add_user", {
            "name": "",  # Пустое имя должно вызвать ошибку валидации
            "email": "new@example.com"
        })
    
    # Проверка обработки несуществующей команды
    with pytest.raises(ValueError, match="Command 'non_existent' not found"):
        registry.execute("non_existent", {})
```

## Рекомендации по организации тестов

1. **Структура директорий** - зеркалируйте структуру исходного кода:
   ```
   src/
     commands/
       user_commands.py
       product_commands.py
   tests/
     commands/
       test_user_commands.py
       test_product_commands.py
   ```

2. **Именование** - используйте понятные имена тестов, отражающие проверяемую функциональность:
   ```python
   def test_add_user_creates_new_user_with_valid_data():
       # ...
       
   def test_add_user_raises_error_when_name_is_empty():
       # ...
   ```

3. **Документирование тестов** - добавляйте docstrings, поясняющие цель теста:
   ```python
   def test_calculate_total_applies_discount_correctly():
       """
       Проверяет, что команда calculate_total правильно применяет скидку к сумме.
       Должна вычесть процент скидки из общей суммы всех цен.
       """
       # ...
   ```

## Примеры тестирования распространенных сценариев

### Тестирование команды с транзакцией базы данных

```python
import pytest
from unittest.mock import MagicMock, patch
from myapp.commands.order_commands import create_order

@patch("myapp.commands.order_commands.get_database")
def test_create_order_transaction(mock_get_db):
    # Настраиваем моки для базы данных и транзакции
    db_mock = MagicMock()
    transaction_mock = MagicMock()
    db_mock.begin_transaction.return_value = transaction_mock
    mock_get_db.return_value = db_mock
    
    # Выполняем команду
    result = create_order(
        user_id="user123",
        items=[
            {"product_id": "prod1", "quantity": 2},
            {"product_id": "prod2", "quantity": 1}
        ]
    )
    
    # Проверяем, что транзакция была начата и закоммичена
    db_mock.begin_transaction.assert_called_once()
    transaction_mock.commit.assert_called_once()
    
    # Проверяем, что не было отката транзакции
    transaction_mock.rollback.assert_not_called()
    
@patch("myapp.commands.order_commands.get_database")
def test_create_order_transaction_rollback(mock_get_db):
    # Настраиваем моки для имитации ошибки
    db_mock = MagicMock()
    transaction_mock = MagicMock()
    db_mock.begin_transaction.return_value = transaction_mock
    db_mock.orders.insert_one.side_effect = Exception("DB Error")
    mock_get_db.return_value = db_mock
    
    # Проверяем, что команда корректно обрабатывает ошибку
    with pytest.raises(Exception):
        create_order(
            user_id="user123",
            items=[{"product_id": "prod1", "quantity": 2}]
        )
    
    # Проверяем, что транзакция была начата и откачена
    db_mock.begin_transaction.assert_called_once()
    transaction_mock.rollback.assert_called_once()
```

### Тестирование логирования в командах

```python
import pytest
import logging
from unittest.mock import patch
from myapp.commands.user_commands import delete_user

@patch("myapp.commands.user_commands.logger")
@patch("myapp.commands.user_commands.get_database")
def test_delete_user_logging(mock_get_db, mock_logger):
    # Настраиваем мок базы данных
    db_mock = MagicMock()
    db_mock.users.delete_one.return_value.deleted_count = 1
    mock_get_db.return_value = db_mock
    
    # Выполняем команду
    result = delete_user("user123")
    
    # Проверяем, что логи были созданы
    mock_logger.info.assert_any_call("Deleting user with ID: user123")
    mock_logger.info.assert_any_call("User user123 successfully deleted")
```

## Заключение

Тестирование команд в Command Registry - важная часть обеспечения качества приложения. Используйте комбинацию модульных, интеграционных и E2E тестов для достижения максимального покрытия. Помните, что хорошие тесты не только проверяют правильную работу кода, но и документируют ожидаемое поведение системы. 