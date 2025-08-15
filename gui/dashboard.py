#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Графічний інтерфейс (Dashboard) для JARVIS
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
from datetime import datetime
import sys
import os

# Додавання батьківської директорії до шляху
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.learner import JarvisLearner
from config import Config

class JarvisDashboard:
    def __init__(self):
        self.config = Config()
        self.learner = JarvisLearner()
        
        # Створення головного вікна
        self.root = tk.Tk()
        self.root.title("JARVIS MVP Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Стилізація
        self.setup_styles()
        
        # Створення інтерфейсу
        self.create_widgets()
        
        # Запуск оновлення даних
        self.update_data()
    
    def setup_styles(self):
        """Налаштування стилів"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Темна тема
        style.configure('TLabel', background='#1e1e1e', foreground='#ffffff')
        style.configure('TButton', background='#3e3e3e', foreground='#ffffff')
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TNotebook', background='#1e1e1e')
        style.configure('TNotebook.Tab', background='#3e3e3e', foreground='#ffffff')
    
    def create_widgets(self):
        """Створення віджетів інтерфейсу"""
        # Заголовок
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = ttk.Label(
            title_frame, 
            text="🤖 JARVIS MVP Dashboard", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side='left')
        
        # Статус
        self.status_label = ttk.Label(
            title_frame, 
            text="Статус: Готовий", 
            font=('Arial', 10)
        )
        self.status_label.pack(side='right')
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладка історії
        self.create_history_tab()
        
        # Вкладка статистики
        self.create_stats_tab()
        
        # Вкладка команд
        self.create_commands_tab()
        
        # Вкладка налаштувань
        self.create_settings_tab()
        
        # Панель керування
        self.create_control_panel()
    
    def create_history_tab(self):
        """Створення вкладки історії"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📜 Історія")
        
        # Список взаємодій
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=20,
            bg='#2e2e2e',
            fg='#ffffff',
            font=('Consolas', 10)
        )
        self.history_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Кнопка оновлення
        refresh_btn = ttk.Button(
            history_frame,
            text="🔄 Оновити",
            command=self.refresh_history
        )
        refresh_btn.pack(pady=5)
    
    def create_stats_tab(self):
        """Створення вкладки статистики"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Статистика")
        
        # Фрейм для статистики
        stats_info_frame = ttk.Frame(stats_frame)
        stats_info_frame.pack(fill='x', padx=10, pady=10)
        
        # Лейбли статистики
        self.stats_labels = {}
        
        stats_items = [
            ("Всього взаємодій:", "total_interactions"),
            ("Кастомних команд:", "custom_commands"),
            ("Записів знань:", "knowledge_count"),
            ("Останнє оновлення:", "last_update")
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            label = ttk.Label(stats_info_frame, text=label_text, font=('Arial', 12))
            label.grid(row=i, column=0, sticky='w', pady=5)
            
            value_label = ttk.Label(stats_info_frame, text="0", font=('Arial', 12, 'bold'))
            value_label.grid(row=i, column=1, sticky='w', padx=(10, 0), pady=5)
            
            self.stats_labels[key] = value_label
    
    def create_commands_tab(self):
        """Створення вкладки команд"""
        commands_frame = ttk.Frame(self.notebook)
        self.notebook.add(commands_frame, text="⚡ Команди")
        
        # Список кастомних команд
        commands_label = ttk.Label(
            commands_frame, 
            text="Кастомні команди:", 
            font=('Arial', 12, 'bold')
        )
        commands_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.commands_text = scrolledtext.ScrolledText(
            commands_frame,
            height=15,
            bg='#2e2e2e',
            fg='#ffffff',
            font=('Consolas', 10)
        )
        self.commands_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Кнопки керування командами
        commands_btn_frame = ttk.Frame(commands_frame)
        commands_btn_frame.pack(fill='x', padx=10, pady=5)
        
        refresh_commands_btn = ttk.Button(
            commands_btn_frame,
            text="🔄 Оновити команди",
            command=self.refresh_commands
        )
        refresh_commands_btn.pack(side='left', padx=(0, 5))
        
        clear_commands_btn = ttk.Button(
            commands_btn_frame,
            text="🗑️ Очистити команди",
            command=self.clear_commands
        )
        clear_commands_btn.pack(side='left')
    
    def create_settings_tab(self):
        """Створення вкладки налаштувань"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Налаштування")
        
        # Налаштування голосу
        voice_frame = ttk.LabelFrame(settings_frame, text="Голосові налаштування")
        voice_frame.pack(fill='x', padx=10, pady=10)
        
        # Швидкість мовлення
        ttk.Label(voice_frame, text="Швидкість мовлення:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.voice_rate_var = tk.IntVar(value=self.config.VOICE_RATE)
        voice_rate_scale = ttk.Scale(
            voice_frame, 
            from_=50, 
            to=300, 
            variable=self.voice_rate_var,
            orient='horizontal'
        )
        voice_rate_scale.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Гучність
        ttk.Label(voice_frame, text="Гучність:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.voice_volume_var = tk.DoubleVar(value=self.config.VOICE_VOLUME)
        voice_volume_scale = ttk.Scale(
            voice_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.voice_volume_var,
            orient='horizontal'
        )
        voice_volume_scale.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        voice_frame.columnconfigure(1, weight=1)
        
        # Кнопка збереження налаштувань
        save_settings_btn = ttk.Button(
            settings_frame,
            text="💾 Зберегти налаштування",
            command=self.save_settings
        )
        save_settings_btn.pack(pady=10)
    
    def create_control_panel(self):
        """Створення панелі керування"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Кнопки керування
        start_btn = ttk.Button(
            control_frame,
            text="▶️ Запустити JARVIS",
            command=self.start_jarvis
        )
        start_btn.pack(side='left', padx=(0, 5))
        
        stop_btn = ttk.Button(
            control_frame,
            text="⏹️ Зупинити JARVIS",
            command=self.stop_jarvis
        )
        stop_btn.pack(side='left', padx=(0, 5))
        
        test_voice_btn = ttk.Button(
            control_frame,
            text="🔊 Тест голосу",
            command=self.test_voice
        )
        test_voice_btn.pack(side='left', padx=(0, 5))
        
        # Кнопка виходу
        exit_btn = ttk.Button(
            control_frame,
            text="❌ Вихід",
            command=self.exit_application
        )
        exit_btn.pack(side='right')
    
    def refresh_history(self):
        """Оновлення історії взаємодій"""
        try:
            history = self.learner.get_interaction_history(50)
            
            self.history_text.delete(1.0, tk.END)
            
            for interaction in history:
                timestamp = interaction['timestamp']
                user_input = interaction['user_input']
                jarvis_response = interaction['jarvis_response']
                
                self.history_text.insert(tk.END, f"[{timestamp}]\n")
                self.history_text.insert(tk.END, f"👤 Користувач: {user_input}\n")
                if jarvis_response:
                    self.history_text.insert(tk.END, f"🤖 JARVIS: {jarvis_response}\n")
                self.history_text.insert(tk.END, "-" * 50 + "\n\n")
            
            self.history_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося оновити історію: {e}")
    
    def refresh_commands(self):
        """Оновлення списку команд"""
        try:
            import sqlite3
            
            with sqlite3.connect(self.learner.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT command_pattern, action_description, usage_count 
                    FROM custom_commands 
                    ORDER BY usage_count DESC
                ''')
                commands = cursor.fetchall()
            
            self.commands_text.delete(1.0, tk.END)
            
            if commands:
                for pattern, description, usage_count in commands:
                    self.commands_text.insert(tk.END, f"Команда: {pattern}\n")
                    self.commands_text.insert(tk.END, f"Дія: {description}\n")
                    self.commands_text.insert(tk.END, f"Використань: {usage_count}\n")
                    self.commands_text.insert(tk.END, "-" * 40 + "\n\n")
            else:
                self.commands_text.insert(tk.END, "Кастомних команд поки немає.\n")
                self.commands_text.insert(tk.END, "Скажіть JARVIS 'навчися новій команді' для додавання.")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося оновити команди: {e}")
    
    def clear_commands(self):
        """Очищення кастомних команд"""
        result = messagebox.askyesno(
            "Підтвердження", 
            "Ви впевнені, що хочете видалити всі кастомні команди?"
        )
        
        if result:
            try:
                import sqlite3
                
                with sqlite3.connect(self.learner.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM custom_commands')
                    conn.commit()
                
                self.refresh_commands()
                messagebox.showinfo("Успіх", "Кастомні команди видалено.")
                
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити команди: {e}")
    
    def update_data(self):
        """Оновлення даних на дашборді"""
        try:
            # Оновлення статистики
            stats = self.learner.get_statistics()
            
            for key, value in stats.items():
                if key in self.stats_labels:
                    self.stats_labels[key].config(text=str(value))
            
            # Автоматичне оновлення історії
            if self.notebook.index(self.notebook.select()) == 0:  # Якщо активна вкладка історії
                self.refresh_history()
            
        except Exception as e:
            print(f"Помилка оновлення даних: {e}")
        
        # Планування наступного оновлення
        self.root.after(5000, self.update_data)  # Кожні 5 секунд
    
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            # Тут можна зберегти налаштування в конфігураційний файл
            messagebox.showinfo("Успіх", "Налаштування збережено!")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {e}")
    
    def start_jarvis(self):
        """Запуск JARVIS"""
        try:
            # Тут буде логіка запуску JARVIS в окремому потоці
            self.status_label.config(text="Статус: Запускається...")
            messagebox.showinfo("JARVIS", "JARVIS запускається...")
            self.status_label.config(text="Статус: Активний")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося запустити JARVIS: {e}")
            self.status_label.config(text="Статус: Помилка")
    
    def stop_jarvis(self):
        """Зупинка JARVIS"""
        try:
            self.status_label.config(text="Статус: Зупиняється...")
            messagebox.showinfo("JARVIS", "JARVIS зупинено.")
            self.status_label.config(text="Статус: Неактивний")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зупинити JARVIS: {e}")
    
    def test_voice(self):
        """Тестування голосу"""
        try:
            # Тут буде тестування голосового синтезу
            messagebox.showinfo("Тест голосу", "Тестую голос JARVIS...")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка тестування голосу: {e}")
    
    def exit_application(self):
        """Вихід з програми"""
        result = messagebox.askyesno("Вихід", "Ви впевнені, що хочете вийти?")
        if result:
            self.root.quit()
    
    def run(self):
        """Запуск GUI"""
        self.root.mainloop()

def main():
    """Головна функція запуску GUI"""
    try:
        dashboard = JarvisDashboard()
        dashboard.run()
    except Exception as e:
        print(f"Помилка запуску GUI: {e}")

if __name__ == "__main__":
    main()
