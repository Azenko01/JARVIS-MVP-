#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система безпеки та валідації команд для JARVIS
"""

import logging
import re
from enum import Enum
from typing import List, Dict, Tuple
from config import Config

class SecurityLevel(Enum):
    """Рівні безпеки команд"""
    SAFE = 1
    CAUTION = 2
    DANGEROUS = 3
    BLOCKED = 4

class CommandCategory(Enum):
    """Категорії команд"""
    SYSTEM = "system"
    FILE = "file"
    NETWORK = "network"
    APPLICATION = "application"
    VOICE = "voice"
    LEARNING = "learning"
    GENERAL = "general"

class CommandValidator:
    def __init__(self):
        self.config = Config()
        
        # Словник небезпечних команд
        self.dangerous_patterns = {
            SecurityLevel.BLOCKED: [
                r'format\s+[cd]:', r'del\s+/[sq]', r'rm\s+-rf\s+/',
                r'shutdown\s+/[fs]', r'taskkill\s+/f', r'net\s+user.*delete'
            ],
            SecurityLevel.DANGEROUS: [
                r'shutdown', r'restart', r'reboot', r'вимкни\s+комп',
                r'перезавантаж', r'format', r'delete\s+system',
                r'kill\s+process', r'terminate\s+all'
            ],
            SecurityLevel.CAUTION: [
                r'закрий\s+всі', r'close\s+all', r'kill\s+\w+',
                r'delete\s+\w+', r'remove\s+\w+', r'uninstall'
            ]
        }
        
        # Дозволені системні команди з підтвердженням
        self.allowed_with_confirmation = [
            'shutdown', 'restart', 'sleep', 'lock',
            'вимкни комп', 'перезавантаж', 'сплячий режим'
        ]
        
        # Категорії команд
        self.command_categories = {
            CommandCategory.SYSTEM: [
                'shutdown', 'restart', 'sleep', 'lock', 'вимкни', 'перезавантаж'
            ],
            CommandCategory.APPLICATION: [
                'відкрий', 'запусти', 'закрий', 'open', 'launch', 'close'
            ],
            CommandCategory.FILE: [
                'створи файл', 'видали файл', 'копіюй', 'переміщай'
            ],
            CommandCategory.NETWORK: [
                'пошукай', 'завантаж', 'надішли', 'search', 'download'
            ],
            CommandCategory.VOICE: [
                'говори', 'мовчи', 'гучніше', 'тихіше'
            ],
            CommandCategory.LEARNING: [
                'навчися', 'запам\'ятай', 'забудь', 'оновись'
            ]
        }
        
        logging.info("CommandValidator ініціалізовано")
    
    def validate_command(self, command: str) -> Tuple[SecurityLevel, CommandCategory, str]:
        """
        Валідація команди на безпеку
        
        Args:
            command (str): Команда для перевірки
            
        Returns:
            Tuple[SecurityLevel, CommandCategory, str]: Рівень безпеки, категорія, повідомлення
        """
        command_lower = command.lower().strip()
        
        # Перевірка на заблоковані команди
        for pattern in self.dangerous_patterns[SecurityLevel.BLOCKED]:
            if re.search(pattern, command_lower):
                return SecurityLevel.BLOCKED, CommandCategory.SYSTEM, "Команда заблокована з міркувань безпеки"
        
        # Перевірка на небезпечні команди
        for pattern in self.dangerous_patterns[SecurityLevel.DANGEROUS]:
            if re.search(pattern, command_lower):
                return SecurityLevel.DANGEROUS, self._get_command_category(command_lower), "Небезпечна команда - потрібне підтвердження"
        
        # Перевірка на команди з обережністю
        for pattern in self.dangerous_patterns[SecurityLevel.CAUTION]:
            if re.search(pattern, command_lower):
                return SecurityLevel.CAUTION, self._get_command_category(command_lower), "Команда потребує обережності"
        
        # Безпечна команда
        category = self._get_command_category(command_lower)
        return SecurityLevel.SAFE, category, "Команда безпечна"
    
    def _get_command_category(self, command: str) -> CommandCategory:
        """Визначення категорії команди"""
        for category, keywords in self.command_categories.items():
            if any(keyword in command for keyword in keywords):
                return category
        return CommandCategory.GENERAL
    
    def is_confirmation_required(self, command: str) -> bool:
        """Перевірка чи потрібне підтвердження"""
        security_level, _, _ = self.validate_command(command)
        return security_level in [SecurityLevel.DANGEROUS, SecurityLevel.CAUTION]
    
    def get_confirmation_message(self, command: str) -> str:
        """Отримання повідомлення для підтвердження"""
        security_level, category, _ = self.validate_command(command)
        
        if security_level == SecurityLevel.DANGEROUS:
            return f"⚠️ Небезпечна команда: '{command}'. Скажіть 'підтверджую' для виконання або 'скасувати' для відміни."
        elif security_level == SecurityLevel.CAUTION:
            return f"⚠️ Команда потребує обережності: '{command}'. Продовжити? (так/ні)"
        
        return ""
    
    def log_security_event(self, command: str, security_level: SecurityLevel, action_taken: str):
        """Логування подій безпеки"""
        logging.warning(f"Security Event - Command: '{command}', Level: {security_level.name}, Action: {action_taken}")

# Глобальний екземпляр
command_validator = CommandValidator()

def validate_command_security(command: str):
    """Функція для використання в main.py"""
    return command_validator.validate_command(command)

def requires_confirmation(command: str):
    """Перевірка потреби підтвердження"""
    return command_validator.is_confirmation_required(command)

def get_confirmation_prompt(command: str):
    """Отримання тексту підтвердження"""
    return command_validator.get_confirmation_message(command)
