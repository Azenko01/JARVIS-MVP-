#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Розширений процесор PDF файлів для JARVIS
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import fitz  # PyMuPDF для кращої обробки
from memory.vector_knowledge import vector_kb
from plugins.gpt_integration import analyze_pdf_with_gpt
from config import Config

class PDFProcessor:
    def __init__(self):
        self.config = Config()
        self.supported_formats = ['.pdf']
        
    async def process_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """
        Повна обробка PDF файлу
        
        Args:
            file_path (str): Шлях до PDF файлу
            
        Returns:
            Dict: Результат обробки
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"success": False, "error": "Файл не знайдено"}
            
            if file_path.suffix.lower() not in self.supported_formats:
                return {"success": False, "error": "Непідтримуваний формат файлу"}
            
            # Витягування тексту
            text_content = await self._extract_text(file_path)
            
            if not text_content.strip():
                return {"success": False, "error": "Не вдалося витягти текст з PDF"}
            
            # Аналіз через GPT
            gpt_analysis = None
            if self.config.OPENAI_API_KEY:
                gpt_analysis = await analyze_pdf_with_gpt(text_content)
            
            # Розбиття на частини для векторної бази
            chunks = self._split_into_chunks(text_content)
            
            # Додавання до векторної бази
            added_chunks = 0
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source": "pdf",
                    "filename": file_path.name,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "file_path": str(file_path)
                }
                
                if vector_kb.add_document(chunk, metadata):
                    added_chunks += 1
            
            # Збереження аналізу GPT
            if gpt_analysis:
                gpt_metadata = {
                    "source": "pdf_gpt_analysis",
                    "filename": file_path.name,
                    "type": "analysis"
                }
                
                if isinstance(gpt_analysis, dict):
                    for key, value in gpt_analysis.items():
                        if isinstance(value, str) and value.strip():
                            vector_kb.add_document(f"{key}: {value}", {**gpt_metadata, "section": key})
                else:
                    vector_kb.add_document(str(gpt_analysis), gpt_metadata)
            
            return {
                "success": True,
                "filename": file_path.name,
                "text_length": len(text_content),
                "chunks_added": added_chunks,
                "total_chunks": len(chunks),
                "gpt_analysis": gpt_analysis is not None,
                "summary": self._create_summary(text_content, gpt_analysis)
            }
            
        except Exception as e:
            logging.error(f"Помилка обробки PDF: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_text(self, file_path: Path) -> str:
        """Витягування тексту з PDF"""
        text_content = ""
        
        try:
            # Спроба з PyMuPDF (кращий для складних PDF)
            doc = fitz.open(str(file_path))
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            doc.close()
            
        except Exception as e:
            logging.warning(f"PyMuPDF помилка: {e}, спробую PyPDF2")
            
            try:
                # Fallback до PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()
                        
            except Exception as e2:
                logging.error(f"PyPDF2 помилка: {e2}")
                raise e2
        
        return text_content
    
    def _split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Розбиття тексту на частини з перекриттям"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = ' '.join(chunk_words)
            
            if chunk.strip():
                chunks.append(chunk)
            
            # Якщо це останній чанк, зупиняємося
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    def _create_summary(self, text: str, gpt_analysis: Any) -> str:
        """Створення короткого резюме"""
        summary_parts = []
        
        # Базова інформація
        word_count = len(text.split())
        summary_parts.append(f"Кількість слів: {word_count}")
        
        # Інформація з GPT аналізу
        if gpt_analysis and isinstance(gpt_analysis, dict):
            if 'summary' in gpt_analysis:
                summary_parts.append(f"Резюме: {gpt_analysis['summary'][:200]}...")
            
            if 'key_points' in gpt_analysis:
                key_points = gpt_analysis['key_points']
                if isinstance(key_points, list):
                    summary_parts.append(f"Ключові моменти: {len(key_points)} пунктів")
        
        return " | ".join(summary_parts)
    
    async def search_in_pdfs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Пошук в завантажених PDF файлах"""
        try:
            # Пошук в векторній базі з фільтром по PDF
            all_results = vector_kb.search(query, top_k=limit * 2)
            
            # Фільтрація тільки PDF результатів
            pdf_results = []
            for result in all_results:
                if result['metadata'].get('source') == 'pdf':
                    pdf_results.append({
                        'text': result['text'][:300] + "..." if len(result['text']) > 300 else result['text'],
                        'filename': result['metadata'].get('filename', 'Unknown'),
                        'chunk_id': result['metadata'].get('chunk_id', 0),
                        'score': result['score']
                    })
                
                if len(pdf_results) >= limit:
                    break
            
            return pdf_results
            
        except Exception as e:
            logging.error(f"Помилка пошуку в PDF: {e}")
            return []
    
    def get_pdf_statistics(self) -> Dict[str, Any]:
        """Статистика завантажених PDF"""
        try:
            # Отримання всіх PDF документів з векторної бази
            all_docs = vector_kb.documents
            all_metadata = vector_kb.metadata
            
            pdf_files = set()
            pdf_chunks = 0
            
            for metadata in all_metadata:
                if metadata.get('source') == 'pdf':
                    pdf_chunks += 1
                    filename = metadata.get('filename')
                    if filename:
                        pdf_files.add(filename)
            
            return {
                'total_pdf_files': len(pdf_files),
                'total_pdf_chunks': pdf_chunks,
                'pdf_files': list(pdf_files)
            }
            
        except Exception as e:
            logging.error(f"Помилка отримання статистики PDF: {e}")
            return {'total_pdf_files': 0, 'total_pdf_chunks': 0, 'pdf_files': []}

# Глобальний екземпляр
pdf_processor = PDFProcessor()

async def process_pdf(file_path: str):
    """Функція для використання в main.py"""
    return await pdf_processor.process_pdf_file(file_path)

async def search_pdfs(query: str, limit: int = 5):
    """Пошук в PDF файлах"""
    return await pdf_processor.search_in_pdfs(query, limit)

def get_pdf_stats():
    """Статистика PDF"""
    return pdf_processor.get_pdf_statistics()

# Тестування
if __name__ == "__main__":
    async def test_pdf():
        # Тестування обробки PDF
        result = await process_pdf("test.pdf")
        print(f"Результат: {result}")
        
        # Тестування пошуку
        search_results = await search_pdfs("Python")
        print(f"Знайдено: {len(search_results)} результатів")
    
    asyncio.run(test_pdf())
