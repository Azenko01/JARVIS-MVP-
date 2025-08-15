#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Інтеграція з OpenAI GPT для JARVIS
"""

import openai
import asyncio
import logging
import json
from config import Config

class GPTIntegration:
    def __init__(self):
        self.config = Config()
        self.client = None
        self._setup_client()
        
    def _setup_client(self):
        """Налаштування OpenAI клієнта"""
        try:
            if self.config.OPENAI_API_KEY:
                openai.api_key = self.config.OPENAI_API_KEY
                self.client = openai
                logging.info("OpenAI клієнт налаштовано успішно")
            else:
                logging.warning("OpenAI API ключ не знайдено")
        except Exception as e:
            logging.error(f"Помилка налаштування OpenAI: {e}")
    
    async def chat_completion(self, messages, model="gpt-3.5-turbo", max_tokens=1000):
        """
        Отримання відповіді від GPT
        
        Args:
            messages (list): Список повідомлень для GPT
            model (str): Модель GPT
            max_tokens (int): Максимальна кількість токенів
            
        Returns:
            str: Відповідь від GPT
        """
        try:
            if not self.client:
                return "OpenAI API недоступний. Перевірте налаштування."
            
            response = await asyncio.to_thread(
                self.client.ChatCompletion.create,
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Помилка GPT запиту: {e}")
            return f"Помилка при обробці запиту: {str(e)}"
    
    async def analyze_pdf_content(self, pdf_text):
        """Аналіз PDF контенту через GPT"""
        try:
            messages = [
                {
                    "role": "system", 
                    "content": """Ти - асистент JARVIS. Проаналізуй наданий текст з PDF та витягни ключові знання.
                    Структуруй відповідь у JSON форматі з полями:
                    - summary: короткий опис документа
                    - key_points: список ключових моментів
                    - topics: список тем
                    - actionable_items: що можна зробити на основі цієї інформації
                    
                    Відповідай українською мовою."""
                },
                {
                    "role": "user",
                    "content": f"Проаналізуй цей текст з PDF:\n\n{pdf_text[:4000]}"
                }
            ]
            
            response = await self.chat_completion(messages, max_tokens=1500)
            
            # Спроба парсингу JSON
            try:
                knowledge_data = json.loads(response)
                return knowledge_data
            except json.JSONDecodeError:
                # Якщо не JSON, повертаємо як текст
                return {
                    "summary": "Аналіз PDF документа",
                    "content": response,
                    "source": "gpt_analysis"
                }
                
        except Exception as e:
            logging.error(f"Помилка аналізу PDF: {e}")
            return None
    
    async def answer_question(self, question, context=""):
        """Відповідь на загальні питання"""
        try:
            system_prompt = f"""Ти - JARVIS, персональний AI асистент Олександра Азенка.
            Ти розумна, ввічлива та корисна. Відповідаєш українською мовою.
            Твоя особистість: професійна, але дружня, як у фільмі "Залізна людина".
            
            Контекст (якщо є): {context}
            
            Відповідай коротко та по суті, але дружньо."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = await self.chat_completion(messages)
            return response
            
        except Exception as e:
            logging.error(f"Помилка відповіді на питання: {e}")
            return "Вибачте, не можу обробити це питання зараз."
    
    async def generate_code_suggestions(self, code_snippet, language="python"):
        """Генерація підказок для коду"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Ти - експерт програміст. Проаналізуй код на {language} та дай конструктивні поради.
                    Відповідай українською мовою. Формат відповіді:
                    1. Загальна оцінка коду
                    2. Конкретні покращення
                    3. Потенційні проблеми
                    4. Рекомендації"""
                },
                {
                    "role": "user",
                    "content": f"Проаналізуй цей код:\n\n```{language}\n{code_snippet}\n```"
                }
            ]
            
            response = await self.chat_completion(messages, max_tokens=800)
            return response
            
        except Exception as e:
            logging.error(f"Помилка аналізу коду: {e}")
            return "Не вдалося проаналізувати код."
    
    async def create_learning_summary(self, interactions_history):
        """Створення зведення навчання"""
        try:
            history_text = "\n".join([
                f"Користувач: {item['user_input']}\nJARVIS: {item['jarvis_response']}"
                for item in interactions_history[-10:]  # Останні 10 взаємодій
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": """Проаналізуй історію взаємодій з користувачем та створи короткий звіт:
                    - Що нового вивчив JARVIS
                    - Які команди використовуються найчастіше
                    - Рекомендації для покращення
                    Відповідай українською мовою."""
                },
                {
                    "role": "user",
                    "content": f"Історія взаємодій:\n{history_text}"
                }
            ]
            
            response = await self.chat_completion(messages, max_tokens=600)
            return response
            
        except Exception as e:
            logging.error(f"Помилка створення зведення: {e}")
            return "Не вдалося створити звіт навчання."

# Глобальний екземпляр
gpt_integration = GPTIntegration()

async def ask_gpt(question, context=""):
    """Функція для використання в main.py"""
    return await gpt_integration.answer_question(question, context)

async def analyze_pdf_with_gpt(pdf_text):
    """Аналіз PDF через GPT"""
    return await gpt_integration.analyze_pdf_content(pdf_text)

async def get_code_suggestions(code, language="python"):
    """Отримання підказок для коду"""
    return await gpt_integration.generate_code_suggestions(code, language)

async def create_learning_report(history):
    """Створення звіту навчання"""
    return await gpt_integration.create_learning_summary(history)

# Тестування
if __name__ == "__main__":
    async def test_gpt():
        result = await ask_gpt("Як справи?")
        print(result)
    
    asyncio.run(test_gpt())
