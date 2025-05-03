#!/usr/bin/env python3
"""
Скрипт для публикации пакета в PyPI.
"""
import sys
import os
import subprocess
import shutil
import argparse

# Путь к корню проекта
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def clean_build_dirs():
    """Очищает директории сборки."""
    print("Очистка директорий сборки...")
    
    dirs_to_clean = [
        os.path.join(PROJECT_ROOT, 'build'),
        os.path.join(PROJECT_ROOT, 'dist'),
        os.path.join(PROJECT_ROOT, 'mcp_proxy_adapter.egg-info'),
        os.path.join(PROJECT_ROOT, 'src/mcp_proxy_adapter.egg-info')
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            print(f"Удаление {dir_path}")
            shutil.rmtree(dir_path)


def build_package():
    """Собирает пакет."""
    print("Сборка пакета...")
    
    # Сборка колеса
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--sdist"], cwd=PROJECT_ROOT, check=True)


def upload_to_pypi(test=True):
    """Загружает пакет в PyPI."""
    if test:
        print("Загрузка в TestPyPI...")
        cmd = [
            sys.executable, "-m", "twine", "upload", 
            "--repository-url", "https://test.pypi.org/legacy/", 
            "dist/*"
        ]
    else:
        print("Загрузка в PyPI...")
        cmd = [sys.executable, "-m", "twine", "upload", "dist/*"]
    
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description="Публикация пакета в PyPI")
    parser.add_argument('--test', action='store_true', help='Загрузить в TestPyPI вместо основного PyPI')
    parser.add_argument('--no-clean', action='store_true', help='Не очищать директории сборки')
    parser.add_argument('--build-only', action='store_true', help='Только сборка без загрузки')
    
    args = parser.parse_args()
    
    try:
        if not args.no_clean:
            clean_build_dirs()
        
        build_package()
        
        if not args.build_only:
            upload_to_pypi(test=args.test)
        
        print("Готово!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e}")
        return 1
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 