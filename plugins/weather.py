#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плагін погоди для JARVIS
"""

import aiohttp
import asyncio
import logging
from config import Config

class WeatherPlugin:
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    async def get_weather(self, city=None):
        """
        Отримання поточної погоди
        
        Args:
            city (str): Назва міста
            
        Returns:
            str: Опис погоди
        """
        if not self.api_key:
            return "Для роботи з погодою потрібно налаштувати API ключ OpenWeatherMap."
        
        city = city or self.config.DEFAULT_CITY
        
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.config.WEATHER_UNITS,
                'lang': 'uk'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_weather_response(data)
                    else:
                        return f"Не вдалося отримати погоду для міста {city}."
                        
        except Exception as e:
            logging.error(f"Помилка отримання погоди: {e}")
            return "Виникла помилка при отриманні інформації про погоду."
    
    def _format_weather_response(self, data):
        """Форматування відповіді про погоду"""
        try:
            city = data['name']
            country = data['sys']['country']
            temp = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            
            response = f"Погода в місті {city}, {country}:\n"
            response += f"Температура: {temp}°C (відчувається як {feels_like}°C)\n"
            response += f"Опис: {description}\n"
            response += f"Вологість: {humidity}%"
            
            return response
            
        except KeyError as e:
            logging.error(f"Помилка парсингу даних погоди: {e}")
            return "Помилка обробки даних про погоду."

# Глобальний екземпляр плагіна
weather_plugin = WeatherPlugin()

async def get_weather(city=None):
    """Функція для використання в main.py"""
    return await weather_plugin.get_weather(city)

# Тестування
if __name__ == "__main__":
    async def test_weather():
        result = await get_weather("Київ")
        print(result)
    
    asyncio.run(test_weather())
