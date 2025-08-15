#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для віддаленого керування JARVIS
"""

import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import subprocess
import psutil
from PIL import ImageGrab
import io

class JarvisTelegramBot:
    def __init__(self, token, authorized_users=None):
        self.token = token
        self.authorized_users = authorized_users or []
        self.app = None
        self.jarvis_instance = None
        
    def set_jarvis_instance(self, jarvis):
        """Встановлення посилання на основний JARVIS"""
        self.jarvis_instance = jarvis
    
    def is_authorized(self, user_id):
        """Перевірка авторизації користувача"""
        return not self.authorized_users or user_id in self.authorized_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Доступ заборонено. Ви не авторизовані для керування JARVIS.")
            return
        
        keyboard = [
            [InlineKeyboardButton("🎤 Статус JARVIS", callback_data="status")],
            [InlineKeyboardButton("📱 Системна інформація", callback_data="system_info")],
            [InlineKeyboardButton("📸 Скріншот", callback_data="screenshot")],
            [InlineKeyboardButton("📋 Команди", callback_data="commands")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 Вітаю! Я JARVIS Telegram Bot.\n"
            "Через мене ви можете керувати JARVIS на вашому комп'ютері.\n\n"
            "Оберіть дію:",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка натискань кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not self.is_authorized(user_id):
            await query.edit_message_text("❌ Доступ заборонено.")
            return
        
        if query.data == "status":
            status = "🟢 Активний" if self.jarvis_instance and self.jarvis_instance.is_active else "🔴 Неактивний"
            await query.edit_message_text(f"📊 Статус JARVIS: {status}")
            
        elif query.data == "system_info":
            info = await self.get_system_info()
            await query.edit_message_text(f"💻 Системна інформація:\n\n{info}")
            
        elif query.data == "screenshot":
            await self.send_screenshot(query)
            
        elif query.data == "commands":
            commands_text = """
📋 Доступні команди:

🎤 Голосові команди:
• Надішліть текст - JARVIS виконає як голосову команду

💻 Системні команди:
• /screenshot - зробити скріншот
• /status - статус системи
• /apps - список запущених програм
• /weather - погода

🔧 Керування:
• /start_jarvis - запустити JARVIS
• /stop_jarvis - зупинити JARVIS
            """
            await query.edit_message_text(commands_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка текстових повідомлень як команд"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Доступ заборонено.")
            return
        
        message_text = update.message.text
        
        # Виконання команди через JARVIS
        if self.jarvis_instance:
            try:
                await update.message.reply_text("🔄 Виконую команду...")
                
                # Симуляція виконання команди
                response = await self.jarvis_instance.execute_command(message_text)
                
                await update.message.reply_text(f"🤖 JARVIS: {response}")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Помилка виконання: {str(e)}")
        else:
            await update.message.reply_text("❌ JARVIS недоступний.")
    
    async def screenshot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /screenshot"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Доступ заборонено.")
            return
        
        await self.send_screenshot(update)
    
    async def send_screenshot(self, update_or_query):
        """Надсилання скріншота"""
        try:
            # Створення скріншота
            screenshot = ImageGrab.grab()
            
            # Зменшення розміру для Telegram
            screenshot.thumbnail((1280, 720), Image.Resampling.LANCZOS)
            
            # Збереження в пам'ять
            bio = io.BytesIO()
            screenshot.save(bio, format='PNG')
            bio.seek(0)
            
            if hasattr(update_or_query, 'message'):
                # Це Update з команди
                await update_or_query.message.reply_photo(
                    photo=bio,
                    caption="📸 Скріншот екрану"
                )
            else:
                # Це CallbackQuery з кнопки
                await update_or_query.message.reply_photo(
                    photo=bio,
                    caption="📸 Скріншот екрану"
                )
                
        except Exception as e:
            error_msg = f"❌ Помилка створення скріншота: {str(e)}"
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text(error_msg)
            else:
                await update_or_query.edit_message_text(error_msg)
    
    async def get_system_info(self):
        """Отримання системної інформації"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = f"""
🖥️ CPU: {cpu_percent}%
🧠 RAM: {memory.percent}% ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)
💾 Диск: {disk.percent}% ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)
            """
            return info.strip()
            
        except Exception as e:
            return f"Помилка отримання інформації: {str(e)}"
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /weather"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Доступ заборонено.")
            return
        
        try:
            from plugins.weather import get_weather
            weather_info = await get_weather()
            await update.message.reply_text(f"🌤️ {weather_info}")
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка отримання погоди: {str(e)}")
    
    async def apps_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /apps - список запущених програм"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Доступ заборонено.")
            return
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 0:
                        processes.append(f"• {proc.info['name']} (CPU: {proc.info['cpu_percent']:.1f}%)")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if processes:
                apps_text = "🖥️ Активні програми:\n\n" + "\n".join(processes[:10])
            else:
                apps_text = "Активних програм не знайдено."
                
            await update.message.reply_text(apps_text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")
    
    def setup_handlers(self):
        """Налаштування обробників команд"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("screenshot", self.screenshot_command))
        self.app.add_handler(CommandHandler("weather", self.weather_command))
        self.app.add_handler(CommandHandler("apps", self.apps_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_bot(self):
        """Запуск бота"""
        try:
            self.app = Application.builder().token(self.token).build()
            self.setup_handlers()
            
            logging.info("Telegram бот запускається...")
            await self.app.run_polling()
            
        except Exception as e:
            logging.error(f"Помилка запуску Telegram бота: {e}")

# Функція для запуску бота в окремому потоці
async def start_telegram_bot(token, authorized_users=None, jarvis_instance=None):
    """Запуск Telegram бота"""
    bot = JarvisTelegramBot(token, authorized_users)
    if jarvis_instance:
        bot.set_jarvis_instance(jarvis_instance)
    
    await bot.start_bot()

# Тестування
if __name__ == "__main__":
    # Замініть на ваш токен бота
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    AUTHORIZED_USERS = [123456789]  # ID авторизованих користувачів
    
    asyncio.run(start_telegram_bot(BOT_TOKEN, AUTHORIZED_USERS))
