#!/usr/bin/env python3
"""
Инструмент для автоматической регистрации всех команд с метаданными.
Проходит по всем модулям с командами и регистрирует их в диспетчере.
"""
import os
import importlib
import inspect
import sys
from typing import Dict, Any, Optional, List, Tuple, get_type_hints, get_origin, get_args
import docstring_parser

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.command_dispatcher import dispatcher
import commands
from commands import get_all_commands, get_command_names

def map_type_to_openapi(type_hint) -> str:
    """
    Преобразует тип Python в тип OpenAPI.
    
    Args:
        type_hint: Тип Python
        
    Returns:
        str: Строковое представление типа OpenAPI
    """
    # Проверяем на None
    if type_hint is None:
        return "object"
    
    # Обрабатываем примитивные типы
    primitives = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        Any: "object"
    }
    
    if type_hint in primitives:
        return primitives[type_hint]
    
    # Проверяем на обобщенные типы
    origin = get_origin(type_hint)
    if origin is not None:
        # Обрабатываем List[X], Dict[X, Y] и т.д.
        if origin in (list, List):
            return "array"
        elif origin in (dict, Dict):
            return "object"
        elif origin is Union:
            # Для Union берем первый тип, который не None
            args = get_args(type_hint)
            for arg in args:
                if arg is not type(None):
                    return map_type_to_openapi(arg)
            return "object"
    
    # По умолчанию возвращаем object
    return "object"

def extract_param_types_from_handler(handler) -> Dict[str, str]:
    """
    Извлекает типы параметров из аннотаций функции.
    
    Args:
        handler: Функция-обработчик
        
    Returns:
        Dict[str, str]: Словарь {имя_параметра: тип_openapi}
    """
    param_types = {}
    
    try:
        # Получаем аннотации типов
        type_hints = get_type_hints(handler)
        
        # Преобразуем типы Python в типы OpenAPI
        for param_name, param_type in type_hints.items():
            # Пропускаем return тип
            if param_name == 'return':
                continue
                
            # Преобразуем тип Python в тип OpenAPI
            openapi_type = map_type_to_openapi(param_type)
            param_types[param_name] = openapi_type
    except Exception as e:
        print(f"  ⚠️ Ошибка при извлечении типов параметров: {str(e)}")
    
    return param_types

def validate_docstring(handler, command_name: str) -> Tuple[bool, List[str]]:
    """
    Проверяет соответствие докстринга функции-обработчика её формальным параметрам.
    
    Args:
        handler: Функция-обработчик команды
        command_name: Имя команды
        
    Returns:
        Tuple[bool, List[str]]: Флаг валидности и список ошибок
    """
    errors = []
    
    # Получаем формальные параметры функции
    try:
        sig = inspect.signature(handler)
        formal_params = list(sig.parameters.keys())
        
        # Пропускаем параметр self для методов
        if formal_params and formal_params[0] == 'self':
            formal_params = formal_params[1:]
            
        # Парсим докстринг
        docstring = handler.__doc__ or ""
        parsed_doc = docstring_parser.parse(docstring)
        
        # Проверяем наличие описания функции
        if not parsed_doc.short_description and not parsed_doc.long_description:
            errors.append(f"Отсутствует описание функции {command_name}")
        
        # Получаем параметры из докстринга
        doc_params = {param.arg_name: param for param in parsed_doc.params}
        
        # Проверяем, что все формальные параметры описаны в докстринге
        for param in formal_params:
            if param not in doc_params and param != 'params':  # 'params' - особый случай, может быть словарём всех параметров
                errors.append(f"Параметр '{param}' не описан в докстринге функции {command_name}")
        
        # Проверяем наличие returns в докстринге
        if not parsed_doc.returns and not any(t.type_name == 'Returns' for t in parsed_doc.meta):
            errors.append(f"Отсутствует описание возвращаемого значения в докстринге функции {command_name}")
        
        # Проверяем аннотации типов
        type_hints = get_type_hints(handler)
        for param in formal_params:
            if param not in type_hints and param != 'params':
                errors.append(f"Отсутствует аннотация типа для параметра '{param}' в функции {command_name}")
        
        return len(errors) == 0, errors
    except Exception as e:
        return False, [f"Ошибка при валидации докстринга: {str(e)}"]

def extract_metadata_from_command(command_name: str, command_info: Dict[str, Any], handler=None):
    """
    Извлекает метаданные из информации о команде и сигнатуры функции-обработчика.
    
    Args:
        command_name: Имя команды
        command_info: Информация о команде
        handler: Функция-обработчик (опционально)
        
    Returns:
        dict: Метаданные для регистрации команды
    """
    metadata = {
        "description": command_info.get("description", f"Команда {command_name}"),
        "summary": command_name.replace("_", " ").title(),
        "params": {}
    }
    
    # Если есть обработчик, извлекаем типы параметров из него
    param_types_from_handler = {}
    if handler:
        param_types_from_handler = extract_param_types_from_handler(handler)
    
    # Если в команде определены параметры, добавляем их
    if "parameters" in command_info:
        for param_name, param_info in command_info["parameters"].items():
            # Начинаем с типа из метаданных команды
            param_type = param_info.get("type", "string")
            
            # Если есть тип из аннотации функции, используем его
            if param_name in param_types_from_handler:
                param_type = param_types_from_handler[param_name]
                
            metadata["params"][param_name] = {
                "type": param_type,
                "description": param_info.get("description", f"Параметр {param_name}"),
                "required": param_info.get("required", False)
            }
            
            if "default" in param_info:
                metadata["params"][param_name]["default"] = param_info["default"]
    # Если параметры не определены, но есть обработчик, извлекаем их из обработчика
    elif handler:
        # Получаем сигнатуру функции
        sig = inspect.signature(handler)
        
        # Проходим по параметрам функции
        for param_name, param in sig.parameters.items():
            # Пропускаем self для методов
            if param_name == 'self':
                continue
                
            # Если параметр называется params, предполагаем, что это словарь всех параметров
            if param_name == 'params':
                # В этом случае метаданные недоступны из сигнатуры
                continue
                
            # Определяем, является ли параметр обязательным
            required = param.default == inspect.Parameter.empty
            
            # Определяем тип параметра
            param_type = "string"  # По умолчанию
            if param_name in param_types_from_handler:
                param_type = param_types_from_handler[param_name]
                
            # Получаем описание из докстринга
            description = f"Параметр {param_name}"
            try:
                # Парсим докстринг
                docstring = handler.__doc__ or ""
                parsed_doc = docstring_parser.parse(docstring)
                
                # Ищем описание параметра
                for doc_param in parsed_doc.params:
                    if doc_param.arg_name == param_name:
                        description = doc_param.description or description
                        break
            except Exception:
                pass
                
            # Добавляем параметр в метаданные
            metadata["params"][param_name] = {
                "type": param_type,
                "description": description,
                "required": required
            }
            
            # Добавляем значение по умолчанию, если есть
            if param.default != inspect.Parameter.empty:
                metadata["params"][param_name]["default"] = param.default
    
    return metadata

def validate_handler_metadata(handler, command_name: str, command_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Проверяет соответствие метаданных команды формальным параметрам функции-обработчика.
    
    Args:
        handler: Функция-обработчик команды
        command_name: Имя команды
        command_info: Информация о команде
        
    Returns:
        Tuple[bool, List[str]]: Флаг валидности и список ошибок
    """
    errors = []
    
    # Получаем формальные параметры функции
    sig = inspect.signature(handler)
    formal_params = list(sig.parameters.keys())
    
    # Пропускаем параметр self для методов
    if formal_params and formal_params[0] == 'self':
        formal_params = formal_params[1:]
    
    # Если функция принимает просто словарь params, пропускаем проверку
    if len(formal_params) == 1 and formal_params[0] == 'params':
        return True, []
    
    # Получаем типы параметров из аннотаций функции
    param_types = extract_param_types_from_handler(handler)
    
    # Проверяем соответствие метаданных команды формальным параметрам
    if "parameters" in command_info:
        for param_name, param_info in command_info["parameters"].items():
            # Проверяем наличие параметра в сигнатуре функции
            if param_name not in formal_params:
                errors.append(f"Параметр '{param_name}' указан в метаданных, но отсутствует в сигнатуре функции {command_name}")
                continue
            
            # Проверяем соответствие типов
            if param_name in param_types and "type" in param_info:
                openapi_type = param_info["type"]
                annotation_type = param_types[param_name]
                
                if openapi_type != annotation_type:
                    errors.append(f"Тип параметра '{param_name}' в метаданных ({openapi_type}) не соответствует аннотации функции ({annotation_type})")
    
        # Проверяем, что все обязательные формальные параметры указаны в метаданных
        for param_name, param in sig.parameters.items():
            if param_name != 'self' and param.default == inspect.Parameter.empty:
                if param_name not in command_info.get("parameters", {}):
                    errors.append(f"Обязательный параметр '{param_name}' не указан в метаданных команды {command_name}")
    
    return len(errors) == 0, errors

def find_handler_function(command_name: str):
    """
    Находит функцию-обработчик для команды.
    
    Args:
        command_name: Имя команды
        
    Returns:
        function: Функция-обработчик команды или None, если не найдена
    """
    # Проверяем различные варианты имени функции
    function_names = [
        command_name,               # имя_команды
        f"{command_name}_command",  # имя_команды_command
        f"execute_{command_name}",  # execute_имя_команды
        "execute"                   # execute (общий обработчик)
    ]
    
    # Пути для поиска функций
    command_paths = [
        f"commands.metadata.{command_name}",
        f"commands.search.{command_name}",
        f"commands.index.{command_name}",
        f"handlers.{command_name}_handlers",
        f"rpc.handlers"
    ]
    
    # Пытаемся импортировать модули и найти функцию
    for path in command_paths:
        try:
            module = importlib.import_module(path)
            
            for func_name in function_names:
                if hasattr(module, func_name):
                    return getattr(module, func_name)
        except (ImportError, ModuleNotFoundError):
            continue
    
    return None

def register_command(command_name: str, command_info: Dict[str, Any], strict: bool = True, auto_fix: bool = False):
    """
    Регистрирует команду в диспетчере с метаданными.
    
    Args:
        command_name: Имя команды
        command_info: Информация о команде
        strict: Если True, прерывает регистрацию при обнаружении ошибок
        auto_fix: Если True, пытается автоматически исправить несоответствия
    """
    # Находим функцию-обработчик
    handler = find_handler_function(command_name)
    
    if not handler:
        print(f"⚠️ Не удалось найти обработчик для команды '{command_name}'")
        return False
    
    # Проверяем соответствие документации и формальных параметров
    is_valid_doc, doc_errors = validate_docstring(handler, command_name)
    is_valid_meta, meta_errors = validate_handler_metadata(handler, command_name, command_info)
    
    # Выводим все ошибки
    if not is_valid_doc or not is_valid_meta:
        print(f"🚫 Ошибки в команде '{command_name}':")
        
        for error in doc_errors:
            print(f"   - {error}")
            
        for error in meta_errors:
            print(f"   - {error}")
        
        # В строгом режиме без автоисправления пропускаем регистрацию
        if strict and not auto_fix:
            print(f"❌ Регистрация команды '{command_name}' пропущена из-за ошибок")
            return False
    
    # Извлекаем метаданные, учитывая аннотации функции
    metadata = extract_metadata_from_command(command_name, command_info, handler if auto_fix else None)
    
    # Регистрируем команду в диспетчере
    print(f"📝 Регистрируем команду '{command_name}'")
    dispatcher.register_handler(
        command=command_name,
        handler=handler,
        description=metadata["description"],
        summary=metadata["summary"],
        params=metadata["params"]
    )
    
    return True

def register_all_commands(strict: bool = True, auto_fix: bool = False):
    """
    Регистрирует все команды в диспетчере.
    
    Args:
        strict: Если True, прерывает регистрацию команды при обнаружении ошибок
        auto_fix: Если True, пытается автоматически исправить несоответствия
    """
    # Получаем все команды
    commands_info = get_all_commands()
    
    # Счетчики
    successful = 0
    failed = 0
    skipped = 0
    
    # Регистрируем каждую команду
    for command_name, command_info in commands_info.items():
        # Пропускаем команду help, она уже зарегистрирована
        if command_name == "help":
            skipped += 1
            continue
            
        if register_command(command_name, command_info, strict, auto_fix):
            successful += 1
        else:
            failed += 1
    
    print(f"\n✅ Итоги регистрации команд:")
    print(f"   - Успешно: {successful}")
    print(f"   - С ошибками: {failed}")
    print(f"   - Пропущено: {skipped}")
    print(f"   - Всего в диспетчере: {len(dispatcher.get_valid_commands())}")
    
    if failed > 0 and strict:
        print("\n⚠️ ВНИМАНИЕ: Некоторые команды не были зарегистрированы из-за ошибок")
        print("   Используйте register_all_commands(strict=False) для регистрации всех команд")
        print("   Или register_all_commands(auto_fix=True) для автоматического исправления ошибок")

if __name__ == "__main__":
    print("🔍 Начинаем регистрацию команд...")
    
    # Проверяем аргументы командной строки
    strict_mode = True
    auto_fix_mode = False
    
    # Обрабатываем аргументы командной строки
    if len(sys.argv) > 1:
        if "--no-strict" in sys.argv:
            strict_mode = False
            print("⚙️ Запуск в нестрогом режиме: команды с ошибками будут зарегистрированы")
        
        if "--auto-fix" in sys.argv:
            auto_fix_mode = True
            print("⚙️ Режим автоисправления: типы и описания будут извлечены из аннотаций функций")
    else:
        print("⚙️ Запуск в строгом режиме: команды с ошибками не будут зарегистрированы")
        print("  Используйте --no-strict для отключения строгого режима")
        print("  Используйте --auto-fix для автоматического исправления ошибок")
    
    register_all_commands(strict=strict_mode, auto_fix=auto_fix_mode) 