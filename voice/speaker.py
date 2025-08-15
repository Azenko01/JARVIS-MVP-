#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль синтезу мовлення для JARVIS
"""

import pyttsx3
import asyncio
import logging
from config import Config

class VoiceSpeaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.config = Config()
        self._setup_voice()
        
        logging.info("VoiceSpeaker ініціалізовано")
    
    def _setup_voice(self):
        """Налаштування голосу"""
        try:
            # Отримання доступних голосів
            voices = self.engine.getProperty('voices')
            
            # Пошук жіночого голосу
            female_voice = None
            for voice in voices:
                if voice.name and ('female' in voice.name.lower() or 
                                 'жіночий' in voice.name.lower() or
                                 'zira' in voice.name.lower() or
                                 'hazel' in voice.name.lower()):
                    female_voice = voice
                    break
            
            # Встановлення голосу
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
                logging.info(f"Встановлено жіночий голос: {female_voice.name}")
            else:
                # Використання першого доступного голосу
                if voices:
                    self.engine.setProperty('voice', voices[1].id)
                    logging.info(f"Встановлено голос: {voices[1].name}")
            
            # Налаштування параметрів
            self.engine.setProperty('rate', self.config.VOICE_RATE)
            self.engine.setProperty('volume', self.config.VOICE_VOLUME)
            
        except Exception as e:
            logging.error(f"Помилка налаштування голосу: {e}")
    
    async def speak(self, text):
        """
        Асинхронне озвучування тексту
        
        Args:
            text (str): Текст для озвучування
        """
        if not text:
            return
            
        try:
            print(f"JARVIS: {text}")
            
            # Запуск в окремому потоці для асинхронності
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._speak_sync, text)
            
        except Exception as e:
            logging.error(f"Помилка при озвучуванні: {e}")
    
    def _speak_sync(self, text):
        """Синхронне озвучування"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Помилка синхронного озвучування: {e}")
    
    def set_voice_properties(self, rate=None, volume=None):
        """
        Зміна властивостей голосу
        
        Args:
            rate (int): Швидкість мовлення (слів за хвилину)
            volume (float): Гучність (0.0 - 1.0)
        """
        try:
            if rate is not None:
                self.engine.setProperty('rate', rate)
                logging.info(f"Швидкість мовлення змінено на: {rate}")
            
            if volume is not None:
                self.engine.setProperty('volume', volume)
                logging.info(f"Гучність змінено на: {volume}")
                
        except Exception as e:
            logging.error(f"Помилка зміни властивостей голосу: {e}")
    
    def get_available_voices(self):
        """Отримання списку доступних голосів"""
        try:
            voices = self.engine.getProperty('voices')
            voice_info = []
            
            for voice in voices:
                voice_info.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender if hasattr(voice, 'gender') else 'Unknown',
                    'age': voice.age if hasattr(voice, 'age') else 'Unknown'
                })
            
            return voice_info
            
        except Exception as e:
            logging.error(f"Помилка отримання списку голосів: {e}")
            return []
    
    async def test_voice(self):
        """Тестування голосу (ВИПРАВЛЕНО)"""
        test_phrases = [
            "Привіт! Я JARVIS, ваш персональний асистент.",
            "Тестую якість мого голосу.",
            "Як вам подобається моє звучання?"
        ]
        
        for phrase in test_phrases:
            await self.speak(phrase)
            await asyncio.sleep(1)

    def get_personalized_response(self, response_type):
        """Отримання персоналізованих відповідей"""
        responses = {
            'greeting': [
                "Слухаю тебе, Олександре.",
                "Так, я тут. Що потрібно зробити?",
                "Готова допомогти. Яка команда?",
                "Вітаю! Чим можу бути корисною?"
            ],
            'success': [
                "Гаразд, виконано.",
                "Завдання виконано успішно.",
                "Готово! Що ще потрібно?",
                "Зроблено. Чим ще допомогти?"
            ],
            'error': [
                "Вибачте, виникла помилка.",
                "Щось пішло не так. Спробуємо ще раз?",
                "Не вдалося виконати команду.",
                "Помилка виконання. Потрібна допомога?"
            ],
            'learning': [
                "Цікаво! Запам'ятовую це.",
                "Додаю до своїх знань.",
                "Вивчила! Тепер знаю, як це робити.",
                "Дякую за навчання. Стала розумнішою!"
            ]
        }
        
        import random
        return random.choice(responses.get(response_type, ["Зрозуміло."]))

# Тестування модуля
if __name__ == "__main__":
    import sys
    
    async def test_speaker():
        speaker = VoiceSpeaker()
        
        # Показати доступні голоси
        voices = speaker.get_available_voices()
        print("Доступні голоси:")
        for voice in voices:
            print(f"- {voice['name']} ({voice['gender']})")
        
        # Тестування голосу
        await speaker.test_voice()
        
        # Тест персоналізованої відповіді
        print("Персоналізована відповідь:", speaker.get_personalized_response('greeting'))
    
    try:
        asyncio.run(test_speaker())
    except KeyboardInterrupt:
        print("\nВихід з програми")
        sys.exit()
