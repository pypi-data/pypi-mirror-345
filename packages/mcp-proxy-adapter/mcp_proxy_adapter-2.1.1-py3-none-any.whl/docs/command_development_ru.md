# Руководство по разработке команд

В этом руководстве описаны лучшие практики и рекомендации по разработке команд для системы Command Registry.

## Основные принципы

При разработке команд для Command Registry придерживайтесь следующих принципов:

1. **Единственная ответственность**: команда должна выполнять одну задачу и делать это хорошо
2. **Декларативность**: команда должна быть самодокументированной через типизацию и docstrings
3. **Независимость**: команда не должна зависеть от других команд
4. **Идемпотентность**: повторное выполнение команды с одинаковыми параметрами должно давать идентичный результат
5. **Валидация**: команда должна проверять входные данные перед выполнением

## Структура команды

Рекомендуемая структура команды:

```python
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger(__name__)

def command_name(
    required_param: str,
    optional_param: Optional[int] = None,
    *,
    keyword_only_param: bool = False
) -> Dict[str, Any]:
    """
    Краткое описание команды (одно предложение).
    
    Подробное описание команды, объясняющее её назначение,
    особенности работы и возможные побочные эффекты.
    
    Args:
        required_param: Описание обязательного параметра
        optional_param: Описание необязательного параметра
        keyword_only_param: Описание параметра, который можно передать только по имени
        
    Returns:
        Описание возвращаемого значения
        
    Raises:
        ValueError: Когда возникает ошибка валидации
        RuntimeError: Когда возникает ошибка выполнения
        
    Examples:
        >>> command_name("value", 42, keyword_only_param=True)
        {'status': 'success', 'result': 'value_processed'}
    """
    # Логирование начала выполнения
    logger.debug(f"Executing command_name with params: {required_param}, {optional_param}, {keyword_only_param}")
    
    # Валидация параметров
    if not required_param:
        raise ValueError("required_param cannot be empty")
    
    if optional_param is not None and optional_param < 0:
        raise ValueError("optional_param must be non-negative")
    
    # Выполнение основной логики
    try:
        # Основная логика команды
        result = process_data(required_param, optional_param, keyword_only_param)
        
        # Логирование успешного выполнения
        logger.info(f"Command command_name executed successfully with result: {result}")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Error executing command command_name: {str(e)}", exc_info=True)
        
        # Проброс исключения для обработки выше
        raise RuntimeError(f"Failed to execute command: {str(e)}") from e
```

## Лучшие практики

### Типизация

1. **Используйте типизацию для всех параметров и возвращаемого значения**:

```python
def process_data(data: List[Dict[str, Any]], limit: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
    # ...
```

2. **Используйте сложные типы из модуля `typing`**:

```python
from typing import Dict, List, Optional, Union, Callable, TypeVar, Generic

T = TypeVar('T')

def filter_items(
    items: List[T],
    predicate: Callable[[T], bool]
) -> List[T]:
    # ...
```

3. **Определяйте свои типы для сложных структур**:

```python
from typing import Dict, List, TypedDict, Optional

class UserData(TypedDict):
    id: str
    name: str
    email: str
    roles: List[str]
    profile: Optional[Dict[str, str]]

def get_user(user_id: str) -> UserData:
    # ...
```

### Документация

1. **Используйте docstrings для описания команды, её параметров и возвращаемого значения**:

```python
def calculate_total(prices: List[float], discount: float = 0.0) -> float:
    """
    Рассчитывает общую стоимость с учетом скидки.
    
    Args:
        prices: Список цен товаров
        discount: Скидка в процентах (от 0.0 до 1.0)
        
    Returns:
        Общая стоимость со скидкой
        
    Raises:
        ValueError: Если скидка не в диапазоне [0, 1]
    """
```

2. **Добавляйте примеры использования в docstring**:

```python
def calculate_total(prices: List[float], discount: float = 0.0) -> float:
    """
    ...
    
    Examples:
        >>> calculate_total([10.0, 20.0, 30.0])
        60.0
        >>> calculate_total([10.0, 20.0, 30.0], discount=0.1)
        54.0
    """
```

### Валидация параметров

1. **Проверяйте корректность параметров в начале функции**:

```python
def update_user(user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """Обновляет информацию о пользователе."""
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    if email is not None and "@" not in email:
        raise ValueError("Invalid email format")
    
    # Основная логика...
```

2. **Используйте библиотеки для валидации сложных данных**:

```python
from pydantic import BaseModel, EmailStr, validator

class UserUpdateParams(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('user_id')
    def user_id_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('user_id cannot be empty')
        return v

def update_user(params: UserUpdateParams) -> Dict[str, Any]:
    # Pydantic уже выполнил валидацию
    # Основная логика...
```

### Обработка ошибок

1. **Используйте специфичные типы исключений**:

```python
def get_user(user_id: str) -> Dict[str, Any]:
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    user = db.find_user(user_id)
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found")
    
    return user
```

2. **Сохраняйте контекст ошибки с помощью цепочки исключений**:

```python
def process_order(order_id: str) -> Dict[str, Any]:
    try:
        order = get_order(order_id)
        # Обработка заказа...
    except OrderNotFoundError as e:
        raise ProcessingError(f"Failed to process order {order_id}") from e
    except Exception as e:
        raise ProcessingError(f"Unexpected error while processing order {order_id}") from e
```

### Логирование

1. **Используйте логирование для отслеживания хода выполнения команды**:

```python
import logging

logger = logging.getLogger(__name__)

def complex_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Starting complex operation with data: {data}")
    
    try:
        # Шаг 1
        logger.debug("Performing step 1")
        result_1 = step_1(data)
        
        # Шаг 2
        logger.debug("Performing step 2")
        result_2 = step_2(result_1)
        
        # Финальный шаг
        logger.debug("Performing final step")
        final_result = final_step(result_2)
        
        logger.info(f"Complex operation completed successfully with result: {final_result}")
        return final_result
    except Exception as e:
        logger.error(f"Error during complex operation: {str(e)}", exc_info=True)
        raise
```

### Тестирование команд

1. **Пишите юнит-тесты для команд**:

```python
import pytest
from myapp.commands import calculate_total

def test_calculate_total_basic():
    result = calculate_total([10.0, 20.0, 30.0])
    assert result == 60.0

def test_calculate_total_with_discount():
    result = calculate_total([10.0, 20.0, 30.0], discount=0.1)
    assert result == 54.0

def test_calculate_total_empty_list():
    result = calculate_total([])
    assert result == 0.0

def test_calculate_total_invalid_discount():
    with pytest.raises(ValueError):
        calculate_total([10.0, 20.0], discount=1.5)
```

2. **Используйте параметризированные тесты**:

```python
import pytest
from myapp.commands import calculate_total

@pytest.mark.parametrize("prices, discount, expected", [
    ([10.0, 20.0, 30.0], 0.0, 60.0),
    ([10.0, 20.0, 30.0], 0.1, 54.0),
    ([10.0], 0.5, 5.0),
    ([], 0.0, 0.0),
])
def test_calculate_total(prices, discount, expected):
    result = calculate_total(prices, discount)
    assert result == expected

@pytest.mark.parametrize("invalid_discount", [-0.1, 1.1, 2.0])
def test_calculate_total_invalid_discount(invalid_discount):
    with pytest.raises(ValueError):
        calculate_total([10.0], discount=invalid_discount)
```

## Организация команд

### Группировка по модулям

Для больших проектов рекомендуется группировать команды по функциональности:

```
commands/
  __init__.py
  users/
    __init__.py
    create.py
    update.py
    delete.py
  orders/
    __init__.py
    create.py
    process.py
    cancel.py
  products/
    __init__.py
    ...
```

В файле `commands/__init__.py` можно экспортировать все команды:

```python
# commands/__init__.py
from .users.create import create_user
from .users.update import update_user
from .users.delete import delete_user
from .orders.create import create_order
from .orders.process import process_order
from .orders.cancel import cancel_order
# ...

__all__ = [
    'create_user',
    'update_user',
    'delete_user',
    'create_order',
    'process_order',
    'cancel_order',
    # ...
]
```

### Регистрация команд

При большом количестве команд рекомендуется использовать автоматическую регистрацию:

```python
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
import commands

dispatcher = CommandDispatcher()
registry = CommandRegistry(dispatcher)

# Регистрация всех команд из модуля
registry.scan_module(commands, recursive=True)
```

## Примеры команд

### Простая команда

```python
def add_numbers(a: int, b: int) -> int:
    """
    Складывает два числа.
    
    Args:
        a: Первое число
        b: Второе число
        
    Returns:
        Сумма чисел
    """
    return a + b
```

### Команда с валидацией

```python
def calculate_discount(price: float, percentage: float) -> float:
    """
    Рассчитывает сумму скидки.
    
    Args:
        price: Исходная цена (должна быть положительной)
        percentage: Процент скидки (от 0 до 100)
        
    Returns:
        Сумма скидки
        
    Raises:
        ValueError: Если цена отрицательная или процент скидки вне диапазона [0, 100]
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")
    
    return price * (percentage / 100)
```

### Команда с внешними зависимостями

```python
import logging
from typing import Dict, Any, Optional
from database import get_database_connection

logger = logging.getLogger(__name__)

def get_user_profile(user_id: str, include_private: bool = False) -> Dict[str, Any]:
    """
    Получает профиль пользователя из базы данных.
    
    Args:
        user_id: Идентификатор пользователя
        include_private: Включать ли приватные данные
        
    Returns:
        Профиль пользователя
        
    Raises:
        ValueError: Если идентификатор пользователя пустой
        UserNotFoundError: Если пользователь не найден
        DatabaseError: При ошибке работы с базой данных
    """
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    logger.info(f"Retrieving user profile for user_id={user_id}")
    
    try:
        db = get_database_connection()
        user = db.users.find_one({"_id": user_id})
        
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        # Формирование результата
        profile = {
            "id": user["_id"],
            "username": user["username"],
            "name": user["name"],
            "created_at": user["created_at"].isoformat()
        }
        
        # Добавление приватных данных, если требуется
        if include_private:
            profile.update({
                "email": user["email"],
                "phone": user["phone"],
                "last_login": user.get("last_login", {}).get("timestamp", "").isoformat()
            })
        
        logger.info(f"Successfully retrieved user profile for user_id={user_id}")
        return profile
    
    except UserNotFoundError:
        logger.warning(f"User with id {user_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile for user_id={user_id}: {str(e)}", exc_info=True)
        raise DatabaseError(f"Failed to retrieve user profile: {str(e)}") from e
```

### Асинхронная команда

```python
import logging
import asyncio
from typing import Dict, Any, List
from database import get_async_database_connection

logger = logging.getLogger(__name__)

async def search_products(
    query: str,
    categories: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Выполняет поиск товаров по различным критериям.
    
    Args:
        query: Поисковый запрос
        categories: Список категорий для фильтрации
        min_price: Минимальная цена
        max_price: Максимальная цена
        limit: Максимальное количество результатов
        offset: Смещение результатов для пагинации
        
    Returns:
        Словарь с результатами поиска и метаданными
    """
    logger.info(f"Searching products with query: {query}, categories: {categories}, "
                f"price range: {min_price}-{max_price}, limit: {limit}, offset: {offset}")
    
    # Формирование фильтра
    filter_query = {"$text": {"$search": query}}
    
    if categories:
        filter_query["category"] = {"$in": categories}
    
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    
    if price_filter:
        filter_query["price"] = price_filter
    
    try:
        # Получение соединения с базой данных
        db = await get_async_database_connection()
        
        # Выполнение запроса
        cursor = db.products.find(filter_query).sort("relevance", -1).skip(offset).limit(limit)
        products = await cursor.to_list(length=limit)
        
        # Получение общего количества результатов
        total_count = await db.products.count_documents(filter_query)
        
        # Формирование результата
        result = {
            "items": products,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(products) < total_count
        }
        
        logger.info(f"Found {total_count} products for query: {query}")
        return result
    
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}", exc_info=True)
        raise SearchError(f"Failed to search products: {str(e)}") from e
```

## Рекомендации по именованию команд

1. **Используйте глаголы для обозначения действий**:
   - `create_user`
   - `update_profile`
   - `delete_item`
   - `process_payment`

2. **Будьте консистентны в именовании**:
   - `get_user`, `get_order`, `get_product` (не `fetch_user`, `retrieve_order`)
   - `create_user`, `create_order`, `create_product` (не `add_user`, `new_order`)

3. **Избегайте сокращений и аббревиатур**:
   - `calculate_total` вместо `calc_total`
   - `verify_email` вместо `ver_email`

4. **Используйте snake_case для имен команд**:
   - `process_payment` вместо `processPayment`
   - `update_user_profile` вместо `updateUserProfile`

5. **Включайте в название объект, над которым выполняется действие**:
   - `create_user` вместо просто `create`
   - `send_notification` вместо просто `send`

## Совместимость команд

При разработке и изменении команд соблюдайте правила совместимости:

1. **Не меняйте тип возвращаемого значения**
2. **Не удаляйте существующие параметры**
3. **Добавляйте только необязательные параметры**
4. **Не меняйте семантику параметров**
5. **Не изменяйте логику работы команды без изменения её названия**

Если требуется несовместимое изменение:

1. Создайте новую команду с другим именем
2. Пометьте старую команду как устаревшую (deprecated)
3. В документации укажите рекомендацию по миграции 