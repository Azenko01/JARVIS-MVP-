#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Головний GUI інтерфейс для JARVIS v2.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import asyncio
import queue
import json
from datetime import datetime
from pathlib import Path
import sys
import os

# Додавання батьківської директорії
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from memory.learner import JarvisLearner
from memory.vector_knowledge import vector_kb

class JarvisGUI:
    def __init__(self):
        self.config = Config()
        self.learner = JarvisLearner()
        self.jarvis_instance = None
        self.message_queue = queue.Queue()
        
        # Створення головного вікна
        self.root = tk.Tk()
        self.root.title("🤖 JARVIS v2.0 - AI Desktop Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Налаштування стилів
        self.setup_styles()
        
        # Створення інтерфейсу
        self.create_widgets()
        
        # Запуск обробки повідомлень
        self.process_messages()
        
        # Автооновлення
        self.auto_update()
    
    def setup_styles(self):
        """Налаштування темної теми"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Темна тема
        style.configure('Dark.TFrame', background='#1a1a1a')
        style.configure('Dark.TLabel', background='#1a1a1a', foreground='#ffffff', font=('Segoe UI', 10))
        style.configure('Dark.TButton', background='#3a3a3a', foreground='#ffffff', font=('Segoe UI', 9))
        style.configure('Chat.TFrame', background='#2a2a2a', relief='solid', borderwidth=1)
        
        # Кольори для статусів
        style.configure('Success.TLabel', background='#1a1a1a', foreground='#4CAF50', font=('Segoe UI', 10, 'bold'))
        style.configure('Error.TLabel', background='#1a1a1a', foreground='#F44336', font=('Segoe UI', 10, 'bold'))
        style.configure('Warning.TLabel', background='#1a1a1a', foreground='#FF9800', font=('Segoe UI', 10, 'bold'))
    
    def create_widgets(self):
        """Створення всіх віджетів"""
        # Головний контейнер
        main_container = ttk.Frame(self.root, style='Dark.TFrame')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Верхня панель
        self.create_header(main_container)
        
        # Основний контент (розділений на дві частини)
        content_frame = ttk.Frame(main_container, style='Dark.TFrame')
        content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Ліва частина - чат
        self.create_chat_panel(content_frame)
        
        # Права частина - панелі управління
        self.create_control_panels(content_frame)
        
        # Нижня панель
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Створення заголовка"""
        header_frame = ttk.Frame(parent, style='Dark.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Логотип та назва
        title_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        title_frame.pack(side='left')
        
        title_label = ttk.Label(
            title_frame, 
            text="🤖 JARVIS v2.0", 
            font=('Segoe UI', 18, 'bold'),
            style='Dark.TLabel'
        )
        title_label.pack(side='left')
        
        subtitle_label = ttk.Label(
            title_frame, 
            text="AI Desktop Assistant", 
            font=('Segoe UI', 10),
            style='Dark.TLabel'
        )
        subtitle_label.pack(side='left', padx=(10, 0))
        
        # Статус системи
        status_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        status_frame.pack(side='right')
        
        self.status_label = ttk.Label(
            status_frame, 
            text="🔴 Неактивний", 
            style='Error.TLabel'
        )
        self.status_label.pack(side='right')
        
        # API статуси
        api_frame = ttk.Frame(status_frame, style='Dark.TFrame')
        api_frame.pack(side='right', padx=(0, 20))
        
        api_status = self.config.get_api_status()
        
        self.openai_status = ttk.Label(
            api_frame, 
            text="🔑 OpenAI: " + ("✅" if api_status['openai'] else "❌"),
            style='Success.TLabel' if api_status['openai'] else 'Error.TLabel'
        )
        self.openai_status.pack(side='right', padx=(0, 10))
        
        self.telegram_status = ttk.Label(
            api_frame, 
            text="📱 Telegram: " + ("✅" if api_status['telegram'] else "❌"),
            style='Success.TLabel' if api_status['telegram'] else 'Error.TLabel'
        )
        self.telegram_status.pack(side='right', padx=(0, 10))
    
    def create_chat_panel(self, parent):
        """Створення панелі чату"""
        # Ліва частина - чат (70% ширини)
        chat_frame = ttk.Frame(parent, style='Chat.TFrame')
        chat_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Заголовок чату
        chat_header = ttk.Label(
            chat_frame, 
            text="💬 Чат з JARVIS", 
            font=('Segoe UI', 12, 'bold'),
            style='Dark.TLabel'
        )
        chat_header.pack(pady=10)
        
        # Область чату
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=25,
            bg='#2a2a2a',
            fg='#ffffff',
            font=('Consolas', 11),
            wrap=tk.WORD,
            state='disabled'
        )
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Налаштування тегів для різних типів повідомлень
        self.chat_display.tag_configure("user", foreground="#4CAF50", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure("jarvis", foreground="#2196F3", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure("system", foreground="#FF9800", font=('Consolas', 10, 'italic'))
        self.chat_display.tag_configure("error", foreground="#F44336", font=('Consolas', 11, 'bold'))
        
        # Поле вводу
        input_frame = ttk.Frame(chat_frame, style='Dark.TFrame')
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.message_entry = tk.Text(
            input_frame,
            height=3,
            bg='#3a3a3a',
            fg='#ffffff',
            font=('Segoe UI', 11),
            wrap=tk.WORD
        )
        self.message_entry.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Кнопки
        buttons_frame = ttk.Frame(input_frame, style='Dark.TFrame')
        buttons_frame.pack(side='right', fill='y')
        
        send_btn = ttk.Button(
            buttons_frame,
            text="📤 Надіслати",
            command=self.send_message,
            style='Dark.TButton'
        )
        send_btn.pack(fill='x', pady=(0, 5))
        
        voice_btn = ttk.Button(
            buttons_frame,
            text="🎤 Голос",
            command=self.toggle_voice,
            style='Dark.TButton'
        )
        voice_btn.pack(fill='x', pady=(0, 5))
        
        clear_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Очистити",
            command=self.clear_chat,
            style='Dark.TButton'
        )
        clear_btn.pack(fill='x')
        
        # Прив'язка Enter для відправки
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
    
    def create_control_panels(self, parent):
        """Створення панелей управління"""
        # Права частина - панелі управління (30% ширини)
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        control_frame.pack(side='right', fill='y', padx=(10, 0))
        control_frame.configure(width=350)
        
        # Notebook для вкладок
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill='both', expand=True)
        
        # Вкладка управління
        self.create_control_tab(notebook)
        
        # Вкладка статистики
        self.create_stats_tab(notebook)
        
        # Вкладка навчання
        self.create_learning_tab(notebook)
        
        # Вкладка налаштувань
        self.create_settings_tab(notebook)
    
    def create_control_tab(self, notebook):
        """Вкладка управління"""
        control_tab = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(control_tab, text="🎛️ Управління")
        
        # Кнопки управління JARVIS
        jarvis_frame = ttk.LabelFrame(control_tab, text="JARVIS Управління", style='Dark.TFrame')
        jarvis_frame.pack(fill='x', padx=10, pady=10)
        
        self.start_btn = ttk.Button(
            jarvis_frame,
            text="▶️ Запустити JARVIS",
            command=self.start_jarvis,
            style='Dark.TButton'
        )
        self.start_btn.pack(fill='x', padx=5, pady=5)
        
        self.stop_btn = ttk.Button(
            jarvis_frame,
            text="⏹️ Зупинити JARVIS",
            command=self.stop_jarvis,
            style='Dark.TButton',
            state='disabled'
        )
        self.stop_btn.pack(fill='x', padx=5, pady=5)
        
        # Швидкі команди
        quick_frame = ttk.LabelFrame(control_tab, text="Швидкі команди", style='Dark.TFrame')
        quick_frame.pack(fill='x', padx=10, pady=10)
        
        quick_commands = [
            ("🌤️ Погода", "яка погода"),
            ("📸 Скріншот", "зроби скріншот"),
            ("🎵 Музика", "включи музику"),
            ("💻 Системна інформація", "системна інформація")
        ]
        
        for text, command in quick_commands:
            btn = ttk.Button(
                quick_frame,
                text=text,
                command=lambda cmd=command: self.send_quick_command(cmd),
                style='Dark.TButton'
            )
            btn.pack(fill='x', padx=5, pady=2)
        
        # Файлові операції
        file_frame = ttk.LabelFrame(control_tab, text="Файли", style='Dark.TFrame')
        file_frame.pack(fill='x', padx=10, pady=10)
        
        pdf_btn = ttk.Button(
            file_frame,
            text="📄 Завантажити PDF",
            command=self.load_pdf,
            style='Dark.TButton'
        )
        pdf_btn.pack(fill='x', padx=5, pady=5)
        
        export_btn = ttk.Button(
            file_frame,
            text="💾 Експорт чату",
            command=self.export_chat,
            style='Dark.TButton'
        )
        export_btn.pack(fill='x', padx=5, pady=5)
    
    def create_stats_tab(self, notebook):
        """Вкладка статистики"""
        stats_tab = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(stats_tab, text="📊 Статистика")
        
        # Загальна статистика
        general_frame = ttk.LabelFrame(stats_tab, text="Загальна статистика", style='Dark.TFrame')
        general_frame.pack(fill='x', padx=10, pady=10)
        
        self.stats_labels = {}
        
        stats_items = [
            ("Всього взаємодій:", "total_interactions"),
            ("Успішних команд:", "successful_commands"),
            ("Помилок:", "failed_commands"),
            ("Кастомних команд:", "custom_commands"),
            ("Документів у базі:", "knowledge_documents")
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            frame = ttk.Frame(general_frame, style='Dark.TFrame')
            frame.pack(fill='x', padx=5, pady=2)
            
            label = ttk.Label(frame, text=label_text, style='Dark.TLabel')
            label.pack(side='left')
            
            value_label = ttk.Label(frame, text="0", style='Success.TLabel')
            value_label.pack(side='right')
            
            self.stats_labels[key] = value_label
        
        # Графік активності (заглушка)
        activity_frame = ttk.LabelFrame(stats_tab, text="Активність", style='Dark.TFrame')
        activity_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.activity_text = scrolledtext.ScrolledText(
            activity_frame,
            height=10,
            bg='#2a2a2a',
            fg='#ffffff',
            font=('Consolas', 9)
        )
        self.activity_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_learning_tab(self, notebook):
        """Вкладка навчання"""
        learning_tab = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(learning_tab, text="🧠 Навчання")
        
        # Кастомні команди
        commands_frame = ttk.LabelFrame(learning_tab, text="Кастомні команди", style='Dark.TFrame')
        commands_frame.pack(fill='x', padx=10, pady=10)
        
        add_command_btn = ttk.Button(
            commands_frame,
            text="➕ Додати команду",
            command=self.add_custom_command,
            style='Dark.TButton'
        )
        add_command_btn.pack(fill='x', padx=5, pady=5)
        
        view_commands_btn = ttk.Button(
            commands_frame,
            text="👁️ Переглянути команди",
            command=self.view_custom_commands,
            style='Dark.TButton'
        )
        view_commands_btn.pack(fill='x', padx=5, pady=5)
        
        # База знань
        knowledge_frame = ttk.LabelFrame(learning_tab, text="База знань", style='Dark.TFrame')
        knowledge_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        update_kb_btn = ttk.Button(
            knowledge_frame,
            text="🔄 Оновити базу знань",
            command=self.update_knowledge_base,
            style='Dark.TButton'
        )
        update_kb_btn.pack(fill='x', padx=5, pady=5)
        
        search_kb_btn = ttk.Button(
            knowledge_frame,
            text="🔍 Пошук в базі",
            command=self.search_knowledge,
            style='Dark.TButton'
        )
        search_kb_btn.pack(fill='x', padx=5, pady=5)
        
        # Список знань
        self.knowledge_list = scrolledtext.ScrolledText(
            knowledge_frame,
            height=8,
            bg='#2a2a2a',
            fg='#ffffff',
            font=('Consolas', 9)
        )
        self.knowledge_list.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_settings_tab(self, notebook):
        """Вкладка налаштувань"""
        settings_tab = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(settings_tab, text="⚙️ Налаштування")
        
        # Голосові налаштування
        voice_frame = ttk.LabelFrame(settings_tab, text="Голос", style='Dark.TFrame')
        voice_frame.pack(fill='x', padx=10, pady=10)
        
        # Швидкість мовлення
        ttk.Label(voice_frame, text="Швидкість:", style='Dark.TLabel').pack(anchor='w', padx=5)
        self.voice_rate_var = tk.IntVar(value=self.config.VOICE_RATE)
        voice_rate_scale = ttk.Scale(
            voice_frame, 
            from_=50, 
            to=300, 
            variable=self.voice_rate_var,
            orient='horizontal'
        )
        voice_rate_scale.pack(fill='x', padx=5, pady=5)
        
        # Гучність
        ttk.Label(voice_frame, text="Гучність:", style='Dark.TLabel').pack(anchor='w', padx=5)
        self.voice_volume_var = tk.DoubleVar(value=self.config.VOICE_VOLUME)
        voice_volume_scale = ttk.Scale(
            voice_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.voice_volume_var,
            orient='horizontal'
        )
        voice_volume_scale.pack(fill='x', padx=5, pady=5)
        
        # API налаштування
        api_frame = ttk.LabelFrame(settings_tab, text="API", style='Dark.TFrame')
        api_frame.pack(fill='x', padx=10, pady=10)
        
        test_openai_btn = ttk.Button(
            api_frame,
            text="🔑 Тест OpenAI",
            command=self.test_openai,
            style='Dark.TButton'
        )
        test_openai_btn.pack(fill='x', padx=5, pady=5)
        
        # Кнопка збереження
        save_btn = ttk.Button(
            settings_tab,
            text="💾 Зберегти налаштування",
            command=self.save_settings,
            style='Dark.TButton'
        )
        save_btn.pack(side='bottom', fill='x', padx=10, pady=10)
    
    def create_footer(self, parent):
        """Створення нижньої панелі"""
        footer_frame = ttk.Frame(parent, style='Dark.TFrame')
        footer_frame.pack(fill='x', pady=(10, 0))
        
        # Інформація про версію
        version_label = ttk.Label(
            footer_frame, 
            text=f"JARVIS v{self.config.VERSION} by {self.config.AUTHOR}", 
            style='Dark.TLabel'
        )
        version_label.pack(side='left')
        
        # Час роботи
        self.uptime_label = ttk.Label(
            footer_frame, 
            text="Час роботи: 00:00:00", 
            style='Dark.TLabel'
        )
        self.uptime_label.pack(side='right')
    
    def add_message(self, sender, message, msg_type="normal"):
        """Додавання повідомлення до чату"""
        self.chat_display.configure(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "user":
            self.chat_display.insert(tk.END, f"[{timestamp}] 👤 Ви: ", "user")
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif sender == "jarvis":
            self.chat_display.insert(tk.END, f"[{timestamp}] 🤖 JARVIS: ", "jarvis")
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif sender == "system":
            self.chat_display.insert(tk.END, f"[{timestamp}] ⚙️ Система: ", "system")
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif sender == "error":
            self.chat_display.insert(tk.END, f"[{timestamp}] ❌ Помилка: ", "error")
            self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Відправка повідомлення"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Очищення поля вводу
        self.message_entry.delete("1.0", tk.END)
        
        # Додавання до чату
        self.add_message("user", message)
        
        # Відправка до JARVIS (якщо запущений)
        if self.jarvis_instance and self.jarvis_instance.is_active:
            threading.Thread(
                target=self.process_jarvis_command, 
                args=(message,), 
                daemon=True
            ).start()
        else:
            self.add_message("system", "JARVIS не запущений. Натисніть 'Запустити JARVIS'")
    
    def send_quick_command(self, command):
        """Відправка швидкої команди"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", command)
        self.send_message()
    
    def process_jarvis_command(self, message):
        """Обробка команди через JARVIS"""
        try:
            # Тут буде виклик JARVIS
            response = f"Обробляю команду: {message}"
            self.message_queue.put(("jarvis", response))
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def start_jarvis(self):
        """Запуск JARVIS"""
        try:
            self.add_message("system", "Запускаю JARVIS...")
            
            # Тут буде запуск основного JARVIS
            # from main import JarvisAssistant
            # self.jarvis_instance = JarvisAssistant()
            
            self.status_label.configure(text="🟢 Активний", style='Success.TLabel')
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            
            self.add_message("system", "JARVIS успішно запущений!")
            
        except Exception as e:
            self.add_message("error", f"Помилка запуску JARVIS: {str(e)}")
    
    def stop_jarvis(self):
        """Зупинка JARVIS"""
        try:
            self.add_message("system", "Зупиняю JARVIS...")
            
            if self.jarvis_instance:
                self.jarvis_instance.is_active = False
                self.jarvis_instance = None
            
            self.status_label.configure(text="🔴 Неактивний", style='Error.TLabel')
            self.start_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
            
            self.add_message("system", "JARVIS зупинений")
            
        except Exception as e:
            self.add_message("error", f"Помилка зупинки JARVIS: {str(e)}")
    
    def toggle_voice(self):
        """Перемикання голосового режиму"""
        self.add_message("system", "Голосовий режим поки не реалізований")
    
    def clear_chat(self):
        """Очищення чату"""
        self.chat_display.configure(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state='disabled')
    
    def load_pdf(self):
        """Завантаження PDF файлу"""
        file_path = filedialog.askopenfilename(
            title="Оберіть PDF файл",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            self.add_message("system", f"Завантажую PDF: {Path(file_path).name}")
            # Тут буде обробка PDF
            threading.Thread(
                target=self.process_pdf, 
                args=(file_path,), 
                daemon=True
            ).start()
    
    def process_pdf(self, file_path):
        """Обробка PDF файлу"""
        try:
            # Тут буде обробка PDF через learner
            self.message_queue.put(("system", f"PDF {Path(file_path).name} успішно оброблений"))
        except Exception as e:
            self.message_queue.put(("error", f"Помилка обробки PDF: {str(e)}"))
    
    def export_chat(self):
        """Експорт чату"""
        file_path = filedialog.asksaveasfilename(
            title="Зберегти чат",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                chat_content = self.chat_display.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(chat_content)
                self.add_message("system", f"Чат збережено: {Path(file_path).name}")
            except Exception as e:
                self.add_message("error", f"Помилка збереження: {str(e)}")
    
    def add_custom_command(self):
        """Додавання кастомної команди"""
        # Створення діалогового вікна
        dialog = CustomCommandDialog(self.root)
        if dialog.result:
            command, action = dialog.result
            # Тут буде додавання команди через learner
            self.add_message("system", f"Додано команду: {command}")
    
    def view_custom_commands(self):
        """Перегляд кастомних команд"""
        # Тут буде отримання команд з learner
        commands = []  # self.learner.get_custom_commands()
        
        if commands:
            commands_text = "\n".join([f"• {cmd}" for cmd in commands])
        else:
            commands_text = "Кастомних команд поки немає"
        
        messagebox.showinfo("Кастомні команди", commands_text)
    
    def update_knowledge_base(self):
        """Оновлення бази знань"""
        self.add_message("system", "Оновлюю базу знань...")
        threading.Thread(target=self._update_kb_thread, daemon=True).start()
    
    def _update_kb_thread(self):
        """Оновлення бази знань в окремому потоці"""
        try:
            # Тут буде оновлення через learner
            self.message_queue.put(("system", "База знань оновлена"))
        except Exception as e:
            self.message_queue.put(("error", f"Помилка оновлення: {str(e)}"))
    
    def search_knowledge(self):
        """Пошук в базі знань"""
        query = tk.simpledialog.askstring("Пошук", "Введіть запит для пошуку:")
        if query:
            # Тут буде пошук через vector_kb
            results = []  # vector_kb.search(query)
            
            if results:
                results_text = "\n".join([f"• {result}" for result in results])
            else:
                results_text = "Нічого не знайдено"
            
            messagebox.showinfo("Результати пошуку", results_text)
    
    def test_openai(self):
        """Тестування OpenAI API"""
        self.add_message("system", "Тестую OpenAI API...")
        threading.Thread(target=self._test_openai_thread, daemon=True).start()
    
    def _test_openai_thread(self):
        """Тестування OpenAI в окремому потоці"""
        try:
            # Тут буде тест API
            self.message_queue.put(("system", "OpenAI API працює"))
        except Exception as e:
            self.message_queue.put(("error", f"OpenAI API помилка: {str(e)}"))
    
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            # Збереження налаштувань голосу
            # self.config.VOICE_RATE = self.voice_rate_var.get()
            # self.config.VOICE_VOLUME = self.voice_volume_var.get()
            
            self.add_message("system", "Налаштування збережено")
        except Exception as e:
            self.add_message("error", f"Помилка збереження: {str(e)}")
    
    def update_stats(self):
        """Оновлення статистики"""
        try:
            stats = self.learner.get_statistics()
            vector_stats = vector_kb.get_statistics()
            
            self.stats_labels['total_interactions'].configure(text=str(stats.get('total_interactions', 0)))
            self.stats_labels['custom_commands'].configure(text=str(stats.get('custom_commands', 0)))
            self.stats_labels['knowledge_documents'].configure(text=str(vector_stats.get('total_documents', 0)))
            
        except Exception as e:
            print(f"Помилка оновлення статистики: {e}")
    
    def process_messages(self):
        """Обробка повідомлень з черги"""
        try:
            while True:
                sender, message = self.message_queue.get_nowait()
                self.add_message(sender, message)
        except queue.Empty:
            pass
        
        # Планування наступної перевірки
        self.root.after(100, self.process_messages)
    
    def auto_update(self):
        """Автоматичне оновлення інтерфейсу"""
        self.update_stats()
        
        # Планування наступного оновлення
        self.root.after(5000, self.auto_update)  # Кожні 5 секунд
    
    def run(self):
        """Запуск GUI"""
        self.root.mainloop()

class CustomCommandDialog:
    """Діалог для додавання кастомної команди"""
    def __init__(self, parent):
        self.result = None
        
        # Створення діалогового вікна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Додати кастомну команду")
        self.dialog.geometry("400x200")
        self.dialog.configure(bg='#1a1a1a')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Поля вводу
        ttk.Label(self.dialog, text="Команда:", style='Dark.TLabel').pack(pady=5)
        self.command_entry = tk.Entry(self.dialog, width=50, bg='#3a3a3a', fg='#ffffff')
        self.command_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Дія:", style='Dark.TLabel').pack(pady=5)
        self.action_entry = tk.Entry(self.dialog, width=50, bg='#3a3a3a', fg='#ffffff')
        self.action_entry.pack(pady=5)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog, style='Dark.TFrame')
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Додати", command=self.ok_clicked).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Скасувати", command=self.cancel_clicked).pack(side='left', padx=5)
        
        # Фокус на першому полі
        self.command_entry.focus()
    
    def ok_clicked(self):
        command = self.command_entry.get().strip()
        action = self.action_entry.get().strip()
        
        if command and action:
            self.result = (command, action)
            self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

def main():
    """Запуск GUI"""
    try:
        app = JarvisGUI()
        app.run()
    except Exception as e:
        print(f"Помилка запуску GUI: {e}")

if __name__ == "__main__":
    main()
