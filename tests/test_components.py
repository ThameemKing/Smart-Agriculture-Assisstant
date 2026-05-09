"""
Component Tests for Farmer Assistant
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.core.knowledge_base import KnowledgeBase
from src.core.ai_engine import AIEngine


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.config = Config()
    
    def test_config_initialization(self):
        """Test config loads defaults"""
        self.assertIsNotNone(self.config.get('ollama_url'))
        self.assertIsNotNone(self.config.get('ai_model'))
    
    def test_config_get_value(self):
        """Test getting config values"""
        value = self.config.get('button_pin')
        self.assertEqual(value, 17)
    
    def test_config_set_value(self):
        """Test setting config values"""
        self.config.set('test_key', 'test_value')
        self.assertEqual(self.config.get('test_key'), 'test_value')
    
    def test_config_default_fallback(self):
        """Test default fallback"""
        value = self.config.get('non_existent_key', 'default')
        self.assertEqual(value, 'default')


class TestKnowledgeBase(unittest.TestCase):
    """Test knowledge base functionality"""
    
    def setUp(self):
        self.config = Config()
        self.kb = KnowledgeBase(self.config)
    
    def test_kb_initialization(self):
        """Test knowledge base loads documents"""
        self.assertGreater(len(self.kb.documents), 0)
    
    def test_kb_search_tomato(self):
        """Test searching for tomato advice"""
        results = self.kb.search("tomato leaves yellow")
        self.assertGreater(len(results), 0)
        self.assertIn("tomato", results.lower())
    
    def test_kb_search_rice(self):
        """Test searching for rice advice"""
        results = self.kb.search("rice fertilizer")
        self.assertGreater(len(results), 0)
    
    def test_kb_add_document(self):
        """Test adding new document"""
        initial_count = len(self.kb.documents)
        self.kb.add_document(
            topic="Test Crop",
            content="Test farming advice",
            keywords=["test"]
        )
        self.assertEqual(len(self.kb.documents), initial_count + 1)


class TestAIEngine(unittest.TestCase):
    """Test AI Engine"""
    
    def setUp(self):
        self.config = Config()
        self.ai = AIEngine(self.config)
    
    def test_ai_initialization(self):
        """Test AI engine initializes"""
        self.assertIsNotNone(self.ai.ollama_url)
        self.assertIsNotNone(self.ai.model)
    
    def test_prompt_building(self):
        """Test prompt construction"""
        prompt = self.ai._build_prompt(
            question="How to grow tomatoes?",
            context="Tomato is a common crop"
        )
        self.assertIn("How to grow tomatoes?", prompt)
        self.assertIn("Tomato is a common crop", prompt)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.config = Config()
        self.kb = KnowledgeBase(self.config)
        self.ai = AIEngine(self.config)
    
    def test_question_search_flow(self):
        """Test question → search → context flow"""
        question = "What about tomato?"
        context = self.kb.search(question)
        self.assertGreater(len(context), 0)
    
    def test_prompt_construction_flow(self):
        """Test full prompt construction"""
        question = "How to grow better tomatoes?"
        context = self.kb.search(question)
        prompt = self.ai._build_prompt(question, context)
        self.assertIn(question, prompt)


if __name__ == '__main__':
    unittest.main()
