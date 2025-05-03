"""
Адаптеры Command Registry
========================

Адаптеры обеспечивают интеграцию Command Registry с различными протоколами и системами.
Они преобразуют команды из реестра в формат, понятный другим системам.

Доступные адаптеры:
- RESTAdapter: Создает REST API эндпоинты
- MCPProxyAdapter: Интегрирует с MCPProxy для работы с инструментами моделей ИИ
"""

from command_registry.adapters.rest_adapter import RESTAdapter
from ..adapter import MCPProxyAdapter  # Импортируем из основного модуля adapter.py

__all__ = ['RESTAdapter', 'MCPProxyAdapter'] 