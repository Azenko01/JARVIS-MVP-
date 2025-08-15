#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плагін візуального аналізу екрану для JARVIS
"""

import asyncio
import logging
import base64
from io import BytesIO
from PIL import Image, ImageGrab
import pytesseract
import cv2
import numpy as np

class VisualAssistant:
    def __init__(self):
        # Налаштування OCR
        try:
            # Встановіть шлях до tesseract, якщо потрібно
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pass
        except Exception as e:
            logging.warning(f"Tesseract не налаштований: {e}")
    
    async def analyze_screen(self):
        """
        Аналіз поточного екрану
        
        Returns:
            str: Опис того, що бачить на екрані
        """
        try:
            # Скріншот екрану
            screenshot = ImageGrab.grab()
            
            # Аналіз скріншота
            analysis_results = []
            
            # OCR - розпізнавання тексту
            text_content = await self._extract_text(screenshot)
            if text_content:
                analysis_results.append(f"Текст на екрані: {text_content[:200]}...")
            
            # Визначення активного вікна
            window_info = await self._get_active_window_info()
            if window_info:
                analysis_results.append(f"Активне вікно: {window_info}")
            
            # Аналіз кольорів та елементів
            visual_analysis = await self._analyze_visual_elements(screenshot)
            if visual_analysis:
                analysis_results.append(visual_analysis)
            
            if analysis_results:
                return "\n".join(analysis_results)
            else:
                return "Бачу екран, але не можу детально проаналізувати вміст."
                
        except Exception as e:
            logging.error(f"Помилка аналізу екрану: {e}")
            return "Помилка при аналізі екрану."
    
    async def _extract_text(self, image):
        """Витягування тексту з зображення"""
        try:
            # Конвертація в формат для OCR
            text = pytesseract.image_to_string(image, lang='ukr+eng')
            
            # Очищення тексту
            cleaned_text = ' '.join(text.split())
            
            return cleaned_text if len(cleaned_text) > 10 else None
            
        except Exception as e:
            logging.error(f"Помилка OCR: {e}")
            return None
    
    async def _get_active_window_info(self):
        """Отримання інформації про активне вікно"""
        try:
            import win32gui
            
            # Отримання активного вікна
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            if window_title:
                return window_title
            else:
                return "Невідоме вікно"
                
        except ImportError:
            logging.warning("pywin32 не встановлений")
            return None
        except Exception as e:
            logging.error(f"Помилка отримання інформації про вікно: {e}")
            return None
    
    async def _analyze_visual_elements(self, image):
        """Аналіз візуальних елементів"""
        try:
            # Конвертація в numpy array
            img_array = np.array(image)
            
            # Аналіз кольорів
            dominant_colors = await self._get_dominant_colors(img_array)
            
            # Пошук кнопок та елементів інтерфейсу
            ui_elements = await self._detect_ui_elements(img_array)
            
            analysis = []
            if dominant_colors:
                analysis.append(f"Домінуючі кольори: {dominant_colors}")
            
            if ui_elements:
                analysis.append(f"Елементи інтерфейсу: {ui_elements}")
            
            return "; ".join(analysis) if analysis else None
            
        except Exception as e:
            logging.error(f"Помилка візуального аналізу: {e}")
            return None
    
    async def _get_dominant_colors(self, img_array):
        """Визначення домінуючих кольорів"""
        try:
            # Зменшення розміру для швидкості
            small_img = cv2.resize(img_array, (100, 100))
            
            # Конвертація в RGB
            rgb_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
            
            # Обчислення середнього кольору
            avg_color = np.mean(rgb_img, axis=(0, 1))
            
            # Визначення назви кольору (спрощено)
            r, g, b = avg_color
            if r > 200 and g > 200 and b > 200:
                return "світлі тони"
            elif r < 50 and g < 50 and b < 50:
                return "темні тони"
            elif r > g and r > b:
                return "червонуваті тони"
            elif g > r and g > b:
                return "зеленуваті тони"
            elif b > r and b > g:
                return "синюваті тони"
            else:
                return "змішані кольори"
                
        except Exception as e:
            logging.error(f"Помилка аналізу кольорів: {e}")
            return None
    
    async def _detect_ui_elements(self, img_array):
        """Виявлення елементів інтерфейсу"""
        try:
            # Конвертація в сірий
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # Пошук прямокутників (кнопки, вікна)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Підрахунок елементів
            rectangles = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Фільтр малих елементів
                    rectangles += 1
            
            if rectangles > 10:
                return "багато елементів інтерфейсу"
            elif rectangles > 5:
                return "кілька елементів інтерфейсу"
            elif rectangles > 0:
                return "мало елементів інтерфейсу"
            else:
                return "мінімальний інтерфейс"
                
        except Exception as e:
            logging.error(f"Помилка виявлення UI елементів: {e}")
            return None
    
    async def take_screenshot(self, filename=None):
        """Створення скріншота"""
        try:
            screenshot = ImageGrab.grab()
            
            if filename:
                screenshot.save(filename)
                return f"Скріншот збережено як {filename}"
            else:
                # Збереження з автоматичною назвою
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                screenshot.save(filename)
                return f"Скріншот збережено як {filename}"
                
        except Exception as e:
            logging.error(f"Помилка створення скріншота: {e}")
            return "Помилка при створенні скріншота."
    
    async def analyze_code_on_screen(self):
        """Спеціальний аналіз коду на екрані"""
        try:
            screenshot = ImageGrab.grab()
            text = pytesseract.image_to_string(screenshot, lang='eng')
            
            # Пошук ключових слів програмування
            code_keywords = [
                'def ', 'class ', 'import ', 'function', 'var ', 'let ', 'const ',
                'if ', 'else', 'for ', 'while ', 'return', 'print', 'console.log'
            ]
            
            found_keywords = [kw for kw in code_keywords if kw in text.lower()]
            
            if found_keywords:
                suggestions = []
                
                if 'def ' in text.lower():
                    suggestions.append("Бачу Python функції. Рекомендую додати docstring.")
                
                if 'class ' in text.lower():
                    suggestions.append("Бачу класи. Перевірте наявність __init__ методу.")
                
                if 'import ' in text.lower():
                    suggestions.append("Бачу імпорти. Рекомендую групувати їх на початку файлу.")
                
                if suggestions:
                    return "Аналіз коду:\n" + "\n".join(suggestions)
                else:
                    return f"Бачу код з ключовими словами: {', '.join(found_keywords)}"
            else:
                return "Не виявлено коду на екрані або код не розпізнається."
                
        except Exception as e:
            logging.error(f"Помилка аналізу коду: {e}")
            return "Помилка при аналізі коду на екрані."

# Глобальний екземпляр
visual_assistant = VisualAssistant()

async def analyze_screen():
    """Функція для використання в main.py"""
    return await visual_assistant.analyze_screen()

async def take_screenshot(filename=None):
    """Створення скріншота"""
    return await visual_assistant.take_screenshot(filename)

async def analyze_code():
    """Аналіз коду на екрані"""
    return await visual_assistant.analyze_code_on_screen()

# Тестування
if __name__ == "__main__":
    async def test_visual():
        print("Аналізую екран...")
        result = await analyze_screen()
        print(result)
        
        print("\nСтворюю скріншот...")
        screenshot_result = await take_screenshot()
        print(screenshot_result)
    
    asyncio.run(test_visual())
