#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль голосового розпізнавання для JARVIS
"""

import speech_recognition as sr
import asyncio
import logging
from config import Config

class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.config = Config()
        
        # Налаштування розпізнавача
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Вибір мікрофона
        self._setup_microphone()
        
        # Калібрування мікрофона
        self._calibrate_microphone()
        
        logging.info("VoiceListener ініціалізовано")
    
    def _setup_microphone(self):
        """Налаштування мікрофона"""
        try:
            # Показати доступні мікрофони
            mic_list = sr.Microphone.list_microphone_names()
            logging.info(f"Доступні мікрофони: {len(mic_list)}")
            
            for i, name in enumerate(mic_list):
                logging.info(f"[{i}] {name}")
            
            # Використовувати мікрофон за замовчуванням
            self.microphone_index = getattr(self.config, 'MICROPHONE_INDEX', None)
            
        except Exception as e:
            logging.error(f"Помилка налаштування мікрофона: {e}")
            self.microphone_index = None
    
    def _calibrate_microphone(self):
        """Калібрування мікрофона для зменшення шуму"""
        try:
            with sr.Microphone(device_index=self.microphone_index) as source:
                print("Калібрування мікрофона... Будьте тихо.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Калібрування завершено.")
                logging.info("Мікрофон відкалібровано")
        except Exception as e:
            logging.error(f"Помилка калібрування мікрофона: {e}")
    
    async def listen(self, timeout=None):
        """
        Асинхронне прослуховування голосової команди
        
        Args:
            timeout: Максимальний час очікування (секунди)
            
        Returns:
            str: Розпізнаний текст або None
        """
        try:
            # Запуск в окремому потоці для асинхронності
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self._listen_sync, timeout)
            return text
            
        except Exception as e:
            logging.error(f"Помилка при прослуховуванні: {e}")
            return None
    
    def _listen_sync(self, timeout=None):
        """Синхронне прослуховування"""
        try:
            with sr.Microphone(device_index=self.microphone_index) as source:
                print("Слухаю...")
                logging.info("Розпочато прослуховування")
                
                # Запис аудіо
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout or self.config.SPEECH_TIMEOUT,
                    phrase_time_limit=self.config.SPEECH_PHRASE_TIMEOUT
                )
                
                print("Розпізнаю мовлення...")
                logging.info("Розпочато розпізнавання мовлення")
                
                # Спроба розпізнавання українською
                try:
                    text = self.recognizer.recognize_google(
                        audio, 
                        language=self.config.SPEECH_LANGUAGE
                    )
                    print(f"Розпізнано (UA): {text}")
                    logging.info(f"Успішно розпізнано українською: {text}")
                    return text
                    
                except sr.UnknownValueError:
                    # Спроба розпізнавання англійською
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        print(f"Розпізнано (EN): {text}")
                        logging.info(f"Успішно розпізнано англійською: {text}")
                        return text
                    except sr.UnknownValueError:
                        print("Не вдалося розпізнати мовлення")
                        logging.warning("Мовлення не розпізнано")
                        return None
                        
        except sr.WaitTimeoutError:
            print("Таймаут очікування")
            logging.info("Таймаут прослуховування")
            return None
        except sr.RequestError as e:
            logging.error(f"Помилка сервісу розпізнавання: {e}")
            print(f"Помилка сервісу: {e}")
            return None
        except Exception as e:
            logging.error(f"Неочікувана помилка при розпізнаванні: {e}")
            print(f"Помилка: {e}")
            return None
    
    async def listen_for_activation(self):
        """
        Спеціальне прослуховування для активаційної фрази
        Менш чутливе, щоб не реагувати на фоновий шум
        """
        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self._listen_for_activation_sync)
            return text
        except Exception as e:
            logging.error(f"Помилка при прослуховуванні активації: {e}")
            return None

    def _listen_for_activation_sync(self):
        """Синхронне прослуховування активації"""
        try:
            with sr.Microphone(device_index=self.microphone_index) as source:
                # Більш тривале очікування для активації
                audio = self.recognizer.listen(
                    source, 
                    timeout=1,  # Коротший таймаут
                    phrase_time_limit=3  # Довша фраза
                )
                
                # Розпізнавання тільки українською для активації
                try:
                    text = self.recognizer.recognize_google(audio, language="uk-UA")
                    logging.info(f"Активаційна фраза: {text}")
                    return text
                except sr.UnknownValueError:
                    return None
                    
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            logging.error(f"Помилка активації: {e}")
            return None
    
    def is_listening_available(self):
        """Перевірка доступності мікрофона"""
        try:
            with sr.Microphone(device_index=self.microphone_index) as source:
                pass
            return True
        except Exception as e:
            logging.error(f"Мікрофон недоступний: {e}")
            return False
    
    def get_microphone_info(self):
        """Отримання інформації про мікрофон"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return {
                "available_microphones": mic_list,
                "current_device_index": self.microphone_index,
                "total_devices": len(mic_list)
            }
        except Exception as e:
            logging.error(f"Помилка отримання інформації про мікрофон: {e}")
            return None

# Тестування модуля
if __name__ == "__main__":
    import sys
    
    async def test_listener():
        listener = VoiceListener()
        print("Тестування голосового розпізнавання...")
        
        # Показати інформацію про мікрофони
        mic_info = listener.get_microphone_info()
        if mic_info:
            print(f"Знайдено {mic_info['total_devices']} мікрофонів")
            print(f"Використовується індекс: {mic_info['current_device_index']}")
        
        # Перевірка доступності
        if not listener.is_listening_available():
            print("ПОМИЛКА: Мікрофон недоступний!")
            return
        
        print("Мікрофон готовий. Говоріть...")
        
        while True:
            text = await listener.listen()
            if text:
                print(f"Розпізнано: {text}")
                if "стоп" in text.lower() or "stop" in text.lower():
                    break
            else:
                print("Нічого не розпізнано")
    
    try:
        asyncio.run(test_listener())
    except KeyboardInterrupt:
        print("\nВихід з програми")
        sys.exit()
