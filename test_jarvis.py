#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестування основних компонентів JARVIS
"""

import asyncio
import sys
from pathlib import Path

def test_imports():
    """Тестування імпортів"""
    print("Тестування імпортів...")
    
    try:
        from config import Config
        print("Config - OK")
    except Exception as e:
        print(f"Config - ПОМИЛКА: {e}")
        return False
    
    try:
        from voice.speaker import VoiceSpeaker
        print("VoiceSpeaker - OK")
    except Exception as e:
        print(f"VoiceSpeaker - ПОМИЛКА: {e}")
    
    try:
        from voice.listener import VoiceListener
        print("VoiceListener - OK")
    except Exception as e:
        print(f"VoiceListener - ПОМИЛКА: {e}")
    
    try:
        from memory.learner import JarvisLearner
        print("JarvisLearner - OK")
    except Exception as e:
        print(f"JarvisLearner - ПОМИЛКА: {e}")
    
    return True

async def test_voice():
    """Тестування голосового синтезу"""
    print("\nТестування голосу...")
    
    try:
        from voice.speaker import VoiceSpeaker
        speaker = VoiceSpeaker()
        await speaker.speak("Тестування голосу JARVIS")
        print("Голосовий синтез - OK")
        return True
    except Exception as e:
        print(f"Голосовий синтез - ПОМИЛКА: {e}")
        return False

def test_config():
    """Тестування конфігурації"""
    print("\nТестування конфігурації...")
    
    try:
        from config import Config
        config = Config()
        
        print(f"Версія: {config.VERSION}")
        print(f"Автор: {config.AUTHOR}")
        print(f"База даних: {config.DATABASE_PATH}")
        
        # Перевірка API статусу
        api_status = config.get_api_status()
        print(f"OpenAI API: {'OK' if api_status['openai'] else 'НЕ НАЛАШТОВАНО'}")
        print(f"Weather API: {'OK' if api_status['weather'] else 'НЕ НАЛАШТОВАНО'}")
        print(f"Telegram Bot: {'OK' if api_status['telegram'] else 'НЕ НАЛАШТОВАНО'}")
        
        return True
    except Exception as e:
        print(f"Конфігурація - ПОМИЛКА: {e}")
        return False

async def main():
    """Головна функція тестування"""
    print("=" * 50)
    print("ТЕСТУВАННЯ JARVIS v2.0")
    print("=" * 50)
    
    # Тестування імпортів
    if not test_imports():
        print("КРИТИЧНА ПОМИЛКА: Не вдалося імпортувати основні модулі")
        return
    
    # Тестування конфігурації
    test_config()
    
    # Тестування голосу
    test_voice_choice = input("\nТестувати голосовий синтез? (y/n): ").lower().strip()
    if test_voice_choice == 'y':
        await test_voice()
    
    print("\n" + "=" * 50)
    print("ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
