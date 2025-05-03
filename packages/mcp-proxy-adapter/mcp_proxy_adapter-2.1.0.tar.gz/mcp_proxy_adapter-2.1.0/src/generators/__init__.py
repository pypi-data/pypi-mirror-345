"""
Генераторы API на основе команд и их метаданных.

Этот модуль содержит классы для автоматической генерации API интерфейсов
(REST, OpenAPI и др.) на основе зарегистрированных команд.
"""

from command_registry.generators.rest_api_generator import RestApiGenerator
from command_registry.generators.openapi_generator import OpenApiGenerator

__all__ = [
    'RestApiGenerator',
    'OpenApiGenerator',
] 