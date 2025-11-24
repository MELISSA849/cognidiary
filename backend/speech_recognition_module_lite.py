"""
Lightweight Speech Recognition Module for CogniDiary
Primarily relies on browser-based speech recognition
Minimal server-side processing for efficiency
"""

import logging
import os
import tempfile

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self):
        """Initialize lightweight speech recognizer"""
        self.last_confidence = 0.0
        logger.info("Lightweight Speech Recognizer initialized (uses browser APIs)")
    
    def recognize_audio(self, audio_file):
        """
        Process audio file - primarily for fallback support
        Main speech recognition happens in browser
        
        Args:
            audio_file: Audio file from Flask request
            
        Returns:
            str: Status message (actual recognition done client-side)
        """
        try:
            # For this lightweight version, we inform that browser should handle it
            # This is a placeholder for compatibility
            logger.info("Audio received - recommend using browser speech recognition for best results")
            
            # Save file temporarily for logging
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                audio_file.save(temp_file.name)
                file_size = os.path.getsize(temp_file.name)
                logger.info(f"Audio file saved: {file_size} bytes")
                os.unlink(temp_file.name)
            
            self.last_confidence = 0.0
            
            return None  # Signal to use browser-based recognition
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return None
    
    def get_last_confidence(self):
        """Get confidence score of last recognition"""
        return self.last_confidence
    
    def is_available(self):
        """Check if speech recognition is available"""
        # Always available since it uses browser APIs
        return True
    
    def get_supported_languages(self):
        """Get list of supported languages (browser dependent)"""
        return {
            'en-US': 'English (US)',
            'en-GB': 'English (UK)',
            'en-IN': 'English (India)',
            'hi-IN': 'Hindi (India)',
            'es-ES': 'Spanish (Spain)',
            'fr-FR': 'French (France)',
            'de-DE': 'German (Germany)',
            'ja-JP': 'Japanese (Japan)',
            'ko-KR': 'Korean (South Korea)',
            'zh-CN': 'Chinese (Simplified)',
            'it-IT': 'Italian (Italy)',
            'pt-BR': 'Portuguese (Brazil)',
            'ru-RU': 'Russian (Russia)',
            'ar-SA': 'Arabic (Saudi Arabia)'
        }
