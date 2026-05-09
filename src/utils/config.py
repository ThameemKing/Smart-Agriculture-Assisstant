"""Configuration management"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration management"""
    
    DEFAULT_CONFIG = {
        # Ollama
        'ollama_url': 'http://localhost:11434',
        'ai_model': 'phi3',
        
        # Hardware
        'button_pin': 17,
        'debounce_time': 0.2,
        'lcd_address': 0x27,
        'lcd_cols': 16,
        'lcd_rows': 2,
        
        # Directories
        'audio_dir': 'data/audio',
        'kb_dir': 'data/knowledge_base',
        'log_dir': 'logs',
        
        # Speech
        'sample_rate': 16000,
        'record_duration': 10,
        
        # AI
        'temperature': 0.7,
        'top_k': 40,
        'top_p': 0.9,
        'kb_search_results': 3,
        'similarity_threshold': 0.1,
    }
    
    def __init__(self, config_file=None):
        """Initialize configuration
        
        Args:
            config_file: Path to JSON config file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from config file
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Ollama settings
        if os.getenv('OLLAMA_URL'):
            self.config['ollama_url'] = os.getenv('OLLAMA_URL')
        if os.getenv('AI_MODEL'):
            self.config['ai_model'] = os.getenv('AI_MODEL')
        
        # Hardware settings
        if os.getenv('BUTTON_PIN'):
            self.config['button_pin'] = int(os.getenv('BUTTON_PIN'))
        if os.getenv('LCD_ADDRESS'):
            self.config['lcd_address'] = int(os.getenv('LCD_ADDRESS'), 16)
    
    def _load_from_file(self, config_file):
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            self.config.update(file_config)
    
    def get(self, key, default=None):
        """Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def to_dict(self):
        """Return configuration as dictionary"""
        return self.config.copy()
