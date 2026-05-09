"""AI Engine for generating farming advice"""

import logging
import requests
import json
from typing import List, Dict

logger = logging.getLogger(__name__)


class AIEngine:
    """Manage AI model interactions via Ollama"""
    
    def __init__(self, config):
        """Initialize AI Engine
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')
        self.model = config.get('ai_model', 'phi3')
        self.test_connection()
    
    def test_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to Ollama")
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Cannot connect to Ollama: {e}")
    
    def generate_answer(self, question: str, context: str = "") -> str:
        """Generate answer using AI model
        
        Args:
            question: User's question
            context: Additional context from knowledge base
            
        Returns:
            Generated answer
        """
        try:
            # Build prompt with context
            prompt = self._build_prompt(question, context)
            
            logger.info(f"Generating answer for: {question}")
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_k": 40,
                    "top_p": 0.9
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                logger.info(f"Answer generated successfully")
                return answer
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return "Sorry, I couldn't generate an answer at this time."
                
        except requests.exceptions.Timeout:
            logger.error("Request to Ollama timed out")
            return "The model took too long to respond. Please try again."
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "An error occurred while generating the answer."
    
    def _build_prompt(self, question: str, context: str = "") -> str:
        """Build prompt for the AI model
        
        Args:
            question: User's question
            context: Additional context
            
        Returns:
            Formatted prompt
        """
        system_prompt = """You are an agricultural expert assistant helping Indian farmers with farming advice. 
Provide practical, actionable advice based on the question asked.
Be concise and use simple language that farmers can understand.
If unsure, ask clarifying questions or suggest consulting an agricultural expert."""
        
        if context:
            return f"""{system_prompt}

Context: {context}

Question: {question}

Answer:"""
        else:
            return f"""{system_prompt}

Question: {question}

Answer:"""
    
    def get_model_info(self) -> Dict:
        """Get information about the current model
        
        Returns:
            Model information dictionary
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/show", 
                                   params={"name": self.model})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
        return {}
