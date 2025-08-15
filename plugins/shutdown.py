#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плагін керування системою для JARVIS
"""

import subprocess
import asyncio
import logging
from config import Config

class SystemControlPlugin:
    def __init__(self):
        self.config = Config()
        self.pending_shutdown = False
        self.pending_restart = False
    
    async def handle_shutdown_command(self, command_text):
        """
        Обробка команд вимкнення/перезавантаження
        
        Args:
            command_text (str): Текст команди
            
        Returns:
            str: Відповідь системи
        """
        command_lower = command_text.lower()
        
        # Перевірка на небезпечні команди
        if self.config.is_dangerous_command(command_text):
            return "Ця команда заблокована з міркувань безпеки."
        
        if any(word in command_lower for word in ['вимкни комп', 'shutdown', 'вимкни систему']):
            return await self._handle_shutdown()
        
        elif any(word in command_lower for word in ['перезавантаж', 'restart', 'reboot']):
            return await self._handle_restart()
        
        elif any(word in command_lower for word in ['сплячий режим', 'sleep', 'hibernate']):
            return await self._handle_sleep()
        
        elif 'перезапусти процесор' in command_lower:
            return await self._handle_cpu_restart()
        
        else:
            return "Не розпізнав команду керування системою."
    
    async def _handle_shutdown(self):
        """Обробка команди вимкнення"""
        if not self.pending_shutdown:
            self.pending_shutdown = True
            return ("Ви впевнені, що хочете вимкнути комп'ютер? "
                   "Скажіть 'так, вимкни' для підтвердження або 'скасувати' для відміни.")
        else:
            # Виконання вимкнення
            try:
                subprocess.run(['shutdown', '/s', '/t', '10'], check=True)
                return "Вимикаю комп'ютер через 10 секунд. До побачення!"
            except subprocess.CalledProcessError as e:
                logging.error(f"Помилка вимкнення: {e}")
                return "Помилка при вимкненні системи."
            finally:
                self.pending_shutdown = False
    
    async def _handle_restart(self):
        """Обробка команди перезавантаження"""
        if not self.pending_restart:
            self.pending_restart = True
            return ("Ви впевнені, що хочете перезавантажити комп'ютер? "
                   "Скажіть 'так, перезавантаж' для підтвердження або 'скасувати' для відміни.")
        else:
            # Виконання перезавантаження
            try:
                subprocess.run(['shutdown', '/r', '/t', '10'], check=True)
                return "Перезавантажую комп'ютер через 10 секунд."
            except subprocess.CalledProcessError as e:
                logging.error(f"Помилка перезавантаження: {e}")
                return "Помилка при перезавантаженні системи."
            finally:
                self.pending_restart = False
    
    async def _handle_sleep(self):
        """Обробка команди сплячого режиму"""
        try:
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            return "Переводжу комп'ютер в сплячий режим."
        except subprocess.CalledProcessError as e:
            logging.error(f"Помилка сплячого режиму: {e}")
            return "Помилка при переході в сплячий режим."
    
    async def _handle_cpu_restart(self):
        """Псевдокоманда перезапуску процесора (безпечна відповідь)"""
        return ("Процесор не можна перезапустити окремо від системи. "
               "Можливо, ви мали на увазі перезавантаження комп'ютера?")
    
    async def cancel_pending_operations(self):
        """Скасування очікуючих операцій"""
        if self.pending_shutdown or self.pending_restart:
            self.pending_shutdown = False
            self.pending_restart = False
            
            # Скасування запланованого вимкнення
            try:
                subprocess.run(['shutdown', '/a'], check=True)
                return "Операцію скасовано."
            except subprocess.CalledProcessError:
                return "Операцію скасовано."
        else:
            return "Немає операцій для скасування."
    
    async def get_system_info(self):
        """Отримання інформації про систему"""
        try:
            import platform
            import psutil
            
            info = []
            info.append(f"Система: {platform.system()} {platform.release()}")
            info.append(f"Процесор: {platform.processor()}")
            info.append(f"Використання CPU: {psutil.cpu_percent()}%")
            info.append(f"Використання RAM: {psutil.virtual_memory().percent}%")
            
            return "\n".join(info)
            
        except Exception as e:
            logging.error(f"Помилка отримання інформації про систему: {e}")
            return "Не вдалося отримати інформацію про систему."
    
    async def lock_computer(self):
        """Блокування комп'ютера"""
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            return "Блокую комп'ютер."
        except subprocess.CalledProcessError as e:
            logging.error(f"Помилка блокування: {e}")
            return "Помилка при блокуванні комп'ютера."

# Глобальний екземпляр
system_control = SystemControlPlugin()

async def handle_shutdown_command(command_text):
    """Функція для використання в main.py"""
    return await system_control.handle_shutdown_command(command_text)

async def cancel_operations():
    """Скасування операцій"""
    return await system_control.cancel_pending_operations()

async def get_system_info():
    """Інформація про систему"""
    return await system_control.get_system_info()

async def lock_computer():
    """Блокування комп'ютера"""
    return await system_control.lock_computer()

# Тестування
if __name__ == "__main__":
    async def test_system():
        print(await handle_shutdown_command("вимкни комп'ютер"))
        print(await cancel_operations())
        print(await get_system_info())
    
    asyncio.run(test_system())
