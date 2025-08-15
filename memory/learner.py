#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль навчання та пам'яті JARVIS
"""

import sqlite3
import json
import datetime
import logging
from pathlib import Path
from config import Config

class JarvisLearner:
    def __init__(self):
        self.config = Config()
        self.db_path = self.config.DATABASE_PATH
        self.knowledge_base_path = self.config.KNOWLEDGE_BASE_DIR / "pdf_data.json"
        self.notes_path = self.config.KNOWLEDGE_BASE_DIR / "notes.txt"
        
        self._init_database()
        self._load_knowledge_base()
        
        logging.info("JarvisLearner ініціалізовано")
    
    def _init_database(self):
        """Ініціалізація бази даних"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблиця взаємодій
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_input TEXT,
                        jarvis_response TEXT,
                        interaction_type TEXT,
                        success BOOLEAN DEFAULT TRUE
                    )
                ''')
                
                # Таблиця кастомних команд
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS custom_commands (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command_pattern TEXT UNIQUE,
                        action_description TEXT,
                        response_template TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        usage_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Таблиця знань
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT,
                        content TEXT,
                        source TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logging.info("База даних ініціалізована")
                
        except Exception as e:
            logging.error(f"Помилка ініціалізації бази даних: {e}")
    
    def _load_knowledge_base(self):
        """Завантаження бази знань"""
        try:
            if self.knowledge_base_path.exists():
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    self.knowledge_data = json.load(f)
            else:
                self.knowledge_data = {}
                self._save_knowledge_base()
                
        except Exception as e:
            logging.error(f"Помилка завантаження бази знань: {e}")
            self.knowledge_data = {}
    
    def _save_knowledge_base(self):
        """Збереження бази знань"""
        try:
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Помилка збереження бази знань: {e}")
    
    def log_interaction(self, user_input, interaction_type, jarvis_response="", success=True):
        """
        Логування взаємодії з користувачем
        
        Args:
            user_input (str): Введення користувача
            interaction_type (str): Тип взаємодії (command, question, learning)
            jarvis_response (str): Відповідь JARVIS
            success (bool): Чи успішна взаємодія
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO interactions 
                    (user_input, jarvis_response, interaction_type, success)
                    VALUES (?, ?, ?, ?)
                ''', (user_input, jarvis_response, interaction_type, success))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка логування взаємодії: {e}")
    
    def learn_custom_command(self, command_text):
        """
        Навчання новій кастомній команді
        
        Args:
            command_text (str): Опис команди від користувача
            
        Returns:
            bool: Успішність навчання
        """
        try:
            # Парсинг команди (спрощена версія)
            # Формат: "Коли я скажу 'команда', виконай дію"
            import re
            
            pattern = r"коли я скажу ['\"](.+?)['\"],?\s*(.+)"
            match = re.search(pattern, command_text.lower())
            
            if match:
                command_pattern = match.group(1)
                action_description = match.group(2)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO custom_commands 
                        (command_pattern, action_description, response_template)
                        VALUES (?, ?, ?)
                    ''', (command_pattern, action_description, f"Виконую: {action_description}"))
                    conn.commit()
                
                logging.info(f"Вивчено нову команду: {command_pattern}")
                return True
            else:
                logging.warning(f"Не вдалося розпарсити команду: {command_text}")
                return False
                
        except Exception as e:
            logging.error(f"Помилка навчання команді: {e}")
            return False
    
    def get_custom_command(self, user_input):
        """
        Пошук кастомної команди
        
        Args:
            user_input (str): Введення користувача
            
        Returns:
            str: Відповідь або None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT command_pattern, response_template FROM custom_commands')
                commands = cursor.fetchall()
                
                user_input_lower = user_input.lower()
                
                for pattern, response in commands:
                    if pattern.lower() in user_input_lower:
                        # Оновлення лічильника використання
                        cursor.execute('''
                            UPDATE custom_commands 
                            SET usage_count = usage_count + 1 
                            WHERE command_pattern = ?
                        ''', (pattern,))
                        conn.commit()
                        
                        return response
                
                return None
                
        except Exception as e:
            logging.error(f"Помилка пошуку кастомної команди: {e}")
            return None
    
    def add_knowledge(self, topic, content, source="user"):
        """
        Додавання знань до бази
        
        Args:
            topic (str): Тема
            content (str): Зміст
            source (str): Джерело знань
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO knowledge (topic, content, source)
                    VALUES (?, ?, ?)
                ''', (topic, content, source))
                conn.commit()
                
            logging.info(f"Додано знання по темі: {topic}")
            
        except Exception as e:
            logging.error(f"Помилка додавання знань: {e}")
    
    def search_knowledge(self, query):
        """
        Пошук знань в базі
        
        Args:
            query (str): Пошуковий запит
            
        Returns:
            list: Список знайдених знань
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT topic, content, source FROM knowledge 
                    WHERE topic LIKE ? OR content LIKE ?
                    ORDER BY updated_at DESC
                ''', (f'%{query}%', f'%{query}%'))
                
                results = cursor.fetchall()
                return [{'topic': r[0], 'content': r[1], 'source': r[2]} for r in results]
                
        except Exception as e:
            logging.error(f"Помилка пошуку знань: {e}")
            return []
    
    def get_interaction_history(self, limit=10):
        """
        Отримання історії взаємодій
        
        Args:
            limit (int): Кількість записів
            
        Returns:
            list: Історія взаємодій
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, user_input, jarvis_response, interaction_type 
                    FROM interactions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                return [{
                    'timestamp': r[0],
                    'user_input': r[1],
                    'jarvis_response': r[2],
                    'type': r[3]
                } for r in results]
                
        except Exception as e:
            logging.error(f"Помилка отримання історії: {e}")
            return []
    
    def save_note(self, note_text):
        """
        Збереження нотатки
        
        Args:
            note_text (str): Текст нотатки
            
        Returns:
            bool: Успішність збереження
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note_entry = f"[{timestamp}] {note_text}\n"
            
            with open(self.notes_path, 'a', encoding='utf-8') as f:
                f.write(note_entry)
            
            logging.info("Нотатку збережено")
            return True
            
        except Exception as e:
            logging.error(f"Помилка збереження нотатки: {e}")
            return False
    
    async def update_from_github(self):
        """Оновлення коду з GitHub репозиторію"""
        try:
            import subprocess
            import os
            
            # Перевірка наявності git
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logging.warning("Git не встановлений")
                return False
            
            # Перевірка наявності .git папки
            if not os.path.exists('.git'):
                logging.info("Не Git репозиторій")
                return False
            
            # Оновлення з remote
            result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("Код успішно оновлено з GitHub")
                return True
            else:
                logging.error(f"Помилка оновлення: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Помилка оновлення з GitHub: {e}")
            return False
    
    async def learn_from_pdf(self, pdf_path):
        """Навчання з PDF файлу через GPT"""
        try:
            import PyPDF2
            import openai
            
            # Читання PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            if not text.strip():
                return False
            
            # Обробка через GPT (якщо є API ключ)
            if self.config.OPENAI_API_KEY:
                openai.api_key = self.config.OPENAI_API_KEY
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Витягни ключові знання з цього тексту та структуруй їх у JSON форматі з темами та описами."},
                        {"role": "user", "content": text[:4000]}  # Обмеження токенів
                    ]
                )
                
                knowledge_json = response.choices[0].message.content
                
                # Збереження знань
                import json
                try:
                    knowledge_data = json.loads(knowledge_json)
                    self.knowledge_data['pdf_learnings'] = self.knowledge_data.get('pdf_learnings', [])
                    self.knowledge_data['pdf_learnings'].append({
                        'source': pdf_path,
                        'learned_at': datetime.datetime.now().isoformat(),
                        'knowledge': knowledge_data
                    })
                    self._save_knowledge_base()
                    return True
                except json.JSONDecodeError:
                    # Fallback - зберігаємо як текст
                    self.add_knowledge("PDF_Content", text[:1000], pdf_path)
                    return True
            else:
                # Без GPT - просто зберігаємо текст
                self.add_knowledge("PDF_Content", text[:1000], pdf_path)
                return True
                
        except Exception as e:
            logging.error(f"Помилка навчання з PDF: {e}")
            return False
    
    async def update_plugins(self):
        """Оновлення плагінів"""
        try:
            plugins_updated = 0
            
            # Список доступних плагінів для оновлення
            available_plugins = [
                'weather_extended.py',
                'code_assistant.py', 
                'system_monitor.py'
            ]
            
            for plugin in available_plugins:
                # Тут буде логіка завантаження нових плагінів
                # Поки що заглушка
                pass
            
            return plugins_updated > 0
            
        except Exception as e:
            logging.error(f"Помилка оновлення плагінів: {e}")
            return False
    
    def update_knowledge_base(self):
        """
        Оновлення бази знань
        
        Returns:
            bool: Чи були оновлення
        """
        try:
            # Тут буде логіка оновлення знань з інтернету
            # Поки що заглушка
            
            current_time = datetime.datetime.now().isoformat()
            self.knowledge_data['last_update'] = current_time
            self._save_knowledge_base()
            
            logging.info("База знань оновлена")
            return True
            
        except Exception as e:
            logging.error(f"Помилка оновлення бази знань: {e}")
            return False
    
    def get_statistics(self):
        """
        Отримання статистики використання
        
        Returns:
            dict: Статистика
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Загальна кількість взаємодій
                cursor.execute('SELECT COUNT(*) FROM interactions')
                total_interactions = cursor.fetchone()[0]
                
                # Кількість кастомних команд
                cursor.execute('SELECT COUNT(*) FROM custom_commands')
                custom_commands = cursor.fetchone()[0]
                
                # Кількість знань
                cursor.execute('SELECT COUNT(*) FROM knowledge')
                knowledge_count = cursor.fetchone()[0]
                
                return {
                    'total_interactions': total_interactions,
                    'custom_commands': custom_commands,
                    'knowledge_count': knowledge_count,
                    'last_update': self.knowledge_data.get('last_update', 'Never')
                }
                
        except Exception as e:
            logging.error(f"Помилка отримання статистики: {e}")
            return {}

# Тестування модуля
if __name__ == "__main__":
    learner = JarvisLearner()
    
    # Тестування
    learner.log_interaction("тест", "test", "тестова відповідь")
    learner.learn_custom_command("Коли я скажу 'відкрий калькулятор', відкрий програму calc.exe")
    
    print("Статистика:", learner.get_statistics())
    print("Історія:", learner.get_interaction_history(5))
