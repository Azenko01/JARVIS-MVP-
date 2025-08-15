#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Діагностика голосової системи JARVIS
"""

import asyncio
import speech_recognition as sr
import sys
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)

async def test_microphone():
    """Тестування мікрофона"""
    print("=== ТЕСТУВАННЯ МІКРОФОНА ===")
    
    try:
        # Показати всі доступні мікрофони
        mic_list = sr.Microphone.list_microphone_names()
        print(f"Знайдено {len(mic_list)} мікрофонів:")
        
        for i, name in enumerate(mic_list):
            print(f"  [{i}] {name}")
        
        # Тестування кожного мікрофона
        recognizer = sr.Recognizer()
        
        for i in range(min(3, len(mic_list))):  # Тестуємо перші 3
            print(f"\nТестування мікрофона [{i}]: {mic_list[i]}")
            
            try:
                with sr.Microphone(device_index=i) as source:
                    print("Калібрування...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    print("Скажіть щось (5 секунд)...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    
                    print("Розпізнаю...")
                    text = recognizer.recognize_google(audio, language="uk-UA")
                    print(f"✅ Розпізнано: {text}")
                    
                    return i  # Повертаємо індекс робочого мікрофона
                    
            except sr.WaitTimeoutError:
                print("❌ Таймаут - нічого не сказано")
            except sr.UnknownValueError:
                print("❌ Не вдалося розпізнати")
            except Exception as e:
                print(f"❌ Помилка: {e}")
        
        return None
        
    except Exception as e:
        print(f"Критична помилка мікрофона: {e}")
        return None

async def test_speaker():
    """Тестування динаміків"""
    print("\n=== ТЕСТУВАННЯ ДИНАМІКІВ ===")
    
    try:
        from voice.speaker import VoiceSpeaker
        
        speaker = VoiceSpeaker()
        
        # Показати доступні голоси
        voices = speaker.get_available_voices()
        print(f"Доступно {len(voices)} голосів:")
        
        for voice in voices[:3]:  # Показати перші 3
            print(f"  - {voice['name']} ({voice.get('gender', 'Unknown')})")
        
        # Тестування голосу
        print("\nТестування голосу...")
        await speaker.speak("Тест голосової системи JARVIS")
        
        return True
        
    except Exception as e:
        print(f"Помилка динаміків: {e}")
        return False

async def test_activation():
    """Тестування активаційних фраз"""
    print("\n=== ТЕСТУВАННЯ АКТИВАЦІЇ ===")
    
    try:
        from voice.listener import VoiceListener
        
        listener = VoiceListener()
        
        print("Скажіть активаційну фразу: 'Привіт, Джарвіс'")
        
        for attempt in range(3):
            print(f"Спроба {attempt + 1}/3...")
            
            text = await listener.listen_for_activation()
            
            if text:
                print(f"Почув: {text}")
                
                # Перевірка активаційних фраз
                text_lower = text.lower()
                activation_phrases = ["привіт джарвіс", "джарвіс", "jarvis"]
                
                if any(phrase in text_lower for phrase in activation_phrases):
                    print("✅ Активаційна фраза розпізнана!")
                    return True
                else:
                    print("❌ Це не активаційна фраза")
            else:
                print("❌ Нічого не почув")
        
        return False
        
    except Exception as e:
        print(f"Помилка активації: {e}")
        return False

async def full_voice_test():
    """Повний тест голосової системи"""
    print("🎤 ДІАГНОСТИКА ГОЛОСОВОЇ СИСТЕМИ JARVIS")
    print("=" * 50)
    
    # Тест мікрофона
    working_mic = await test_microphone()
    
    if working_mic is None:
        print("\n❌ КРИТИЧНА ПОМИЛКА: Мікрофон не працює!")
        print("Рекомендації:")
        print("1. Перевірте підключення мікрофона")
        print("2. Надайте дозвіл на використання мікрофона")
        print("3. Закрийте інші програми, що можуть використовувати мікрофон")
        return False
    
    print(f"\n✅ Робочий мікрофон знайдено: індекс {working_mic}")
    
    # Тест динаміків
    speaker_ok = await test_speaker()
    
    if not speaker_ok:
        print("\n❌ ПОМИЛКА: Динаміки не працюють!")
        return False
    
    print("\n✅ Динаміки працюють")
    
    # Тест активації
    activation_ok = await test_activation()
    
    if not activation_ok:
        print("\n❌ ПОМИЛКА: Активація не працює!")
        print("Рекомендації:")
        print("1. Говоріть чітко та голосно")
        print("2. Зменшіть фоновий шум")
        print("3. Спробуйте сказати 'Привіт, Джарвіс' або 'Джарвіс'")
        return False
    
    print("\n🎉 ВСЕ ПРАЦЮЄ! Голосова система готова до роботи.")
    
    # Збереження налаштувань
    print(f"\n💾 Рекомендовано використовувати мікрофон з індексом: {working_mic}")
    print("Додайте в config.py:")
    print(f"MICROPHONE_INDEX = {working_mic}")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(full_voice_test())
        
        if result:
            print("\n✅ Тепер можете запускати JARVIS!")
        else:
            print("\n❌ Виправте помилки перед запуском JARVIS")
            
    except KeyboardInterrupt:
        print("\n👋 Тестування перервано")
    except Exception as e:
        print(f"\n💥 Критична помилка: {e}")
