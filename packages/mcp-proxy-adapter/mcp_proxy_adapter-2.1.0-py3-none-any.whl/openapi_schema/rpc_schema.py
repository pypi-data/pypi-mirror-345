"""
Модуль для создания RPC части OpenAPI схемы.
Содержит описание единого RPC эндпоинта для вызова команд.
"""
from typing import Dict, Any

def get_rpc_schema() -> Dict[str, Any]:
    """
    Возвращает RPC часть OpenAPI схемы.
    
    Returns:
        dict: RPC часть OpenAPI схемы
    """
    return {
        "paths": {
            "/cmd": {
                "post": {
                    "summary": "Универсальный RPC эндпоинт для выполнения команд",
                    "description": "**Основной интерфейс взаимодействия с системой**. Эндпоинт принимает структурированный JSON-RPC 2.0 запрос с командой и параметрами, выполняет указанную операцию и возвращает результат. Поддерживает работу только с векторами размерности 384.",
                    "operationId": "executeCommand",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CommandRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Результат выполнения команды (независимо от успеха или ошибки). API всегда возвращает код 200 и использует поле 'success' для индикации успеха операции.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ApiResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "CommandRequest": {
                    "properties": {
                        "command": {
                            "type": "string",
                            "title": "Command",
                            "description": "Название команды для выполнения",
                            "enum": [
                                "health", "status", "help", "get_metadata", "get_text",
                                "create_record", "add_vector", "create_text_record", "add_text",
                                "search_records", "search_by_vector", "search_text_records",
                                "search_by_text", "filter_records", "filter", "delete_records",
                                "delete", "get_by_session_message"
                            ]
                        },
                        "params": {
                            "title": "Params",
                            "description": "Параметры команды",
                            "type": "object",
                            "additionalProperties": True
                        },
                        "jsonrpc": {
                            "type": "string",
                            "description": "Версия JSON-RPC протокола",
                            "enum": ["2.0"],
                            "default": "2.0"
                        },
                        "id": {
                            "type": "string",
                            "description": "Идентификатор запроса (опционально)"
                        }
                    },
                    "type": "object",
                    "required": ["command"],
                    "title": "CommandRequest",
                    "description": "Модель для запроса выполнения команды векторного хранилища"
                },
                "JsonRpcResponse": {
                    "type": "object",
                    "required": ["jsonrpc", "success"],
                    "properties": {
                        "jsonrpc": {
                            "type": "string",
                            "description": "Версия JSON-RPC протокола",
                            "enum": ["2.0"],
                            "default": "2.0"
                        },
                        "success": {
                            "type": "boolean",
                            "description": "Индикатор успешности операции",
                            "default": False
                        },
                        "result": {
                            "description": "Результат операции. Присутствует только при успешном выполнении (success=True). Формат результата зависит от выполненной команды."
                        },
                        "error": {
                            "description": "Информация об ошибке. Присутствует только при возникновении ошибки (success=\"false\").",
                            "type": "object",
                            "required": ["code", "message"],
                            "properties": {
                                "code": {
                                    "type": "integer",
                                    "description": "Код ошибки (внутренний код, не HTTP-статус)",
                                    "example": 400
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Текстовое описание ошибки",
                                    "example": "Запись не существует: ID 12345"
                                }
                            }
                        },
                        "id": {
                            "type": "string",
                            "description": "Идентификатор запроса (если был указан в запросе)"
                        }
                    },
                    "example": {
                        "jsonrpc": "2.0",
                        "success": True,
                        "result": {"id": "550e8400-e29b-41d4-a716-446655440000"}
                    }
                },
                "HealthParams": {
                    "type": "object",
                    "properties": {},
                    "title": "HealthParams",
                    "description": "Параметры для команды health"
                },
                "StatusParams": {
                    "type": "object",
                    "properties": {},
                    "title": "StatusParams",
                    "description": "Параметры для команды status"
                },
                "HelpParams": {
                    "type": "object",
                    "properties": {},
                    "title": "HelpParams",
                    "description": "Параметры для команды help"
                },
                "GetMetadataParams": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор записи"
                        }
                    },
                    "required": ["id"],
                    "title": "GetMetadataParams",
                    "description": "Параметры для команды get_metadata"
                },
                "GetTextParams": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор записи"
                        }
                    },
                    "required": ["id"],
                    "title": "GetTextParams",
                    "description": "Параметры для команды get_text"
                },
                "CreateRecordParams": {
                    "type": "object",
                    "properties": {
                        "vector": {
                            "$ref": "#/components/schemas/Vector"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Метаданные записи"
                        },
                        "session_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор сессии (опционально)"
                        },
                        "message_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор сообщения (опционально)"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Временная метка в формате ISO 8601 (опционально)"
                        }
                    },
                    "required": ["vector"],
                    "title": "CreateRecordParams",
                    "description": "Параметры для создания новой векторной записи"
                },
                "CreateTextRecordParams": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Текст для векторизации"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Метаданные записи"
                        },
                        "model": {
                            "type": "string",
                            "description": "Модель для векторизации (опционально)"
                        },
                        "session_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор сессии (опционально)"
                        },
                        "message_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор сообщения (опционально)"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Временная метка в формате ISO 8601 (опционально)"
                        }
                    },
                    "required": ["text"],
                    "title": "CreateTextRecordParams",
                    "description": "Параметры для создания новой текстовой записи"
                },
                "SearchRecordsParams": {
                    "type": "object",
                    "properties": {
                        "vector": {
                            "$ref": "#/components/schemas/Vector"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Максимальное количество результатов",
                            "default": 10
                        },
                        "threshold": {
                            "type": "number",
                            "description": "Порог схожести (от 0 до 1)",
                            "default": 0.7
                        }
                    },
                    "required": ["vector"],
                    "title": "SearchRecordsParams",
                    "description": "Параметры для поиска векторных записей"
                },
                "SearchTextRecordsParams": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Текст для поиска"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Максимальное количество результатов",
                            "default": 10
                        },
                        "threshold": {
                            "type": "number",
                            "description": "Порог схожести (от 0 до 1)",
                            "default": 0.7
                        }
                    },
                    "required": ["text"],
                    "title": "SearchTextRecordsParams",
                    "description": "Параметры для поиска текстовых записей"
                },
                "FilterRecordsParams": {
                    "type": "object",
                    "properties": {
                        "metadata": {
                            "type": "object",
                            "description": "Критерии фильтрации по метаданным"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Максимальное количество результатов",
                            "default": 10
                        }
                    },
                    "required": ["metadata"],
                    "title": "FilterRecordsParams",
                    "description": "Параметры для фильтрации записей"
                },
                "DeleteRecordsParams": {
                    "type": "object",
                    "properties": {
                        "ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uuid"
                            },
                            "description": "Список UUID4 идентификаторов записей для удаления"
                        }
                    },
                    "required": ["ids"],
                    "title": "DeleteRecordsParams",
                    "description": "Параметры для удаления записей"
                },
                "GetBySessionMessageParams": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор сессии"
                        },
                        "message_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID4 идентификатор сообщения"
                        }
                    },
                    "required": ["session_id", "message_id"],
                    "title": "GetBySessionMessageParams",
                    "description": "Параметры для получения записи по идентификаторам сессии и сообщения"
                }
            },
            "examples": {
                "health_check": {
                    "summary": "Проверка доступности сервиса",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "health",
                        "id": "1"
                    }
                },
                "create_vector": {
                    "summary": "Создание векторной записи",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "create_record",
                        "params": {
                            "vector": [0.1] * 384,
                            "metadata": {"source": "test"}
                        },
                        "id": "2"
                    }
                },
                "search_by_vector": {
                    "summary": "Поиск по вектору",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "search_records",
                        "params": {
                            "vector": [0.1] * 384,
                            "limit": 5
                        },
                        "id": "3"
                    }
                },
                "search_by_text": {
                    "summary": "Поиск по тексту",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "search_text_records",
                        "params": {
                            "text": "пример поиска",
                            "limit": 5
                        },
                        "id": "4"
                    }
                },
                "filter_records": {
                    "summary": "Фильтрация записей",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "filter_records",
                        "params": {
                            "metadata": {"source": "test"},
                            "limit": 10
                        },
                        "id": "5"
                    }
                },
                "delete_records": {
                    "summary": "Удаление записей",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "delete_records",
                        "params": {
                            "ids": ["550e8400-e29b-41d4-a716-446655440000"]
                        },
                        "id": "6"
                    }
                },
                "get_by_session_message": {
                    "summary": "Получение записи по идентификаторам",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "get_by_session_message",
                        "params": {
                            "session_id": "550e8400-e29b-41d4-a716-446655440000",
                            "message_id": "660e8400-e29b-41d4-a716-446655440000"
                        },
                        "id": "7"
                    }
                }
            }
        }
    } 