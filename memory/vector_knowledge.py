#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Векторна база знань для JARVIS
"""

import numpy as np
import json
import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any
from config import Config

class VectorKnowledgeBase:
    def __init__(self):
        self.config = Config()
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        
        self.vector_db_path = self.config.KNOWLEDGE_BASE_DIR / "vectors.index"
        self.metadata_path = self.config.KNOWLEDGE_BASE_DIR / "metadata.json"
        
        self._initialize_model()
        self._load_existing_data()
        
        logging.info("VectorKnowledgeBase ініціалізовано")
    
    def _initialize_model(self):
        """Ініціалізація моделі для векторизації"""
        try:
            # Використовуємо багатомовну модель
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logging.info("Модель векторизації завантажена")
        except Exception as e:
            logging.error(f"Помилка завантаження моделі: {e}")
            # Fallback до простішої моделі
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logging.info("Завантажена fallback модель")
            except Exception as e2:
                logging.error(f"Критична помилка моделі: {e2}")
                self.model = None
    
    def _load_existing_data(self):
        """Завантаження існуючих даних"""
        try:
            if self.vector_db_path.exists() and self.metadata_path.exists():
                # Завантаження індексу
                self.index = faiss.read_index(str(self.vector_db_path))
                
                # Завантаження метаданих
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
                
                logging.info(f"Завантажено {len(self.documents)} документів з векторної бази")
            else:
                self._create_new_index()
                
        except Exception as e:
            logging.error(f"Помилка завантаження векторної бази: {e}")
            self._create_new_index()
    
    def _create_new_index(self):
        """Створення нового індексу"""
        try:
            if self.model:
                # Розмірність векторів для обраної моделі
                dimension = 384  # для MiniLM моделей
                self.index = faiss.IndexFlatIP(dimension)  # Inner Product для косинусної подібності
                self.documents = []
                self.metadata = []
                logging.info("Створено новий векторний індекс")
        except Exception as e:
            logging.error(f"Помилка створення індексу: {e}")
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None):
        """
        Додавання документа до векторної бази
        
        Args:
            text (str): Текст документа
            metadata (dict): Метадані документа
        """
        try:
            if not self.model or not self.index:
                logging.error("Модель або індекс не ініціалізовані")
                return False
            
            # Векторизація тексту
            vector = self.model.encode([text])
            
            # Нормалізація для косинусної подібності
            faiss.normalize_L2(vector)
            
            # Додавання до індексу
            self.index.add(vector)
            
            # Збереження тексту та метаданих
            self.documents.append(text)
            self.metadata.append(metadata or {})
            
            # Збереження на диск
            self._save_to_disk()
            
            logging.info(f"Додано документ до векторної бази: {text[:50]}...")
            return True
            
        except Exception as e:
            logging.error(f"Помилка додавання документа: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Пошук схожих документів
        
        Args:
            query (str): Пошуковий запит
            top_k (int): Кількість результатів
            
        Returns:
            List[Dict]: Список знайдених документів з оцінками
        """
        try:
            if not self.model or not self.index or len(self.documents) == 0:
                return []
            
            # Векторизація запиту
            query_vector = self.model.encode([query])
            faiss.normalize_L2(query_vector)
            
            # Пошук
            scores, indices = self.index.search(query_vector, min(top_k, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    results.append({
                        'text': self.documents[idx],
                        'metadata': self.metadata[idx],
                        'score': float(score),
                        'index': int(idx)
                    })
            
            return results
            
        except Exception as e:
            logging.error(f"Помилка пошуку: {e}")
            return []
    
    def add_pdf_knowledge(self, pdf_content: str, filename: str):
        """Додавання знань з PDF"""
        try:
            # Розбиття на частини для кращого пошуку
            chunks = self._split_text(pdf_content, chunk_size=500)
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    'source': 'pdf',
                    'filename': filename,
                    'chunk_id': i,
                    'type': 'pdf_content'
                }
                self.add_document(chunk, metadata)
            
            logging.info(f"Додано {len(chunks)} частин з PDF: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Помилка додавання PDF: {e}")
            return False
    
    def add_interaction(self, user_input: str, jarvis_response: str):
        """Додавання взаємодії до бази знань"""
        try:
            interaction_text = f"Питання: {user_input}\nВідповідь: {jarvis_response}"
            metadata = {
                'source': 'interaction',
                'type': 'qa_pair',
                'user_input': user_input,
                'jarvis_response': jarvis_response
            }
            
            return self.add_document(interaction_text, metadata)
            
        except Exception as e:
            logging.error(f"Помилка додавання взаємодії: {e}")
            return False
    
    def _split_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Розбиття тексту на частини"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _save_to_disk(self):
        """Збереження індексу та метаданих на диск"""
        try:
            if self.index:
                faiss.write_index(self.index, str(self.vector_db_path))
            
            metadata_data = {
                'documents': self.documents,
                'metadata': self.metadata
            }
            
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"Помилка збереження на диск: {e}")
    
    def get_statistics(self):
        """Статистика векторної бази"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'model_loaded': self.model is not None
        }
    
    def find_relevant_context(self, query: str, max_context_length: int = 1000) -> str:
        """Знаходження релевантного контексту для GPT"""
        try:
            results = self.search(query, top_k=3)
            
            context_parts = []
            current_length = 0
            
            for result in results:
                text = result['text']
                if current_length + len(text) <= max_context_length:
                    context_parts.append(text)
                    current_length += len(text)
                else:
                    # Додаємо частину тексту, що поміщається
                    remaining_space = max_context_length - current_length
                    if remaining_space > 100:  # Мінімальний розмір частини
                        context_parts.append(text[:remaining_space])
                    break
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Помилка пошуку контексту: {e}")
            return ""

# Глобальний екземпляр
vector_kb = VectorKnowledgeBase()

def add_knowledge(text, metadata=None):
    """Додавання знань до векторної бази"""
    return vector_kb.add_document(text, metadata)

def search_knowledge(query, top_k=5):
    """Пошук знань"""
    return vector_kb.search(query, top_k)

def add_pdf_to_knowledge(pdf_content, filename):
    """Додавання PDF до бази знань"""
    return vector_kb.add_pdf_knowledge(pdf_content, filename)

def get_context_for_gpt(query):
    """Отримання контексту для GPT"""
    return vector_kb.find_relevant_context(query)

# Тестування
if __name__ == "__main__":
    # Тестування векторної бази
    vector_kb.add_document("Python - це мова програмування", {"topic": "programming"})
    vector_kb.add_document("JARVIS - це AI асистент", {"topic": "ai"})
    
    results = vector_kb.search("програмування")
    for result in results:
        print(f"Знайдено: {result['text']} (оцінка: {result['score']:.3f})")
