"""Speech processing module for audio recording and conversion"""

import os
import logging
import whisper
import pyttsx3
import pyaudio
import wave
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeechProcessor:
    """Handle speech-to-text and text-to-speech conversion"""
    
    def __init__(self, config):
        """Initialize speech processor
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.audio_dir = Path(config.get('audio_dir', 'data/audio'))
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Whisper model
        self.whisper_model = None
        self.tts_engine = None
        self.setup_models()
    
    def setup_models(self):
        """Setup speech models"""
        try:
            logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("tiny")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
        
        try:
            logger.info("Initializing TTS engine...")
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
    
    def record_audio(self, duration=10, sample_rate=16000):
        """Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            
        Returns:
            Path to recorded audio file
        """
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            chunk = 1024
            channels = 1
            format = pyaudio.paFloat32
            
            p = pyaudio.PyAudio()
            stream = p.open(format=format, channels=channels, 
                          rate=sample_rate, input=True, 
                          frames_per_buffer=chunk)
            
            frames = []
            for _ in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save audio file
            audio_file = self.audio_dir / f"audio_{os.urandom(4).hex()}.wav"
            with wave.open(str(audio_file), 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(format))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"Audio recorded: {audio_file}")
            return str(audio_file)
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    def speech_to_text(self, audio_file):
        """Convert speech to text using Whisper
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            if not self.whisper_model:
                logger.error("Whisper model not loaded")
                return None
            
            logger.info(f"Transcribing audio: {audio_file}")
            result = self.whisper_model.transcribe(audio_file, language="en")
            text = result["text"].strip()
            
            logger.info(f"Transcription: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def text_to_speech(self, text):
        """Convert text to speech
        
        Args:
            text: Text to convert
        """
        try:
            if not self.tts_engine:
                logger.error("TTS engine not initialized")
                return
            
            logger.info(f"Converting to speech: {text[:50]}...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info("Speech generation completed")
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    def cleanup(self):
        """Cleanup speech resources"""
        if self.tts_engine:
            self.tts_engine.stop()
