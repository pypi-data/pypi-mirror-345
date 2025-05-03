# Command Testing Guide

This guide describes approaches and best practices for testing commands registered in Command Registry.

## Why Testing Commands is Important

Commands in Command Registry often represent key business operations of the application. Testing them has the following advantages:

1. **Reliability** - verifying command functionality in various conditions
2. **Documentation** - tests demonstrate expected command behavior
3. **Regression** - preventing regressions when making changes
4. **Refactoring** - ability to safely improve command code
5. **Validation** - verifying correct handling of input parameters and errors

## Testing Levels

### 1. Unit Testing

Testing individual command functions in isolation from other components.

```python
import pytest
from myapp.commands.math_commands import add_numbers

def test_add_numbers_basic():
    # Basic scenario
    result = add_numbers(5, 3)
    assert result == 8
    
def test_add_numbers_negative():
    # Working with negative numbers
    result = add_numbers(-5, 3)
    assert result == -2
    
def test_add_numbers_zero():
    # Working with zeros
    result = add_numbers(0, 0)
    assert result == 0
```

### 2. Integration Testing

Testing commands with real dependencies or their mocks.

```python
import pytest
from unittest.mock import MagicMock, patch
from myapp.commands.user_commands import get_user_data

@pytest.fixture
def mock_db():
    """Fixture for creating database mock."""
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
    # Setup mock
    get_database_mock.return_value = mock_db
    
    # Call command
    result = get_user_data("user123")
    
    # Assertions
    assert result["id"] == "user123"
    assert result["name"] == "Test User"
    assert "email" in result
    
    # Verify DB call with correct parameters
    mock_db.users.find_one.assert_called_once_with({"id": "user123"})
```

### 3. Testing Through Command Registry

Testing commands through Command Registry interface.

```python
import pytest
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
from myapp.commands.math_commands import add_numbers, subtract_numbers

@pytest.fixture
def registry():
    """Fixture for creating CommandRegistry with registered commands."""
    registry = CommandRegistry(CommandDispatcher())
    registry.register_command("add", add_numbers)
    registry.register_command("subtract", subtract_numbers)
    return registry

def test_registry_add_command(registry):
    # Execute command through registry
    result = registry.execute("add", {"a": 10, "b": 5})
    assert result == 15
    
def test_registry_subtract_command(registry):
    # Execute command through registry
    result = registry.execute("subtract", {"a": 10, "b": 5})
    assert result == 5
    
def test_command_not_found(registry):
    # Check handling of non-existent command
    with pytest.raises(ValueError, match="Command 'multiply' not found"):
        registry.execute("multiply", {"a": 10, "b": 5})
```

### 4. E2E Testing Through API

Testing commands through external interfaces (REST, JSON-RPC, etc.).

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app  # FastAPI application with registered commands

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

## Testing Using Parameterization

Parameterization allows testing multiple scenarios with different inputs and expectations.

```python
import pytest
from myapp.commands.math_commands import calculate_total

@pytest.mark.parametrize("prices, discount, expected", [
    ([10, 20, 30], 0, 60),       # No discount
    ([10, 20, 30], 10, 54),      # 10% discount
    ([100], 50, 50),            # 50% discount
    ([], 10, 0),                # Empty list
])
def test_calculate_total(prices, discount, expected):
    result = calculate_total(prices, discount)
    assert result == expected

@pytest.mark.parametrize("invalid_discount", [-10, 110, "invalid"])
def test_calculate_total_invalid_discount(invalid_discount):
    with pytest.raises(ValueError):
        calculate_total([10, 20], invalid_discount)
```

## Testing Asynchronous Commands

Use pytest-asyncio for testing asynchronous commands.

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from myapp.commands.async_commands import fetch_user_data

@pytest.mark.asyncio
@patch("myapp.commands.async_commands.get_async_database")
async def test_fetch_user_data(mock_get_db):
    # Create async mock
    mock_db = AsyncMock()
    mock_db.users.find_one.return_value = {"id": "user123", "name": "Test User"}
    mock_get_db.return_value = mock_db
    
    # Call async command
    result = await fetch_user_data("user123")
    
    # Check result
    assert result["id"] == "user123"
    assert result["name"] == "Test User"
    
    # Verify mock was called with correct parameters
    mock_db.users.find_one.assert_called_once_with({"id": "user123"})
```

## Testing Error Handling

```python
import pytest
from myapp.commands.user_commands import get_user_data
from myapp.exceptions import UserNotFoundError

@patch("myapp.commands.user_commands.get_database")
def test_get_user_data_not_found(mock_get_db):
    # Configure mock to return None (user not found)
    db_mock = MagicMock()
    db_mock.users.find_one.return_value = None
    mock_get_db.return_value = db_mock
    
    # Check that command raises expected exception
    with pytest.raises(UserNotFoundError, match="User with id 'unknown_user' not found"):
        get_user_data("unknown_user")
```

## Testing Parameter Validation

```python
import pytest
from myapp.commands.product_commands import update_product_price

def test_update_product_price_negative():
    # Check for negative price
    with pytest.raises(ValueError, match="Price cannot be negative"):
        update_product_price("product123", -10.0)
        
def test_update_product_price_invalid_id():
    # Check for empty product ID
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        update_product_price("", 10.0)
```

## Using Fixtures for Common Cases

```python
import pytest
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
import myapp.commands as commands

@pytest.fixture
def registry():
    """Creates CommandRegistry with all registered commands."""
    registry = CommandRegistry(CommandDispatcher())
    registry.scan_module(commands)
    return registry

@pytest.fixture
def mock_database():
    """Creates database mock with test data."""
    db = MagicMock()
    db.users.find_one.return_value = {"id": "user1", "name": "Test User"}
    db.products.find.return_value = [
        {"id": "product1", "name": "Test Product", "price": 10.0},
        {"id": "product2", "name": "Another Product", "price": 20.0}
    ]
    return db
``` 