#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Стартовий скрипт для JARVIS v2.0
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Перевірка версії Python"""
    if sys.version_info < (3, 8):
        print("ПОМИЛКА: Потрібен Python 3.8 або новіший")
        print(f"Поточна версія: {sys.version}")
        return False
    
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def check_dependencies():
    """Перевірка встановлених залежностей"""
    required_packages = [
        'speechrecognition',
        'pyttsx3',
        'aiohttp',
        'requests',
        'beautifulsoup4',
        'PIL',
        'psutil',
        'numpy',
        'openai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            else:
                importlib.import_module(package)
            print(f"{package} - OK")
        except ImportError:
            print(f"{package} - ВІДСУТНІЙ")
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Встановлення відсутніх пакетів"""
    if not packages:
        return True
    
    print(f"\nВстановлюю відсутні пакети: {', '.join(packages)}")
    
    # Мапінг назв пакетів для pip
    pip_names = {
        'PIL': 'Pillow'
    }
    
    for package in packages:
        pip_name = pip_names.get(package, package)
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name])
            print(f"Встановлено {pip_name}")
        except subprocess.CalledProcessError:
            print(f"ПОМИЛКА встановлення {pip_name}")
            return False
    
    return True

def create_directories():
    """Створення необхідних директорій"""
    directories = [
        'memory',
        'memory/knowledge_base',
        'logs',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("Директорії створено")

def show_startup_menu():
    """Показ меню запуску"""
    print("\n" + "="*50)
    print("JARVIS v2.0 - AI Desktop Assistant")
    print("="*50)
    print("Оберіть режим запуску:")
    print("1. Голосовий режим (консоль)")
    print("2. Графічний інтерфейс (GUI)")
    print("3. Тестування системи")
    print("4. Вихід")
    print("="*50)
    
    while True:
        try:
            choice = input("Ваш вибір (1-4): ").strip()
            
            if choice == '1':
                return 'console'
            elif choice == '2':
                return 'gui'
            elif choice == '3':
                return 'test'
            elif choice == '4':
                return 'exit'
            else:
                print("Невірний вибір. Спробуйте ще раз.")
                
        except KeyboardInterrupt:
            return 'exit'

def run_tests():
    """Запуск тестів системи"""
    print("\nТестування системи JARVIS:")
    print("-" * 40)
    
    # Перевірка файлів
    required_files = [
        'main.py',
        'config.py',
        'voice/listener.py',
        'voice/speaker.py',
        'memory/learner.py'
    ]
    
    print("Перевірка файлів:")
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"{file_path} - OK")
        else:
            print(f"{file_path} - ВІДСУТНІЙ")
    
    # Перевірка конфігурації
    try:
        from config import Config
        config = Config()
        print(f"Конфігурація - OK")
        print(f"Версія: {config.VERSION}")
        print(f"Автор: {config.AUTHOR}")
    except Exception as e:
        print(f"Конфігурація - ПОМИЛКА: {e}")

def main():
    """Головна функція запуску"""
    print("Запуск JARVIS v2.0...")
    
    # Перевірка Python
    if not check_python_version():
        sys.exit(1)
    
    # Перевірка залежностей
    missing = check_dependencies()
    if missing:
        print(f"\nВідсутні залежності: {', '.join(missing)}")
        install = input("Встановити автоматично? (y/n): ").lower().strip()
        
        if install == 'y':
            if not install_missing_packages(missing):
                print("ПОМИЛКА встановлення залежностей")
                sys.exit(1)
        else:
            print("Неможливо продовжити без залежностей")
            sys.exit(1)
    
    # Створення директорій
    create_directories()
    
    # Меню запуску
    while True:
        mode = show_startup_menu()
        
        if mode == 'console':
            print("\nЗапускаю JARVIS в голосовому режимі...")
            os.system(f"{sys.executable} main.py")
            break
            
        elif mode == 'gui':
            print("\nЗапускаю JARVIS з графічним інтерфейсом...")
            os.system(f"{sys.executable} main.py --gui")
            break
            
        elif mode == 'test':
            run_tests()
            input("\nНатисніть Enter для продовження...")
            
        elif mode == 'exit':
            print("До побачення!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nДо побачення!")
    except Exception as e:
        print(f"Критична помилка: {e}")
        sys.exit(1)
