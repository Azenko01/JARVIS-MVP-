#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плагін асистента програміста для JARVIS
"""

import asyncio
import logging
import subprocess
import os
import pyautogui
import time

class CodeAssistant:
    def __init__(self):
        self.supported_ides = {
            'vscode': 'Visual Studio Code',
            'pycharm': 'PyCharm',
            'sublime': 'Sublime Text',
            'atom': 'Atom'
        }
        
        self.code_suggestions = {
            'python': {
                'function': 'def function_name():\n    """Docstring"""\n    pass',
                'class': 'class ClassName:\n    def __init__(self):\n        pass',
                'import': 'import module_name\nfrom module import function',
                'try_except': 'try:\n    # code\nexcept Exception as e:\n    print(f"Error: {e}")'
            },
            'javascript': {
                'function': 'function functionName() {\n    // code\n}',
                'arrow_function': 'const functionName = () => {\n    // code\n};',
                'class': 'class ClassName {\n    constructor() {\n        // code\n    }\n}',
                'async': 'async function functionName() {\n    // code\n}'
            }
        }
    
    async def analyze_current_code(self):
        """Аналіз поточного коду на екрані"""
        try:
            # Отримання активного вікна
            active_window = await self._get_active_ide()
            
            if not active_window:
                return "Не виявлено активного редактора коду."
            
            # Копіювання поточного коду
            pyautogui.hotkey('ctrl', 'a')  # Виділити все
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'c')  # Копіювати
            time.sleep(0.1)
            
            # Отримання коду з буфера обміну
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            
            try:
                code = root.clipboard_get()
                root.destroy()
                
                # Аналіз коду
                suggestions = await self._analyze_code_quality(code)
                return f"Аналіз коду в {active_window}:\n{suggestions}"
                
            except tk.TclError:
                root.destroy()
                return "Не вдалося отримати код з буфера обміну."
                
        except Exception as e:
            logging.error(f"Помилка аналізу коду: {e}")
            return "Помилка при аналізі коду."
    
    async def _get_active_ide(self):
        """Визначення активного IDE"""
        try:
            import win32gui
            
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd).lower()
            
            for ide_key, ide_name in self.supported_ides.items():
                if ide_key in window_title:
                    return ide_name
            
            # Перевірка на загальні ознаки редактора коду
            code_indicators = ['.py', '.js', '.html', '.css', '.json', 'code', 'editor']
            if any(indicator in window_title for indicator in code_indicators):
                return "Code Editor"
            
            return None
            
        except ImportError:
            return "Code Editor"  # Fallback
        except Exception as e:
            logging.error(f"Помилка визначення IDE: {e}")
            return None
    
    async def _analyze_code_quality(self, code):
        """Аналіз якості коду"""
        suggestions = []
        
        # Базові перевірки для Python
        if 'def ' in code or 'class ' in code:
            lines = code.split('\n')
            
            # Перевірка docstrings
            if 'def ' in code and '"""' not in code and "'''" not in code:
                suggestions.append("• Рекомендую додати docstrings до функцій")
            
            # Перевірка довжини рядків
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 80]
            if long_lines:
                suggestions.append(f"• Довгі рядки: {', '.join(map(str, long_lines[:3]))}")
            
            # Перевірка імпортів
            imports = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
            if len(imports) > 5:
                suggestions.append("• Багато імпортів - розгляньте групування")
            
            # Перевірка складності
            if code.count('if ') > 5:
                suggestions.append("• Висока циклічна складність - розгляньте рефакторинг")
        
        # Перевірки для JavaScript
        elif 'function' in code or 'const ' in code or 'let ' in code:
            if 'console.log' in code:
                suggestions.append("• Знайдено console.log - не забудьте видалити перед продакшеном")
            
            if 'var ' in code:
                suggestions.append("• Використовуйте const/let замість var")
        
        if not suggestions:
            suggestions.append("• Код виглядає добре! Продовжуйте в тому ж дусі.")
        
        return '\n'.join(suggestions)
    
    async def insert_code_template(self, template_type, language='python'):
        """Вставка шаблону коду"""
        try:
            if language in self.code_suggestions and template_type in self.code_suggestions[language]:
                template = self.code_suggestions[language][template_type]
                
                # Вставка шаблону
                pyautogui.write(template)
                
                return f"Вставлено шаблон {template_type} для {language}"
            else:
                return f"Шаблон {template_type} для {language} не знайдено."
                
        except Exception as e:
            logging.error(f"Помилка вставки шаблону: {e}")
            return "Помилка при вставці шаблону коду."
    
    async def format_code(self):
        """Форматування коду"""
        try:
            # Спроба автоформатування через IDE
            pyautogui.hotkey('ctrl', 'shift', 'i')  # VS Code format
            time.sleep(0.5)
            
            # Альтернативні комбінації для інших IDE
            pyautogui.hotkey('ctrl', 'alt', 'l')  # PyCharm format
            
            return "Код відформатовано."
            
        except Exception as e:
            logging.error(f"Помилка форматування: {e}")
            return "Помилка при форматуванні коду."
    
    async def run_code(self):
        """Запуск поточного коду"""
        try:
            # Збереження файлу
            pyautogui.hotkey('ctrl', 's')
            time.sleep(0.5)
            
            # Запуск коду
            pyautogui.key('f5')  # VS Code run
            
            return "Код запущено."
            
        except Exception as e:
            logging.error(f"Помилка запуску коду: {e}")
            return "Помилка при запуску коду."
    
    async def create_new_file(self, file_type='python'):
        """Створення нового файлу"""
        try:
            # Новий файл
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(0.5)
            
            # Додавання базового шаблону
            if file_type == 'python':
                template = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"""\nModule description\n"""\n\n'
                pyautogui.write(template)
            elif file_type == 'javascript':
                template = '// JavaScript file\n\n'
                pyautogui.write(template)
            
            return f"Створено новий {file_type} файл з базовим шаблоном."
            
        except Exception as e:
            logging.error(f"Помилка створення файлу: {e}")
            return "Помилка при створенні нового файлу."

# Глобальний екземпляр
code_assistant = CodeAssistant()

async def analyze_code():
    """Аналіз поточного коду"""
    return await code_assistant.analyze_current_code()

async def insert_template(template_type, language='python'):
    """Вставка шаблону коду"""
    return await code_assistant.insert_code_template(template_type, language)

async def format_current_code():
    """Форматування коду"""
    return await code_assistant.format_code()

async def run_current_code():
    """Запуск коду"""
    return await code_assistant.run_code()

async def create_file(file_type='python'):
    """Створення нового файлу"""
    return await code_assistant.create_new_file(file_type)

# Тестування
if __name__ == "__main__":
    async def test_code_assistant():
        result = await analyze_code()
        print(result)
    
    asyncio.run(test_code_assistant())
