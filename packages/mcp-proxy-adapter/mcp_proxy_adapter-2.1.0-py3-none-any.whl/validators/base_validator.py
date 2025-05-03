"""
Base class for command validators.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple

class BaseValidator(ABC):
    """
    Base class for all command validators.
    
    Defines a common interface for validating command handler functions,
    their docstrings, metadata, and other aspects.
    """
    
    @abstractmethod
    def validate(self, *args, **kwargs) -> Tuple[bool, List[str]]:
        """
        Main validation method.
        
        Returns:
            Tuple[bool, List[str]]: Validity flag and list of errors
        """
        pass 