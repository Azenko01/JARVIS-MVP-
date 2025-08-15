#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плагін веб-пошуку для JARVIS
"""

import aiohttp
import asyncio
import logging
import subprocess
import urllib.parse
from bs4 import BeautifulSoup

class WebSearchPlugin:
    def __init__(self):
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}',
            'youtube': 'https://www.youtube.com/results?search_query={}'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search(self, query, engine='google', open_browser=True):
        """
        Веб-пошук
        
        Args:
            query (str): Пошуковий запит
            engine (str): Пошукова система
            open_browser (bool): Відкрити в браузері
            
        Returns:
            str: Результат пошуку
        """
        try:
            # Очищення запиту від команд
            clean_query = self._extract_search_query(query)
            
            if not clean_query:
                return "Не зрозуміла, що шукати."
            
            # Кодування запиту для URL
            encoded_query = urllib.parse.quote_plus(clean_query)
            
            # Формування URL
            if engine in self.search_engines:
                search_url = self.search_engines[engine].format(encoded_query)
            else:
                search_url = self.search_engines['google'].format(encoded_query)
            
            # Відкриття в браузері
            if open_browser:
                subprocess.run(['start', search_url], shell=True)
                return f"Шукаю '{clean_query}' в {engine.title()}."
            
            # Отримання результатів (без відкриття браузера)
            results = await self._get_search_results(search_url)
            return f"Результати пошуку '{clean_query}':\n{results}"
            
        except Exception as e:
            logging.error(f"Помилка веб-пошуку: {e}")
            return f"Помилка при пошуку '{query}'."
    
    def _extract_search_query(self, command_text):
        """Витягування пошукового запиту з команди"""
        import re
        
        patterns = [
            r'пошукай (.+)',
            r'знайди (.+)',
            r'шукай (.+)',
            r'search (.+)',
            r'find (.+)',
            r'look for (.+)',
            r'google (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return command_text.strip()
    
    async def _get_search_results(self, url):
        """Отримання результатів пошуку (спрощена версія)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Пошук результатів (спрощено для Google)
                        results = []
                        for result in soup.find_all('h3')[:3]:  # Перші 3 результати
                            if result.text:
                                results.append(result.text)
                        
                        if results:
                            return '\n'.join(f"• {result}" for result in results)
                        else:
                            return "Результати знайдено, але не вдалося їх обробити."
                    else:
                        return "Не вдалося отримати результати пошуку."
                        
        except Exception as e:
            logging.error(f"Помилка отримання результатів: {e}")
            return "Помилка при отриманні результатів."
    
    async def search_youtube(self, query):
        """Пошук на YouTube"""
        return await self.search(query, engine='youtube')
    
    async def search_images(self, query):
        """Пошук зображень"""
        clean_query = self._extract_search_query(query)
        encoded_query = urllib.parse.quote_plus(clean_query)
        
        image_search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
        subprocess.run(['start', image_search_url], shell=True)
        
        return f"Шукаю зображення '{clean_query}' в Google Images."
    
    async def search_news(self, query):
        """Пошук новин"""
        clean_query = self._extract_search_query(query)
        encoded_query = urllib.parse.quote_plus(clean_query)
        
        news_search_url = f"https://www.google.com/search?q={encoded_query}&tbm=nws"
        subprocess.run(['start', news_search_url], shell=True)
        
        return f"Шукаю новини про '{clean_query}' в Google News."
    
    async def search_maps(self, location):
        """Пошук на картах"""
        clean_location = self._extract_search_query(location)
        encoded_location = urllib.parse.quote_plus(clean_location)
        
        maps_url = f"https://www.google.com/maps/search/{encoded_location}"
        subprocess.run(['start', maps_url], shell=True)
        
        return f"Показую '{clean_location}' на Google Maps."

# Глобальний екземпляр
web_search = WebSearchPlugin()

async def search(query, engine='google'):
    """Функція для використання в main.py"""
    return await web_search.search(query, engine)

async def search_youtube(query):
    """Пошук на YouTube"""
    return await web_search.search_youtube(query)

async def search_images(query):
    """Пошук зображень"""
    return await web_search.search_images(query)

async def search_news(query):
    """Пошук новин"""
    return await web_search.search_news(query)

async def search_maps(location):
    """Пошук на картах"""
    return await web_search.search_maps(location)

# Тестування
if __name__ == "__main__":
    async def test_search():
        result = await search("пошукай рецепт борщу")
        print(result)
        
        result = await search_youtube("навчання Python")
        print(result)
    
    asyncio.run(test_search())
