#!/usr/bin/env python3
"""
Farmer Assistant - IoT-Based Offline Agricultural Advisory System
Main entry point for the application
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('farmer_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from src.core.speech_processor import SpeechProcessor
from src.core.ai_engine import AIEngine
from src.core.knowledge_base import KnowledgeBase
from src.hardware.gpio_interface import GPIOInterface
from src.hardware.lcd_display import LCDDisplay
from src.utils.config import Config
from src.utils.logger import setup_logger


class FarmerAssistant:
    """Main Farmer Assistant Application"""
    
    def __init__(self):
        """Initialize Farmer Assistant"""
        logger.info("Initializing Farmer Assistant...")
        
        self.config = Config()
        self.speech_processor = SpeechProcessor(self.config)
        self.ai_engine = AIEngine(self.config)
        self.knowledge_base = KnowledgeBase(self.config)
        
        # Hardware initialization (optional for non-Pi systems)
        try:
            self.gpio = GPIOInterface(self.config)
            self.lcd = LCDDisplay(self.config)
            self.hardware_available = True
            logger.info("Hardware initialized successfully")
        except Exception as e:
            logger.warning(f"Hardware not available: {e}. Running in software mode.")
            self.hardware_available = False
            self.gpio = None
            self.lcd = None
    
    def display_message(self, message, duration=2):
        """Display message on LCD or console"""
        if self.hardware_available and self.lcd:
            self.lcd.display(message)
        else:
            print(f"[DISPLAY] {message}")
    
    def wait_for_button_press(self):
        """Wait for button press"""
        if self.hardware_available and self.gpio:
            logger.info("Waiting for button press...")
            self.display_message("Press button!")
            self.gpio.wait_for_button()
        else:
            print("\nPress ENTER to continue (simulating button press)...")
            input()
    
    def process_question(self, audio_file=None):
        """Process user question from speech"""
        try:
            # Capture or use provided audio
            if audio_file is None:
                self.display_message("Listening...")
                logger.info("Capturing audio...")
                audio_file = self.speech_processor.record_audio()
            
            # Convert speech to text
            logger.info("Converting speech to text...")
            question = self.speech_processor.speech_to_text(audio_file)
            logger.info(f"Question: {question}")
            
            if not question:
                self.display_message("Sorry, no audio detected!")
                return
            
            # Search knowledge base
            self.display_message("Searching...")
            logger.info("Searching knowledge base...")
            context = self.knowledge_base.search(question)
            
            # Generate answer using AI
            self.display_message("Thinking...")
            logger.info("Generating answer...")
            answer = self.ai_engine.generate_answer(question, context)
            logger.info(f"Answer: {answer}")
            
            # Convert answer to speech
            self.display_message("Speaking...")
            logger.info("Converting answer to speech...")
            self.speech_processor.text_to_speech(answer)
            
            # Display completion
            self.display_message("Done!")
            logger.info("Question processing completed")
            
            return {
                'question': question,
                'answer': answer,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            self.display_message("Error occurred!")
            return None
    
    def run_demo_mode(self):
        """Run demo with sample questions"""
        demo_questions = [
            "My tomato leaves are turning yellow",
            "What fertilizer is good for rice?",
            "How to control pests in cotton?",
            "How to save water in my farm?",
            "When should I sow wheat?"
        ]
        
        logger.info("Running in DEMO mode")
        self.display_message("Demo Mode")
        
        for idx, question in enumerate(demo_questions, 1):
            logger.info(f"Demo Question {idx}: {question}")
            print(f"\n[DEMO {idx}] {question}")
            
            # Simulate processing
            context = self.knowledge_base.search(question)
            answer = self.ai_engine.generate_answer(question, context)
            
            print(f"[ANSWER] {answer}\n")
            logger.info(f"Demo answer provided")
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        logger.info("Starting interactive mode...")
        self.display_message("Ready!", 1)
        
        while True:
            self.wait_for_button_press()
            result = self.process_question()
            
            if result:
                logger.info(f"Successfully processed question: {result['question']}")
            
            # Ask if user wants to continue
            if not self.hardware_available:
                cont = input("\nContinue? (y/n): ").lower()
                if cont != 'y':
                    break
    
    def run_api_mode(self):
        """Run as API server for testing"""
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'healthy'})
        
        @app.route('/process', methods=['POST'])
        def process():
            data = request.json
            question = data.get('question', '')
            
            if not question:
                return jsonify({'error': 'No question provided'}), 400
            
            context = self.knowledge_base.search(question)
            answer = self.ai_engine.generate_answer(question, context)
            
            return jsonify({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
        
        logger.info("Starting API server on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    def run(self, mode='interactive'):
        """Main run method"""
        try:
            logger.info(f"Starting Farmer Assistant in {mode} mode")
            self.display_message(f"Farmer Assistant")
            
            if mode == 'demo':
                self.run_demo_mode()
            elif mode == 'api':
                self.run_api_mode()
            else:
                self.run_interactive_mode()
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            self.display_message("Shutting down...")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self.display_message("Error!")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        if self.hardware_available:
            if self.gpio:
                self.gpio.cleanup()
            if self.lcd:
                self.lcd.cleanup()
        logger.info("Farmer Assistant stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Farmer Assistant - IoT Agricultural Advisory System')
    parser.add_argument('--mode', choices=['interactive', 'demo', 'api'], 
                       default='interactive', help='Operation mode')
    parser.add_argument('--question', type=str, help='Process a single question')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    app = FarmerAssistant()
    
    if args.question:
        print(f"Question: {args.question}")
        # Simple text-based question processing
        context = app.knowledge_base.search(args.question)
        answer = app.ai_engine.generate_answer(args.question, context)
        print(f"Answer: {answer}")
    else:
        app.run(mode=args.mode)


if __name__ == '__main__':
    main()
