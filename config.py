#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфігурація JARVIS v2.0
"""

import os
from pathlib import Path

class Config:
    # Основні налаштування
    APP_NAME = "JARVIS MVP"
    VERSION = "2.0.0"
    AUTHOR = "Oleksandr Azenko"
    
    # Шляхи
    BASE_DIR = Path(__file__).parent
    MEMORY_DIR = BASE_DIR / "memory"
    KNOWLEDGE_BASE_DIR = MEMORY_DIR / "knowledge_base"
    LOGS_DIR = BASE_DIR / "logs"
    
    # База даних
    DATABASE_PATH = MEMORY_DIR / "memory.db"
    
    # Голосові налаштування
    VOICE_LANGUAGE = "uk-UA"
    VOICE_RATE = 150
    VOICE_VOLUME = 0.8
    
    # Розпізнавання мовлення
    SPEECH_LANGUAGE = "uk-UA"
    SPEECH_TIMEOUT = 5
    SPEECH_PHRASE_TIMEOUT = 3
    
    # Налаштування мікрофона
    MICROPHONE_INDEX = None  # None = використовувати за замовчуванням
    MICROPHONE_ENERGY_THRESHOLD = 300
    MICROPHONE_DYNAMIC_THRESHOLD = True
    MICROPHONE_PAUSE_THRESHOLD = 0.8
    
    # API ключі
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    
    # Налаштування погоди
    DEFAULT_CITY = "Київ"
    WEATHER_UNITS = "metric"
    
    # Налаштування безпеки
    DANGEROUS_COMMANDS = [
        "format", "delete system", "rm -rf", 
        "shutdown -f", "restart -f"
    ]
    
    # Активаційні фрази
    ACTIVATION_PHRASES = [
        "привіт джарвіс", "привет джарвис",
        "hey jarvis", "hi jarvis",
        "джарвіс", "jarvis"
    ]
    
    # Відповіді
    GREETING_RESPONSES = [
        "Слухаю тебе, Олександре.",
        "Так, я тут. Що потрібно зробити?",
        "Готова допомогти. Яка команда?",
        "Вітаю! Чим можу бути корисною?"
    ]
    
    ERROR_RESPONSES = [
        "Вибачте, не зрозуміла команду.",
        "Можете повторити?",
        "Щось пішло не так. Спробуйте ще раз.",
        "Не можу виконати цю команду."
    ]

    # Налаштування навчання
    LEARNING_MODE = True
    AUTO_UPDATE_ENABLED = True
    PDF_LEARNING_ENABLED = True

    # Налаштування GPT
    GPT_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000

    # Персоналізація
    USER_NAME = "Олександре"
    ASSISTANT_PERSONALITY = "helpful_professional"

    # Режими роботи
    VOICE_ONLY_MODE = False
    SCREEN_ANALYSIS_MODE = True
    LEARNING_NOTIFICATIONS = True

    # Векторна база знань
    VECTOR_DB_ENABLED = True
    VECTOR_SEARCH_TOP_K = 5
    VECTOR_CONTEXT_MAX_LENGTH = 1000

    # Telegram бот
    TELEGRAM_BOT_ENABLED = True
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_AUTHORIZED_USERS = os.getenv("TELEGRAM_AUTHORIZED_USERS", "").split(",")

    # Статистика та логування
    DETAILED_LOGGING = True
    STATISTICS_ENABLED = True
    INTERACTION_HISTORY_LIMIT = 100
    
    @classmethod
    def ensure_directories(cls):
        """Створення необхідних директорій"""
        cls.MEMORY_DIR.mkdir(exist_ok=True)
        cls.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def is_dangerous_command(cls, command):
        """Перевірка на небезпечну команду"""
        command_lower = command.lower()
        return any(dangerous in command_lower for dangerous in cls.DANGEROUS_COMMANDS)

    @classmethod
    def get_api_status(cls):
        """Перевірка статусу API ключів"""
        return {
            "openai": bool(cls.OPENAI_API_KEY),
            "weather": bool(cls.WEATHER_API_KEY),
            "telegram": bool(cls.TELEGRAM_BOT_TOKEN)
        }

# Ініціалізація при імпорті
Config.ensure_directories()
