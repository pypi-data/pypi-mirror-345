"""
REST OpenAPI схема для API сервера.
Содержит все определения REST эндпоинтов, параметров и ответов.
"""
from typing import Dict, Any

__all__ = ["get_rest_schema"]


def get_rest_schema() -> Dict[str, Any]:
    """
    Создает и возвращает OpenAPI схему для REST API.
    
    Returns:
        Dict[str, Any]: Схема OpenAPI для REST API
    """
    return {
        "openapi": "3.0.2",
        "info": {
            "title": "Vector Store API",
            "description": "API для работы с векторным хранилищем",
            "version": "1.0.0"
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "Проверка состояния сервера",
                    "operationId": "check_health",
                    "description": "Проверяет доступность и состояние сервера",
                    "parameters": [
                        {
                            "name": "check_type",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["basic", "detailed"],
                                "default": "basic"
                            },
                            "description": "Тип проверки: базовая или расширенная"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/network/check": {
                "post": {
                    "summary": "Проверка сетевого соединения",
                    "operationId": "network_check",
                    "description": "Проверяет доступность указанного хоста и порта",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/NetworkCheckRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/NetworkCheckResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/config/reload": {
                "post": {
                    "summary": "Перезагрузка конфигурации",
                    "operationId": "reload_config",
                    "description": "Перезагружает конфигурацию сервера",
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ReloadConfigRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/BaseResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/index": {
                "post": {
                    "summary": "Добавление векторов",
                    "operationId": "add_vectors",
                    "description": "Добавляет векторы в хранилище",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/IndexRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/IndexResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/search": {
                "post": {
                    "summary": "Поиск по векторам",
                    "operationId": "search",
                    "description": "Выполняет поиск по векторам в хранилище",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SearchRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/SearchResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/help": {
                "get": {
                    "summary": "Получение справочной информации",
                    "operationId": "get_help",
                    "description": "Возвращает справочную информацию обо всех доступных командах или конкретной команде",
                    "parameters": [
                        {
                            "name": "command",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Название команды для получения справки. Если не указано, возвращается список всех доступных команд."
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HelpResponse"
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
                "BaseResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Статус выполнения операции"
                        },
                        "message": {
                            "type": "string",
                            "description": "Сообщение о результате операции"
                        }
                    },
                    "required": ["status"]
                },
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Статус сервера"
                        },
                        "version": {
                            "type": "string",
                            "description": "Версия сервера"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Время ответа"
                        },
                        "details": {
                            "type": "object",
                            "additionalProperties": True,
                            "description": "Дополнительная информация при детальной проверке"
                        }
                    },
                    "required": ["status", "timestamp"]
                },
                "NetworkCheckRequest": {
                    "type": "object",
                    "properties": {
                        "host": {
                            "type": "string",
                            "description": "Хост для проверки"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Порт для проверки"
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Таймаут в секундах",
                            "default": 5
                        }
                    },
                    "required": ["host", "port"]
                },
                "NetworkCheckResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Статус проверки"
                        },
                        "host": {
                            "type": "string",
                            "description": "Проверенный хост"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Проверенный порт"
                        },
                        "accessible": {
                            "type": "boolean",
                            "description": "Доступность хоста и порта"
                        },
                        "latency": {
                            "type": "number",
                            "description": "Время отклика в миллисекундах"
                        }
                    },
                    "required": ["status", "host", "port", "accessible"]
                },
                "ReloadConfigRequest": {
                    "type": "object",
                    "properties": {
                        "config_path": {
                            "type": "string",
                            "description": "Путь к файлу конфигурации (опционально)"
                        }
                    }
                },
                "Vector": {
                    "type": "array",
                    "items": {
                        "type": "number",
                        "format": "float"
                    },
                    "description": "Вектор в представлении массива чисел с плавающей точкой",
                    "minItems": 384,
                    "maxItems": 384
                },
                "Metadata": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Метаданные, связанные с вектором"
                },
                "IndexRequest": {
                    "type": "object",
                    "properties": {
                        "vectors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "vector": {
                                        "$ref": "#/components/schemas/Vector"
                                    },
                                    "metadata": {
                                        "$ref": "#/components/schemas/Metadata"
                                    }
                                },
                                "required": ["vector"]
                            },
                            "description": "Массив векторов для добавления"
                        }
                    },
                    "required": ["vectors"]
                },
                "IndexResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Статус операции"
                        },
                        "ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uuid"
                            },
                            "description": "Идентификаторы добавленных векторов"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Количество добавленных векторов"
                        }
                    },
                    "required": ["status", "ids", "count"]
                },
                "SearchRequest": {
                    "type": "object",
                    "properties": {
                        "vector": {
                            "$ref": "#/components/schemas/Vector"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Количество результатов для возврата",
                            "default": 10,
                            "minimum": 1
                        },
                        "filter": {
                            "type": "object",
                            "additionalProperties": True,
                            "description": "Фильтр для метаданных"
                        }
                    },
                    "required": ["vector"]
                },
                "SearchResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Статус операции"
                        },
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "format": "uuid",
                                        "description": "Идентификатор найденного вектора"
                                    },
                                    "score": {
                                        "type": "number",
                                        "format": "float",
                                        "description": "Оценка сходства"
                                    },
                                    "metadata": {
                                        "$ref": "#/components/schemas/Metadata"
                                    }
                                },
                                "required": ["id", "score"]
                            },
                            "description": "Результаты поиска"
                        },
                        "total": {
                            "type": "integer",
                            "description": "Общее количество результатов"
                        }
                    },
                    "required": ["status", "results", "total"]
                },
                "HelpParams": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Название команды для получения справки. Если не указано, возвращается список всех доступных команд."
                        }
                    },
                    "title": "HelpParams",
                    "description": "Параметры для команды help (получение справки по командам)"
                },
                "HelpResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Статус операции"
                        },
                        "commands": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Название команды"
                                    },
                                    "summary": {
                                        "type": "string",
                                        "description": "Краткое описание команды"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Полное описание команды"
                                    },
                                    "parameters": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "type": "string",
                                                    "description": "Название параметра"
                                                },
                                                "type": {
                                                    "type": "string",
                                                    "description": "Тип параметра"
                                                },
                                                "description": {
                                                    "type": "string",
                                                    "description": "Описание параметра"
                                                },
                                                "required": {
                                                    "type": "boolean",
                                                    "description": "Является ли параметр обязательным"
                                                },
                                                "default": {
                                                    "description": "Значение по умолчанию (если есть)"
                                                }
                                            },
                                            "required": ["name", "type", "description"]
                                        },
                                        "description": "Параметры команды"
                                    },
                                    "examples": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "description": {
                                                    "type": "string",
                                                    "description": "Описание примера"
                                                },
                                                "request": {
                                                    "type": "object",
                                                    "description": "Пример запроса"
                                                },
                                                "response": {
                                                    "type": "object",
                                                    "description": "Пример ответа"
                                                }
                                            },
                                            "required": ["description", "request"]
                                        },
                                        "description": "Примеры использования команды"
                                    }
                                },
                                "required": ["name", "summary", "description"]
                            },
                            "description": "Список доступных команд или детальная информация о конкретной команде"
                        }
                    },
                    "required": ["status", "commands"]
                }
            }
        }
    } 