# Command Development Guide

This guide describes best practices and recommendations for developing commands for the Command Registry system.

## Core Principles

When developing commands for Command Registry, follow these principles:

1. **Single Responsibility**: a command should do one thing and do it well
2. **Declarative**: a command should be self-documenting through type hints and docstrings
3. **Independence**: a command should not depend on other commands
4. **Idempotency**: repeated execution of a command with the same parameters should yield identical results
5. **Validation**: a command should validate input data before execution

## Command Structure

Recommended command structure:

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
    Brief command description (one sentence).
    
    Detailed command description explaining its purpose,
    operational features, and possible side effects.
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        keyword_only_param: Description of keyword-only parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation error occurs
        RuntimeError: When execution error occurs
        
    Examples:
        >>> command_name("value", 42, keyword_only_param=True)
        {'status': 'success', 'result': 'value_processed'}
    """
    # Log execution start
    logger.debug(f"Executing command_name with params: {required_param}, {optional_param}, {keyword_only_param}")
    
    # Parameter validation
    if not required_param:
        raise ValueError("required_param cannot be empty")
    
    if optional_param is not None and optional_param < 0:
        raise ValueError("optional_param must be non-negative")
    
    # Execute main logic
    try:
        # Main command logic
        result = process_data(required_param, optional_param, keyword_only_param)
        
        # Log successful execution
        logger.info(f"Command command_name executed successfully with result: {result}")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        # Log error
        logger.error(f"Error executing command command_name: {str(e)}", exc_info=True)
        
        # Propagate exception for handling above
        raise RuntimeError(f"Failed to execute command: {str(e)}") from e
```

## Best Practices

### Type Hints

1. **Use type hints for all parameters and return values**:

```python
def process_data(data: List[Dict[str, Any]], limit: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
    # ...
```

2. **Use complex types from the `typing` module**:

```python
from typing import Dict, List, Optional, Union, Callable, TypeVar, Generic

T = TypeVar('T')

def filter_items(
    items: List[T],
    predicate: Callable[[T], bool]
) -> List[T]:
    # ...
```

3. **Define your own types for complex structures**:

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

### Documentation

1. **Use docstrings to describe the command, its parameters, and return value**:

```python
def calculate_total(prices: List[float], discount: float = 0.0) -> float:
    """
    Calculates total cost with discount.
    
    Args:
        prices: List of item prices
        discount: Discount percentage (from 0.0 to 1.0)
        
    Returns:
        Total cost with discount
        
    Raises:
        ValueError: If discount is not in range [0, 1]
    """
```

2. **Add usage examples in docstring**:

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

### Parameter Validation

1. **Check parameter correctness at the beginning of the function**:

```python
def update_user(user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """Updates user information."""
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    if email is not None and "@" not in email:
        raise ValueError("Invalid email format")
    
    # Main logic...
```

2. **Use libraries for complex data validation**:

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
    # Pydantic has already performed validation
    # Main logic...
```

### Error Handling

1. **Use specific exception types**:

```python
def get_user(user_id: str) -> Dict[str, Any]:
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    user = db.find_user(user_id)
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found")
    
    return user
```

2. **Preserve error context using exception chaining**:

```python
def process_order(order_id: str) -> Dict[str, Any]:
    try:
        order = get_order(order_id)
        # Order processing...
    except OrderNotFoundError as e:
        raise ProcessingError(f"Failed to process order {order_id}") from e
    except Exception as e:
        raise ProcessingError(f"Unexpected error while processing order {order_id}") from e
```

### Logging

1. **Use logging to track command execution progress**:

```python
import logging

logger = logging.getLogger(__name__)

def complex_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Starting complex operation with data: {data}")
    
    try:
        # Step 1
        logger.debug("Performing step 1")
        result_1 = step_1(data)
        
        # Step 2
        logger.debug("Performing step 2")
        result_2 = step_2(result_1)
        
        # Final step
        logger.debug("Performing final step")
        final_result = final_step(result_2)
``` 