#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плагін відкриття додатків для JARVIS
"""

import subprocess
import os
import asyncio
import logging
import psutil
from pathlib import Path

class AppOpener:
    def __init__(self):
        # Словник популярних додатків
        self.app_paths = {
            # Браузери
            'chrome': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ],
            'firefox': [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
            ],
            'edge': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
            ],
            
            # Редактори коду
            'vscode': [
                r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe'.format(os.getenv('USERNAME')),
                r'C:\Program Files\Microsoft VS Code\Code.exe'
            ],
            'notepad++': [
                r'C:\Program Files\Notepad++\notepad++.exe',
                r'C:\Program Files (x86)\Notepad++\notepad++.exe'
            ],
            
            # Системні додатки
            'calculator': ['calc.exe'],
            'notepad': ['notepad.exe'],
            'paint': ['mspaint.exe'],
            'cmd': ['cmd.exe'],
            'powershell': ['powershell.exe'],
            
            # Медіа
            'vlc': [
                r'C:\Program Files\VideoLAN\VLC\vlc.exe',
                r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'
            ],
            
            # Офісні програми
            'word': [
                r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
                r'C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE'
            ],
            'excel': [
                r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
                r'C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE'
            ],
            
            # Месенджери
            'telegram': [
                r'C:\Users\{}\AppData\Roaming\Telegram Desktop\Telegram.exe'.format(os.getenv('USERNAME'))
            ],
            'discord': [
                r'C:\Users\{}\AppData\Local\Discord\Update.exe'.format(os.getenv('USERNAME'))
            ]
        }
        
        # URL для веб-сервісів
        self.web_services = {
            'youtube': 'https://www.youtube.com',
            'gmail': 'https://mail.google.com',
            'google': 'https://www.google.com',
            'facebook': 'https://www.facebook.com',
            'instagram': 'https://www.instagram.com',
            'twitter': 'https://www.twitter.com',
            'github': 'https://www.github.com'
        }
    
    def _find_app_path(self, app_name):
        """Пошук шляху до додатка"""
        app_name_lower = app_name.lower()
        
        if app_name_lower in self.app_paths:
            for path in self.app_paths[app_name_lower]:
                if os.path.exists(path):
                    return path
        
        return None
    
    async def open_app(self, app_name):
        """
        Відкриття додатка
        
        Args:
            app_name (str): Назва додатка
            
        Returns:
            str: Результат виконання
        """
        try:
            app_name_clean = app_name.lower().strip()
            
            # Пошук в веб-сервісах
            if app_name_clean in self.web_services:
                url = self.web_services[app_name_clean]
                subprocess.run(['start', url], shell=True)
                return f"Відкриваю {app_name} в браузері."
            
            # Пошук локального додатка
            app_path = self._find_app_path(app_name_clean)
            if app_path:
                subprocess.Popen([app_path])
                return f"Запускаю {app_name}."
            
            # Спроба запуску як системної команди
            try:
                subprocess.run([app_name_clean], shell=True, check=True)
                return f"Запустив {app_name}."
            except subprocess.CalledProcessError:
                return f"Не вдалося знайти додаток {app_name}."
                
        except Exception as e:
            logging.error(f"Помилка відкриття додатка {app_name}: {e}")
            return f"Помилка при запуску {app_name}."
    
    async def close_app(self, app_name):
        """
        Закриття додатка
        
        Args:
            app_name (str): Назва додатка
            
        Returns:
            str: Результат виконання
        """
        try:
            app_name_lower = app_name.lower()
            closed_count = 0
            
            # Пошук процесів за назвою
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name_lower in proc_name or proc_name.startswith(app_name_lower):
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed_count > 0:
                return f"Закрив {closed_count} процес(ів) {app_name}."
            else:
                return f"Не знайшов запущених процесів {app_name}."
                
        except Exception as e:
            logging.error(f"Помилка закриття додатка {app_name}: {e}")
            return f"Помилка при закритті {app_name}."
    
    async def close_all_windows(self):
        """Закриття всіх вікон"""
        try:
            # Використання Alt+F4 для закриття активного вікна
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            return "Закриваю активне вікно."
        except Exception as e:
            logging.error(f"Помилка закриття вікон: {e}")
            return "Не вдалося закрити вікна."
    
    async def open_music(self):
        """Відкриття музичного додатка"""
        music_apps = ['spotify', 'vlc', 'windows media player']
        
        for app in music_apps:
            result = await self.open_app(app)
            if "Запускаю" in result:
                return result
        
        # Відкриття YouTube Music
        subprocess.run(['start', 'https://music.youtube.com'], shell=True)
        return "Відкриваю YouTube Music в браузері."

# Глобальний екземпляр
app_opener = AppOpener()

async def handle_open_command(command_text):
    """Обробка команди відкриття"""
    # Витягування назви додатка з команди
    import re
    
    patterns = [
        r'відкрий (.+)',
        r'запусти (.+)',
        r'зайди у (.+)',
        r'open (.+)',
        r'launch (.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command_text, re.IGNORECASE)
        if match:
            app_name = match.group(1).strip()
            return await app_opener.open_app(app_name)
    
    return "Не зрозуміла, який додаток відкрити."

async def handle_close_command(command_text):
    """Обробка команди закриття"""
    import re
    
    if "всі вікна" in command_text.lower() or "all windows" in command_text.lower():
        return await app_opener.close_all_windows()
    
    patterns = [
        r'закрий (.+)',
        r'вимкни (.+)',
        r'close (.+)',
        r'quit (.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command_text, re.IGNORECASE)
        if match:
            app_name = match.group(1).strip()
            return await app_opener.close_app(app_name)
    
    return "Не зрозуміла, що закрити."

async def open_music():
    """Відкриття музики"""
    return await app_opener.open_music()

# Тестування
if __name__ == "__main__":
    async def test_apps():
        print(await handle_open_command("відкрий chrome"))
        await asyncio.sleep(2)
        print(await handle_close_command("закрий chrome"))
    
    asyncio.run(test_apps())
