"""
Генератор REST API на основе команд и их метаданных.
"""
from typing import Dict, Any, Optional, List, Callable
import inspect
import logging
from command_registry.dispatchers.base_dispatcher import BaseDispatcher

logger = logging.getLogger("command_registry")

class RestApiGenerator:
    """
    Генератор REST API для FastAPI на основе команд.
    
    Этот класс создает REST эндпоинты для FastAPI на основе
    зарегистрированных команд и их метаданных.
    """
    
    def __init__(self, app, dispatcher: Optional[BaseDispatcher] = None, prefix: str = ""):
        """
        Инициализирует генератор REST API.
        
        Args:
            app: Экземпляр FastAPI приложения
            dispatcher: Диспетчер команд для доступа к метаданным
            prefix: Префикс для всех эндпоинтов (например, "/api")
        """
        self.app = app
        self.dispatcher = dispatcher
        self.prefix = prefix.rstrip("/")
        
        # Словарь для хранения соответствия между командами и эндпоинтами
        self._endpoints = {}
    
    def set_dispatcher(self, dispatcher: BaseDispatcher) -> None:
        """
        Устанавливает диспетчер команд.
        
        Args:
            dispatcher: Диспетчер команд
        """
        self.dispatcher = dispatcher
    
    def generate_endpoints(self) -> None:
        """
        Генерирует REST эндпоинты для всех команд.
        
        Создает эндпоинты для всех команд, зарегистрированных в диспетчере,
        включая автоматический хелп-эндпоинт.
        """
        if not self.dispatcher:
            logger.warning("Диспетчер команд не установлен, невозможно сгенерировать эндпоинты")
            return
        
        # Получаем информацию о всех командах
        commands_info = self.dispatcher.get_commands_info()
        
        # Генерируем эндпоинты для каждой команды
        for command, info in commands_info.items():
            # Генерируем путь для эндпоинта
            path = f"{self.prefix}/{command.replace('_', '-')}"
            
            # Генерируем обработчик для эндпоинта
            endpoint = self._create_endpoint_handler(command, info)
            
            # Регистрируем эндпоинт в FastAPI
            self.app.post(
                path,
                summary=info.get("summary", command),
                description=info.get("description", ""),
                tags=self._get_tags_for_command(command)
            )(endpoint)
            
            # Сохраняем соответствие между командой и эндпоинтом
            self._endpoints[command] = path
            
            logger.debug(f"Сгенерирован REST эндпоинт для команды '{command}': {path}")
        
        # Генерируем хелп-эндпоинт
        self._generate_help_endpoint()
    
    def _create_endpoint_handler(self, command: str, info: Dict[str, Any]) -> Callable:
        """
        Создает функцию-обработчик для эндпоинта.
        
        Args:
            command: Имя команды
            info: Метаданные команды
            
        Returns:
            Callable: Функция-обработчик для FastAPI
        """
        dispatcher = self.dispatcher
        
        # Создаем динамическую функцию-обработчик
        async def endpoint(**kwargs):
            try:
                # Выполняем команду через диспетчер
                result = dispatcher.execute(command, **kwargs)
                
                # Если результат корутина, ожидаем его завершения
                if inspect.iscoroutine(result):
                    result = await result
                
                return result
            except Exception as e:
                # В случае ошибки возвращаем структурированный ответ с ошибкой
                return {
                    "error": {
                        "message": str(e),
                        "code": 500
                    }
                }
        
        # Устанавливаем имя функции и докстринг
        endpoint.__name__ = f"{command}_endpoint"
        endpoint.__doc__ = info.get("description", "")
        
        # Возвращаем функцию-обработчик
        return endpoint
    
    def _generate_help_endpoint(self) -> None:
        """
        Генерирует хелп-эндпоинт для API.
        
        Создает специальный эндпоинт /help, который возвращает информацию
        о всех доступных командах и их эндпоинтах.
        """
        app = self.app
        dispatcher = self.dispatcher
        endpoints = self._endpoints
        
        # Путь для хелп-эндпоинта
        help_path = f"{self.prefix}/help"
        
        # Функция-обработчик для хелп-эндпоинта
        async def help_endpoint(command: Optional[str] = None):
            if command:
                # Если указана конкретная команда, возвращаем информацию о ней
                command_info = dispatcher.get_command_info(command)
                if not command_info:
                    return {
                        "error": f"Команда '{command}' не найдена",
                        "available_commands": list(dispatcher.get_valid_commands())
                    }
                
                # Добавляем URL эндпоинта
                endpoint_url = endpoints.get(command)
                if endpoint_url:
                    command_info["endpoint"] = endpoint_url
                
                return {
                    "command": command,
                    "info": command_info
                }
            
            # Иначе возвращаем информацию о всех командах
            commands_info = {}
            for cmd, info in dispatcher.get_commands_info().items():
                endpoint_url = endpoints.get(cmd)
                commands_info[cmd] = {
                    "summary": info.get("summary", ""),
                    "description": info.get("description", ""),
                    "endpoint": endpoint_url,
                    "params_count": len(info.get("params", {}))
                }
            
            return {
                "commands": commands_info,
                "total": len(commands_info),
                "base_url": self.prefix,
                "note": "Для получения подробной информации о команде используйте параметр 'command'"
            }
        
        # Регистрируем хелп-эндпоинт в FastAPI
        app.get(
            help_path,
            summary="API справка",
            description="Возвращает информацию о доступных командах и эндпоинтах API",
            tags=["help"]
        )(help_endpoint)
        
        logger.debug(f"Сгенерирован хелп-эндпоинт: {help_path}")
    
    def _get_tags_for_command(self, command: str) -> List[str]:
        """
        Определяет теги для команды.
        
        Args:
            command: Имя команды
            
        Returns:
            List[str]: Список тегов для документации OpenAPI
        """
        # Простая эвристика для определения категории команды
        if command.startswith(("get_", "search_", "find_", "list_")):
            return ["query"]
        elif command.startswith(("create_", "add_", "insert_")):
            return ["mutation", "create"]
        elif command.startswith(("update_", "change_", "modify_")):
            return ["mutation", "update"]
        elif command.startswith(("delete_", "remove_")):
            return ["mutation", "delete"]
        else:
            # Используем первую часть имени команды в качестве тега
            parts = command.split("_")
            return [parts[0]] if parts else ["other"] 