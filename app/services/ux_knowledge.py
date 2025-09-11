"""
UX Knowledge Base Service
Handles extraction and processing of UX knowledge from PDF files
"""

import os
import PyPDF2
from typing import List, Dict, Any
from pathlib import Path

class UXKnowledgeService:
    """Service for managing UX knowledge base"""
    
    def __init__(self, resources_path: str = "Resources"):
        self.resources_path = Path(resources_path)
        self.knowledge_base = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load knowledge from PDF files in the resources directory"""
        if not self.resources_path.exists():
            print(f"Warning: Resources directory {self.resources_path} not found")
            return
        
        for pdf_file in self.resources_path.glob("*.pdf"):
            try:
                content = self._extract_pdf_content(pdf_file)
                self.knowledge_base[pdf_file.stem] = {
                    "title": pdf_file.stem,
                    "content": content,
                    "type": "pdf"
                }
                print(f"Loaded knowledge: {pdf_file.stem}")
            except Exception as e:
                print(f"Error loading {pdf_file}: {e}")
    
    def _extract_pdf_content(self, pdf_path: Path) -> str:
        """Extract text content from PDF file"""
        content = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF content: {e}")
            content = f"Error reading PDF: {pdf_path.name}"
        
        return content.strip()
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of available knowledge"""
        return {
            "total_documents": len(self.knowledge_base),
            "documents": list(self.knowledge_base.keys()),
            "types": list(set(doc["type"] for doc in self.knowledge_base.values()))
        }
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search through the knowledge base"""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc_data in self.knowledge_base.items():
            content_lower = doc_data["content"].lower()
            if query_lower in content_lower:
                # Simple relevance scoring
                relevance = content_lower.count(query_lower)
                results.append({
                    "document": doc_id,
                    "title": doc_data["title"],
                    "relevance": relevance,
                    "preview": doc_data["content"][:200] + "..." if len(doc_data["content"]) > 200 else doc_data["content"]
                })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
    
    def get_document_content(self, document_id: str) -> str:
        """Get full content of a specific document"""
        return self.knowledge_base.get(document_id, {}).get("content", "")
