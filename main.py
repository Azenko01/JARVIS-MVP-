#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS v2.0 - Повноцінний AI Desktop Assistant
Автор: Oleksandr Azenko

Головний файл з FSM (Finite State Machine) архітектурою
"""

import asyncio
import threading
import time
import logging
import sys
import os
from enum import Enum
from pathlib import Path

# Імпорти модулів JARVIS
from voice.listener import VoiceListener
from voice.speaker import VoiceSpeaker
from memory.learner import JarvisLearner
from memory.vector_knowledge import vector_kb
from plugins import weather, open_apps, search_web, shutdown, visual_assistant
from plugins.gpt_integration import gpt_integration, ask_gpt
from config import Config

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class JarvisState(Enum):
    """Стани JARVIS"""
    INACTIVE = "inactive"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    LEARNING = "learning"
    ERROR = "error"

class SecurityLevel(Enum):
    """Рівні безпеки команд"""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"

class JarvisAssistant:
    def __init__(self, gui_mode=False):
        self.config = Config()
        self.gui_mode = gui_mode
        
        # Ініціалізація компонентів
        self.listener = VoiceListener()
        self.speaker = VoiceSpeaker()
        self.learner = JarvisLearner()
        
        # Стан системи
        self.state = JarvisState.INACTIVE
        self.is_active = False
        self.is_listening = False
        self.show_on_screen = False
        self.start_time = time.time()
        self.current_command = ""
        self.current_response = ""
        
        # Статистика
        self.stats = {
            'total_interactions': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'learning_sessions': 0
        }
        
        # Плагіни
        self.plugins = {
            'weather': weather,
            'open_apps': open_apps,
            'search_web': search_web,
            'shutdown': shutdown,
            'visual_assistant': visual_assistant
        }
        
        # Telegram бот
        self.telegram_bot_task = None
        
        # Система безпеки
        self.security_commands = {
            SecurityLevel.DANGEROUS: [
                'вимкни комп', 'shutdown', 'format', 'delete system',
                'rm -rf', 'перезавантаж', 'restart'
            ],
            SecurityLevel.CAUTION: [
                'закрий всі', 'kill process', 'terminate'
            ]
        }
        
        logging.info("JARVIS Assistant ініціалізовано")
    
    async def initialize(self):
        """Ініціалізація всіх систем"""
        try:
            print("Ініціалізація JARVIS v2.0...")
            
            # Перевірка API ключів
            api_status = self.config.get_api_status()
            print(f"OpenAI API: {'OK' if api_status['openai'] else 'NOT SET'}")
            print(f"Weather API: {'OK' if api_status['weather'] else 'NOT SET'}")
            print(f"Telegram Bot: {'OK' if api_status['telegram'] else 'NOT SET'}")
            
            # Ініціалізація векторної бази
            vector_stats = vector_kb.get_statistics()
            print(f"Векторна база: {vector_stats['total_documents']} документів")
            
            # Запуск Telegram бота
            if api_status['telegram']:
                await self._start_telegram_bot()
            
            # Калібрування голосу
            if not self.gui_mode:
                print("Калібрування мікрофона...")
            
            print("Ініціалізація завершена")
            return True
            
        except Exception as e:
            logging.error(f"Помилка ініціалізації: {e}")
            return False
    
    async def _start_telegram_bot(self):
        """Запуск Telegram бота"""
        try:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            authorized_users_str = os.getenv("TELEGRAM_AUTHORIZED_USERS", "")
            
            if bot_token:
                authorized_users = []
                if authorized_users_str:
                    authorized_users = [int(uid.strip()) for uid in authorized_users_str.split(",")]
                
                # Запуск в окремому потоці
                def run_bot():
                    from plugins.telegram_bot import start_telegram_bot
                    asyncio.run(start_telegram_bot(bot_token, authorized_users, self))
                
                bot_thread = threading.Thread(target=run_bot, daemon=True)
                bot_thread.start()
                
                logging.info("Telegram бот запущено")
                
        except Exception as e:
            logging.error(f"Помилка запуску Telegram бота: {e}")
    
    async def start(self):
        """Запуск JARVIS"""
        if not await self.initialize():
            print("Помилка ініціалізації. Завершення роботи.")
            return
        
        self.is_active = True
        self.state = JarvisState.LISTENING
        
        if not self.gui_mode:
            await self.speaker.speak("Вітаю, Олександре! JARVIS версії 2.0 готовий до роботи!")
        
        print("Очікую активаційну фразу 'Привіт, Джарвіс'...")
        
        # Основний цикл
        await self.main_loop()
    
    async def main_loop(self):
        """Основний цикл роботи (FSM)"""
        while self.is_active:
            try:
                if self.state == JarvisState.LISTENING:
                    await self._handle_listening_state()
                elif self.state == JarvisState.PROCESSING:
                    await self._handle_processing_state()
                elif self.state == JarvisState.RESPONDING:
                    await self._handle_responding_state()
                elif self.state == JarvisState.LEARNING:
                    await self._handle_learning_state()
                elif self.state == JarvisState.ERROR:
                    await self._handle_error_state()
                
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                await self.shutdown()
                break
            except Exception as e:
                logging.error(f"Помилка в основному циклі: {e}")
                self.state = JarvisState.ERROR
                await asyncio.sleep(1)
    
    async def _handle_listening_state(self):
        """Обробка стану прослуховування"""
        if not self.is_listening:
            # Очікування активаційної фрази
            text = await self.listener.listen_for_activation()
            if text and self.is_activation_phrase(text):
                await self.activate()
        else:
            # Активний режим - прослуховування команд
            text = await self.listener.listen()
            if text:
                self.current_command = text
                self.state = JarvisState.PROCESSING
    
    async def _handle_processing_state(self):
        """Обробка стану обробки команди"""
        try:
            # Перевірка безпеки
            security_level = self.check_command_security(self.current_command)
            
            if security_level == SecurityLevel.DANGEROUS:
                if not await self.confirm_dangerous_command(self.current_command):
                    self.current_response = "Команду скасовано з міркувань безпеки."
                    self.state = JarvisState.RESPONDING
                    return
            
            # Логування команди
            self.learner.log_interaction(self.current_command, "command")
            self.stats['total_interactions'] += 1
            
            # Обробка команди
            self.current_response = await self.execute_command(self.current_command)
            
            if self.current_response:
                self.stats['successful_commands'] += 1
            else:
                self.stats['failed_commands'] += 1
                self.current_response = "Не вдалося виконати команду."
            
            self.state = JarvisState.RESPONDING
            
        except Exception as e:
            logging.error(f"Помилка обробки команди: {e}")
            self.current_response = f"Помилка обробки: {str(e)}"
            self.stats['failed_commands'] += 1
            self.state = JarvisState.RESPONDING
    
    async def _handle_responding_state(self):
        """Обробка стану відповіді"""
        try:
            # Логування відповіді
            self.learner.log_interaction(self.current_response, "response")
            
            # Додавання до векторної бази
            vector_kb.add_interaction(self.current_command, self.current_response)
            
            # Відповідь користувачу
            if self.show_on_screen or self.gui_mode:
                print(f"JARVIS: {self.current_response}")
            else:
                await self.speaker.speak(self.current_response)
            
            # Повернення до прослуховування
            self.state = JarvisState.LISTENING
            
            # Автоматичне відключення після команди
            if self.is_listening:
                await asyncio.sleep(2)
                self.is_listening = False
                if not self.gui_mode:
                    print("Очікую наступну активацію...")
            
        except Exception as e:
            logging.error(f"Помилка відповіді: {e}")
            self.state = JarvisState.ERROR
    
    async def _handle_learning_state(self):
        """Обробка стану навчання"""
        try:
            self.stats['learning_sessions'] += 1
            self.state = JarvisState.LISTENING
        except Exception as e:
            logging.error(f"Помилка навчання: {e}")
            self.state = JarvisState.ERROR
    
    async def _handle_error_state(self):
        """Обробка стану помилки"""
        try:
            await asyncio.sleep(1)
            self.state = JarvisState.LISTENING
        except Exception as e:
            logging.error(f"Критична помилка: {e}")
            await self.shutdown()
    
    def check_command_security(self, command):
        """Перевірка рівня безпеки команди"""
        command_lower = command.lower()
        
        for level, keywords in self.security_commands.items():
            if any(keyword in command_lower for keyword in keywords):
                return level
        
        return SecurityLevel.SAFE
    
    async def confirm_dangerous_command(self, command):
        """Підтвердження небезпечної команди"""
        if self.gui_mode:
            return False
        
        await self.speaker.speak("Це небезпечна команда. Скажіть 'підтверджую' для виконання або 'скасувати' для відміни.")
        
        confirmation = await self.listener.listen(timeout=10)
        if confirmation:
            return "підтверджую" in confirmation.lower() or "confirm" in confirmation.lower()
        
        return False
    
    def is_activation_phrase(self, text):
        """Перевірка активаційної фрази"""
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.config.ACTIVATION_PHRASES)
    
    async def activate(self):
        """Активація асистента"""
        self.is_listening = True
        
        if not self.gui_mode:
            responses = self.config.GREETING_RESPONSES
            import random
            await self.speaker.speak(random.choice(responses))
        
        # Автоматичне відключення через 30 секунд
        asyncio.create_task(self.auto_deactivate())
    
    async def auto_deactivate(self):
        """Автоматичне відключення"""
        await asyncio.sleep(30)
        if self.is_listening:
            self.is_listening = False
            if not self.gui_mode:
                await self.speaker.speak("Переходжу в режим очікування.")
    
    async def execute_command(self, text):
        """Виконання команди з розширеною логікою"""
        text_lower = text.lower()
        
        # Команди керування режимами
        if "напиши на екрані" in text_lower:
            self.show_on_screen = True
            return "Переключився в текстовий режим."
        
        if "говори голосом" in text_lower:
            self.show_on_screen = False
            return "Повернувся до голосового режиму."
        
        # Команди завершення
        if any(word in text_lower for word in ["стоп", "вихід", "завершити", "stop", "exit"]):
            asyncio.create_task(self.shutdown())
            return "Завершую роботу. До побачення!"
        
        # Перевірка кастомних команд
        custom_response = self.learner.get_custom_command(text)
        if custom_response:
            return custom_response
        
        # Системні команди
        if "відкрий" in text_lower or "запусти" in text_lower:
            return await self.plugins['open_apps'].handle_open_command(text)
        
        if "закрий" in text_lower:
            return await self.plugins['open_apps'].handle_close_command(text)
        
        if "погода" in text_lower:
            return await self.plugins['weather'].get_weather()
        
        if "пошукай" in text_lower or "знайди" in text_lower:
            return await self.plugins['search_web'].search(text)
        
        if "вимкни" in text_lower or "перезавантаж" in text_lower:
            return await self.plugins['shutdown'].handle_shutdown_command(text)
        
        if "що на екрані" in text_lower or "що бачиш" in text_lower:
            return await self.plugins['visual_assistant'].analyze_screen()
        
        if "включи музику" in text_lower:
            return await self.plugins['open_apps'].open_music()
        
        # Команди програмування
        if "аналізуй код" in text_lower:
            try:
                from plugins.code_assistant import analyze_code
                return await analyze_code()
            except ImportError:
                return "Модуль аналізу коду недоступний."
        
        # Команди навчання
        if "навчися" in text_lower or "запам'ятай" in text_lower:
            return await self.handle_learning_command(text)
        
        if "онови себе" in text_lower:
            return await self.handle_update_command()
        
        # Команди роботи з знаннями
        if "що ти знаєш про" in text_lower or "розкажи про" in text_lower:
            return await self.handle_knowledge_query(text)
        
        # Загальні запитання через GPT
        return await self.handle_general_question(text)
    
    async def handle_learning_command(self, text):
        """Обробка команд навчання"""
        self.state = JarvisState.LEARNING
        
        if "pdf" in text.lower():
            return await self.handle_pdf_learning()
        
        if not self.gui_mode:
            await self.speaker.speak("Я слухаю. Назви команду та опиши її дію.")
            new_command = await self.listener.listen(timeout=10)
            
            if new_command:
                success = self.learner.learn_custom_command(new_command)
                if success:
                    vector_kb.add_document(new_command, {"type": "custom_command"})
                    return "Команду вивчено та додано до бази знань!"
                else:
                    return "Не вдалося вивчити команду."
        
        return "Навчання доступне тільки в голосовому режимі."
    
    async def handle_update_command(self):
        """Комплексне оновлення системи"""
        updates = []
        
        try:
            # Оновлення з GitHub
            if await self.learner.update_from_github():
                updates.append("код з GitHub")
        except Exception as e:
            logging.error(f"Помилка оновлення GitHub: {e}")
        
        try:
            # Оновлення бази знань
            if self.learner.update_knowledge_base():
                updates.append("база знань")
        except Exception as e:
            logging.error(f"Помилка оновлення знань: {e}")
        
        if updates:
            return f"Успішно оновлено: {', '.join(updates)}"
        else:
            return "Всі компоненти актуальні."
    
    async def handle_knowledge_query(self, text):
        """Обробка запитів про знання"""
        try:
            # Пошук в векторній базі
            results = vector_kb.search(text, top_k=3)
            
            if results:
                context = "\n".join([result['text'] for result in results[:2]])
                return await ask_gpt(text, context)
            else:
                return await ask_gpt(text)
                
        except Exception as e:
            logging.error(f"Помилка обробки запиту знань: {e}")
            return "Не можу знайти інформацію про це."
    
    async def handle_general_question(self, text):
        """Обробка загальних запитань"""
        try:
            context = vector_kb.find_relevant_context(text)
            response = await ask_gpt(text, context)
            return response
        except Exception as e:
            logging.error(f"Помилка GPT запиту: {e}")
            return "Не можу обробити це питання зараз."
    
    async def handle_pdf_learning(self):
        """Навчання з PDF"""
        if not self.gui_mode:
            await self.speaker.speak("Перетягніть PDF файл в папку knowledge_base або назвіть шлях до файлу.")
        
        return "PDF навчання доступне через GUI або файлову систему."
    
    def get_statistics(self):
        """Отримання статистики"""
        uptime = time.time() - self.start_time
        
        return {
            **self.stats,
            'uptime_seconds': int(uptime),
            'uptime_formatted': self.format_uptime(uptime),
            'state': self.state.value,
            'is_active': self.is_active,
            'is_listening': self.is_listening
        }
    
    def format_uptime(self, seconds):
        """Форматування часу роботи"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    async def shutdown(self):
        """Завершення роботи"""
        self.is_active = False
        self.is_listening = False
        self.state = JarvisState.INACTIVE
        
        # Збереження статистики
        try:
            final_stats = self.get_statistics()
            logging.info(f"Фінальна статистика: {final_stats}")
        except Exception as e:
            logging.error(f"Помилка збереження статистики: {e}")
        
        if not self.gui_mode:
            await self.speaker.speak("До побачення, Олександре! JARVIS завершує роботу.")
        
        logging.info("JARVIS завершив роботу")

async def main():
    """Головна функція"""
    # Перевірка аргументів командного рядка
    gui_mode = "--gui" in sys.argv or "-g" in sys.argv
    
    if gui_mode:
        # Запуск GUI
        try:
            from gui.main_window import JarvisGUI
            app = JarvisGUI()
            app.run()
        except ImportError:
            print("GUI модуль недоступний. Запускаю в консольному режимі.")
            gui_mode = False
    
    if not gui_mode:
        # Запуск в консольному режимі
        jarvis = JarvisAssistant(gui_mode=False)
        try:
            await jarvis.start()
        except KeyboardInterrupt:
            print("\nJARVIS завершує роботу...")
        except Exception as e:
            logging.error(f"Критична помилка: {e}")
            print(f"Помилка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
