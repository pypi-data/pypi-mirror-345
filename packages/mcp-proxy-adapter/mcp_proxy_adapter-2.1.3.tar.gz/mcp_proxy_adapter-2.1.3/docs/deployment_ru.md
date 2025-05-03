# Руководство по развертыванию Command Registry

В этом руководстве описаны подходы и рекомендации по развертыванию приложений, использующих Command Registry, в различных окружениях.

## Содержание

- [Подготовка к развертыванию](#подготовка-к-развертыванию)
- [Развертывание в Docker](#развертывание-в-docker)
- [Развертывание на VPS](#развертывание-на-vps)
- [Развертывание в Kubernetes](#развертывание-в-kubernetes)
- [CI/CD для Command Registry](#cicd-для-command-registry)
- [Мониторинг и логирование](#мониторинг-и-логирование)
- [Масштабирование](#масштабирование)
- [Безопасность](#безопасность)
- [Гибридная схема и интеграция с MCPProxy](#гибридная-схема-и-интеграция-с-mcpproxy)

## Подготовка к развертыванию

### 1. Создание пакета приложения

Для удобного развертывания рекомендуется оформить приложение как Python-пакет:

```
my_app/
  ├── pyproject.toml
  ├── setup.py
  ├── setup.cfg
  ├── README.md
  ├── src/
  │   └── my_app/
  │       ├── __init__.py
  │       ├── commands/
  │       │   ├── __init__.py
  │       │   └── ...
  │       ├── app.py
  │       └── main.py
  └── tests/
      └── ...
```

Пример `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-app"
version = "0.1.0"
description = "Command Registry Application"
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.8"
dependencies = [
    "command-registry>=0.1.0",
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
]
```

### 2. Настройка конфигурации

Создайте систему конфигурации, поддерживающую различные окружения:

```python
# src/my_app/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Настройки приложения."""
    APP_NAME: str = "Command Registry App"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8000
    
    # Настройки Command Registry
    STRICT_MODE: bool = True
    AUTO_FIX: bool = False
    
    # Настройки базы данных
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "app_db"
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_"

# Загрузка настроек
settings = Settings()
```

### 3. Создание точки входа

```python
# src/my_app/main.py
import uvicorn
from my_app.app import app
from my_app.config import settings

def start():
    """Запускает приложение."""
    uvicorn.run(
        "my_app.app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    start()
```

## Развертывание в Docker

### 1. Создание Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml setup.py setup.cfg ./

# Установка зависимостей
RUN pip install --no-cache-dir .

# Копирование кода приложения
COPY src/ ./src/

# Определение переменных окружения
ENV APP_DEBUG=false \
    APP_LOG_LEVEL=INFO \
    APP_API_PORT=8000 \
    APP_STRICT_MODE=true \
    APP_AUTO_FIX=false

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["python", "-m", "my_app.main"]
```

### 2. Docker Compose для локальной разработки

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_DEBUG=true
      - APP_LOG_LEVEL=DEBUG
      - APP_DB_HOST=db
    depends_on:
      - db
    volumes:
      - ./src:/app/src
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. Сборка и запуск

```bash
# Сборка образа
docker build -t my-app .

# Запуск контейнера
docker run -p 8000:8000 my-app

# Или с использованием Docker Compose
docker-compose up
```

## Развертывание на VPS

### 1. Установка зависимостей на сервере

```bash
# Обновление пакетов
sudo apt update
sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install -y python3 python3-pip python3-venv

# Установка Nginx
sudo apt install -y nginx

# Установка Supervisor
sudo apt install -y supervisor
```

### 2. Настройка Gunicorn

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка приложения и Gunicorn
pip install gunicorn
pip install .  # установка вашего приложения
```

### 3. Настройка Supervisor

```ini
# /etc/supervisor/conf.d/my-app.conf
[program:my-app]
command=/home/user/my-app/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker my_app.app:app -b 127.0.0.1:8000
directory=/home/user/my-app
user=user
autostart=true
autorestart=true
environment=APP_DEBUG=false,APP_LOG_LEVEL=INFO,APP_STRICT_MODE=true

[supervisord]
logfile=/var/log/supervisor/supervisord.log
```

### 4. Настройка Nginx

```nginx
# /etc/nginx/sites-available/my-app
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Активация конфигурации

```bash
# Активация конфигурации Nginx
sudo ln -s /etc/nginx/sites-available/my-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Запуск приложения через Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start my-app
```

## Развертывание в Kubernetes

### 1. Создание Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: APP_DEBUG
          value: "false"
        - name: APP_LOG_LEVEL
          value: "INFO"
        - name: APP_DB_HOST
          value: "postgres-service"
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "100m"
            memory: "256Mi"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
```

### 2. Создание Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### 3. Создание Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-service
            port:
              number: 80
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls-secret
```

### 4. Развертывание в Kubernetes

```bash
# Применение манифестов
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Проверка состояния
kubectl get pods
kubectl get services
kubectl get ingress
```

## CI/CD для Command Registry

### 1. GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install -e .
    - name: Run tests
      run: |
        pytest --cov=my_app

  validate-commands:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    - name: Validate commands
      run: |
        python -m my_app.tools.validate_commands --strict

  build-and-push:
    needs: [test, validate-commands]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and push Docker image
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: ghcr.io/${{ github.repository }}:latest
```

### 2. Скрипт для валидации команд

```python
# src/my_app/tools/validate_commands.py
import argparse
import sys
from my_app.app import registry

def validate_commands(strict: bool = True) -> bool:
    """
    Проверяет все команды на соответствие требованиям документации.
    
    Args:
        strict: Если True, возвращает ошибку при несоответствии
        
    Returns:
        bool: True если все команды валидны, False иначе
    """
    result = registry.validate_all_commands(strict=strict)
    
    print(f"Проверено команд: {result['total']}")
    print(f"Успешно: {result['successful']}")
    print(f"С ошибками: {result['failed']}")
    
    if result['failed'] > 0:
        print("\nКоманды с ошибками:")
        for command, errors in result['errors'].items():
            print(f"\n{command}:")
            for error in errors:
                print(f"  - {error}")
    
    return result['failed'] == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Валидация команд")
    parser.add_argument("--strict", action="store_true", help="Строгий режим проверки")
    args = parser.parse_args()
    
    success = validate_commands(strict=args.strict)
    sys.exit(0 if success else 1)
```

## Мониторинг и логирование

### 1. Настройка логирования

```python
# src/my_app/logging.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from my_app.config import settings

def setup_logging():
    """Настраивает логирование для приложения."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Обработчик для записи в файл (в production)
    if not settings.DEBUG:
        file_handler = RotatingFileHandler(
            'app.log',
            maxBytes=10485760,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Отключаем логи библиотек
    for logger_name in ['uvicorn.access']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
```

### 2. Prometheus метрики

```python
# src/my_app/monitoring.py
from prometheus_client import Counter, Histogram, Summary
import time

# Счетчики для команд
command_counter = Counter(
    'command_calls_total',
    'Total number of command calls',
    ['command', 'status']
)

# Гистограмма времени выполнения
command_duration = Histogram(
    'command_duration_seconds',
    'Command execution duration in seconds',
    ['command']
)

# Middleware для измерения времени выполнения команд
class CommandMetricsMiddleware:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.original_execute = dispatcher.execute
        dispatcher.execute = self.execute_with_metrics
    
    def execute_with_metrics(self, command_name, **params):
        start_time = time.time()
        try:
            result = self.original_execute(command_name, **params)
            command_counter.labels(command=command_name, status="success").inc()
            return result
        except Exception as e:
            command_counter.labels(command=command_name, status="error").inc()
            raise
        finally:
            duration = time.time() - start_time
            command_duration.labels(command=command_name).observe(duration)
```

### 3. Интеграция с FastAPI

```python
# src/my_app/app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import make_asgi_app

from my_app.config import settings
from my_app.logging import setup_logging
from my_app.registry import create_registry
from my_app.monitoring import CommandMetricsMiddleware

# Настройка логирования
setup_logging()

# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Добавление middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для измерения времени запросов
class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(RequestTimingMiddleware)

# Создание и настройка реестра команд
registry = create_registry(
    strict=settings.STRICT_MODE,
    auto_fix=settings.AUTO_FIX
)

# Применение метрик к диспетчеру команд
CommandMetricsMiddleware(registry.dispatcher)

# Добавление Prometheus метрик
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Эндпоинт для проверки состояния
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Регистрация адаптера REST API
from command_registry.adapters import RESTAdapter
rest_adapter = RESTAdapter(registry)
rest_adapter.register_endpoints(app)
```

## Масштабирование

### 1. Горизонтальное масштабирование

Приложения с Command Registry могут легко масштабироваться горизонтально, так как не имеют состояния. Для масштабирования:

- Используйте балансировщик нагрузки (Nginx, HAProxy)
- В Kubernetes увеличьте количество реплик
- Используйте автомасштабирование на основе метрик

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Асинхронное выполнение команд

Для долго выполняющихся команд используйте асинхронное выполнение:

```python
# src/my_app/commands/async_commands.py
import asyncio
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

async def process_large_dataset(data_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Асинхронно обрабатывает большой набор данных.
    
    Args:
        data_id: Идентификатор набора данных
        options: Опции обработки
        
    Returns:
        Dict[str, Any]: Результат обработки
    """
    logger.info(f"Starting processing of dataset {data_id}")
    
    # Имитация долгой обработки
    await asyncio.sleep(5)
    
    logger.info(f"Completed processing of dataset {data_id}")
    return {
        "data_id": data_id,
        "status": "completed",
        "results": [
            {"item_id": 1, "value": 100},
            {"item_id": 2, "value": 200}
        ]
    }
```

### 3. Очереди задач с Celery

```python
# src/my_app/tasks.py
from celery import Celery
from my_app.config import settings

# Создание Celery приложения
celery_app = Celery(
    'my_app',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
)

# Настройка Celery
celery_app.conf.update(
    worker_concurrency=4,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name="process_data")
def process_data_task(data_id, options=None):
    """Фоновая задача для обработки данных."""
    from my_app.commands.data_commands import process_data
    return process_data(data_id, options)
```

### 4. Интеграция с Command Registry

```python
# src/my_app/commands/background_commands.py
from typing import Dict, Any
from my_app.tasks import process_data_task

def start_data_processing(data_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Запускает обработку данных в фоновом режиме.
    
    Args:
        data_id: Идентификатор набора данных
        options: Опции обработки
        
    Returns:
        Dict[str, Any]: Информация о запущенной задаче
    """
    # Запуск задачи в Celery
    task = process_data_task.delay(data_id, options)
    
    return {
        "task_id": task.id,
        "status": "started",
        "data_id": data_id
    }

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Получает статус фоновой задачи.
    
    Args:
        task_id: Идентификатор задачи
        
    Returns:
        Dict[str, Any]: Статус и результат задачи, если она завершена
    """
    from my_app.tasks import celery_app
    task = celery_app.AsyncResult(task_id)
    
    result = {
        "task_id": task_id,
        "status": task.status,
    }
    
    if task.status == 'SUCCESS':
        result["result"] = task.result
    elif task.status == 'FAILURE':
        result["error"] = str(task.result)
    
    return result
```

## Безопасность

### 1. Аутентификация и авторизация

```python
# src/my_app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from my_app.config import settings

# Схема OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """Создает JWT токен."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Получает текущего пользователя по токену."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Здесь должен быть код для получения пользователя из базы данных
    user = {"username": username, "role": payload.get("role", "user")}
    return user

def check_permission(user: Dict[str, Any], required_role: str) -> bool:
    """Проверяет, имеет ли пользователь требуемую роль."""
    return user.get("role") == required_role
```

### 2. Защита эндпоинтов

```python
# src/my_app/app.py
from fastapi import Depends, HTTPException, status
from my_app.auth import get_current_user, check_permission

# Защита эндпоинта требованием аутентификации
@app.post("/protected/command/{command_name}")
async def execute_protected_command(
    command_name: str,
    params: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Защищенный эндпоинт для выполнения команд."""
    # Проверка разрешений
    if not check_permission(current_user, "admin") and command_name.startswith("admin_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Выполнение команды
    try:
        result = registry.dispatcher.execute(command_name, **params)
        return {"result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### 3. Защита от распространенных уязвимостей

```python
# src/my_app/app.py
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Редирект на HTTPS
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)

# Ограничение хостов
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.example.com", "localhost"]
)

# Сжатие ответов
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Настройка заголовков безопасности
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Заключение

При развертывании приложений с Command Registry важно учитывать:

1. **Конфигурацию** - используйте переменные окружения и файлы .env
2. **Логирование** - настройте логирование для отладки и мониторинга
3. **Масштабирование** - разработайте приложение для горизонтального масштабирования
4. **Безопасность** - защитите API с помощью аутентификации и авторизации
5. **CI/CD** - автоматизируйте тестирование и развертывание
6. **Мониторинг** - отслеживайте метрики производительности и использования

Эти рекомендации помогут вам успешно развернуть и поддерживать приложения на основе Command Registry в различных окружениях. 

## Гибридная схема и интеграция с MCPProxy

### Проблема масштабирования OpenAPI схем

При большом количестве команд документация OpenAPI становится громоздкой и трудной для обработки. Это создает следующие проблемы:

1. Модели ИИ могут не справляться с обработкой больших схем
2. Клиентские библиотеки генерируются с ошибками
3. Документация становится менее удобной для разработчиков
4. Увеличивается время загрузки Swagger UI

### Решение: гибридная архитектура REST+JSONRPC

Command Registry предлагает гибридный подход, сочетающий преимущества REST и JSONRPC:

```
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│                   │    │                   │    │                   │
│  Command Registry │───►│  Гибридная схема  │───►│ REST + JSONRPC API│
│                   │    │                   │    │                   │
└───────────────────┘    └───────────────────┘    └───────────────────┘
                                                          │
                                                          ▼
                                                ┌───────────────────┐
                                                │                   │
                                                │     MCPProxy      │
                                                │                   │
                                                └───────────────────┘
                                                          │
                                                          ▼
                                                ┌───────────────────┐
                                                │                   │
                                                │ Инструменты модели│
                                                │                   │
                                                └───────────────────┘
```

#### Компоненты решения:

1. **Традиционные REST эндпоинты** для стандартных операций
2. **Универсальный эндпоинт `cmd`** принимающий JSONRPC запросы
3. **Генератор гибридной схемы** создающий оптимизированную документацию API

### Генератор гибридной схемы

Для генерации гибридной схемы был создан отдельный генератор, который:

1. Анализирует команды из Command Registry
2. Создает оптимизированную OpenAPI схему
3. Формирует универсальный эндпоинт для JSONRPC
4. Поддерживает обратную совместимость с существующими клиентами

```python
# Пример использования генератора гибридной схемы
from command_registry.generators.hybrid_generator import HybridAPIGenerator
from my_app.registry import registry

# Создаем генератор
generator = HybridAPIGenerator(
    title="My Hybrid API",
    description="API с поддержкой REST и JSONRPC",
    version="1.0.0",
    cmd_endpoint="/api/cmd"
)

# Регистрируем в Command Registry
registry.add_generator(generator)

# Применяем к FastAPI приложению
app = FastAPI()
generator.apply_to_fastapi(app)
```

### Интеграция с MCPProxy

MCPProxy позволяет преобразовать OpenAPI серверы в инструменты для моделей ИИ. Для успешной интеграции Command Registry с MCPProxy:

1. **Установите MCPProxy**:

```bash
pip install mcp-proxy
```

2. **Включите поддержку MCPProxy в вашем приложении**:

```python
from command_registry.adapters import MCPProxyAdapter
from my_app.registry import registry

# Создаем адаптер для MCPProxy
mcp_adapter = MCPProxyAdapter(registry)

# Регистрируем в приложении
app = FastAPI()
mcp_adapter.register_endpoints(app)
```

3. **Настройте маршрутизацию в MCPProxy**:

```yaml
# mcp_proxy_config.yaml
routes:
  - path: /api/cmd
    type: json_rpc
    schema_url: http://your-api.com/openapi.json
    command_field: method
    params_field: params
```

### Рекомендации для больших проектов

При использовании Command Registry в крупных проектах с MCPProxy:

1. **Группируйте команды по функциональности**:
   ```python
   # Пример структуры команд
   my_app/
     commands/
       user_commands.py
       data_commands.py
       admin_commands.py
   ```

2. **Используйте подпроекты** для отдельных доменных областей:
   ```
   my_solution/
     ├── user_service/
     │   └── commands/
     ├── data_service/
     │   └── commands/
     └── admin_service/
         └── commands/
   ```

3. **Создайте отдельные гибридные схемы** для каждого подпроекта:
   ```python
   # Для каждого подпроекта
   user_registry = CommandRegistry(...)
   user_generator = HybridAPIGenerator(...)
   user_registry.add_generator(user_generator)
   ```

4. **Объедините схемы при необходимости** с помощью агрегатора:
   ```python
   from command_registry.tools import SchemaAggregator
   
   aggregator = SchemaAggregator()
   aggregator.add_schema("users", "http://user-service/openapi.json")
   aggregator.add_schema("data", "http://data-service/openapi.json")
   aggregator.add_schema("admin", "http://admin-service/openapi.json")
   
   # Создание единой схемы
   combined_schema = aggregator.generate_combined_schema()
   ```

### Обновление индекса кода

Для поддержания актуальности документации, обновляйте `code_index.yaml` при изменении структуры проекта:

```yaml
# Пример обновления code_index.yaml
sections:
  - name: "Генераторы"
    description: "Генераторы API схем"
    files:
      - path: "command_registry/generators/hybrid_generator.py"
        description: "Генератор гибридной схемы REST+JSONRPC для MCPProxy"
      
  - name: "Адаптеры"
    description: "Адаптеры для различных протоколов"
    files:
      - path: "command_registry/adapters/mcp_proxy_adapter.py"
        description: "Адаптер для интеграции с MCPProxy"
```

Этот подход к организации кода и документации позволит эффективно масштабировать проекты на базе Command Registry и успешно интегрировать их с MCPProxy для создания инструментов моделей ИИ. 

# Руководство по публикации в PyPI

В этом руководстве описывается процесс подготовки и публикации пакета MCP Proxy Adapter в Python Package Index (PyPI).

## Подготовка пакета

### 1. Обновите метаданные пакета

Перед публикацией убедитесь, что файлы `pyproject.toml` и `setup.py` содержат актуальную информацию:

- Версия пакета
- Описание
- URL проекта
- Адрес электронной почты автора
- Классификаторы
- Зависимости

### 2. Установите необходимые инструменты

```bash
pip install build twine
```

### 3. Соберите пакет

```bash
python -m build
```

Эта команда создаст как Source Distribution (sdist), так и Wheel Distribution (bdist_wheel) в директории `dist/`.

### 4. Проверьте пакет

```bash
twine check dist/*
```

Убедитесь, что все проверки пройдены без ошибок.

## Публикация пакета

### 1. Настройка аутентификации

Создайте файл `.pypirc` в вашем домашнем каталоге со следующим содержимым:

```
[pypi]
username = __token__
password = <ваш_токен_pypi>
```

Замените `<ваш_токен_pypi>` на ваш токен доступа к PyPI, который вы можете получить в своем аккаунте PyPI.

Альтернативно, вы можете передать учетные данные непосредственно в команду `twine upload`.

### 2. Публикация в тестовом PyPI (опционально)

Сначала рекомендуется опубликовать пакет в тестовом репозитории:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

После этого вы можете установить пакет из тестового PyPI и проверить его работу:

```bash
pip install --index-url https://test.pypi.org/simple/ mcp-proxy-adapter
```

### 3. Публикация в основном PyPI

После успешного тестирования опубликуйте пакет в основном PyPI:

```bash
twine upload dist/*
```

### 4. Проверка установки

Проверьте, что пакет успешно загружен и может быть установлен:

```bash
pip install mcp-proxy-adapter
```

## Обновление пакета

Для публикации новой версии пакета:

1. Обновите версию в `pyproject.toml` и `setup.py`
2. Обновите файл `CHANGELOG.md` (если есть)
3. Соберите пакет заново
4. Загрузите новую версию в PyPI

```bash
# Обновите версию в файлах
# ...

# Соберите пакет
python -m build

# Загрузите пакет
twine upload dist/*
```

## Использование GitHub Actions для автоматической публикации

Вы можете автоматизировать процесс публикации пакета при создании нового релиза в GitHub.

Создайте файл `.github/workflows/publish.yml` со следующим содержимым:

```yaml
name: Build and publish Python package

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and publish
      env:
        TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        python -m build
        twine upload dist/*
```

Не забудьте добавить соответствующие секреты `PYPI_USERNAME` и `PYPI_PASSWORD` в настройках вашего GitHub репозитория.

## Проверка совместимости

Перед публикацией рекомендуется проверить совместимость пакета с различными версиями Python.
Для этого можно использовать инструмент `tox`:

```bash
pip install tox

# Создайте файл tox.ini в корне проекта
# [tox]
# envlist = py39, py310, py311, py312
# 
# [testenv]
# deps = pytest
# commands = pytest

# Запустите тесты для разных версий Python
tox
```

## Документация по установке пакета для пользователей

После публикации пакета в PyPI, пользователи смогут установить его с помощью `pip`:

```bash
pip install mcp-proxy-adapter
```

Для установки конкретной версии:

```bash
pip install mcp-proxy-adapter==1.0.0
```

Для обновления до последней версии:

```bash
pip install --upgrade mcp-proxy-adapter
``` 