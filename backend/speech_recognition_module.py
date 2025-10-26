"""
Speech Recognition Module for CogniDiary
Handles audio processing and speech-to-text conversion
"""

import speech_recognition as sr
import os
import tempfile
import logging
import shutil
from pydub import AudioSegment
from pydub.utils import which
import io

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self):
        """Initialize the speech recognizer with Google Speech Recognition"""
        self.recognizer = sr.Recognizer()
        self.last_confidence = 0.0
        
        # Adjust for ambient noise (optional)
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
        logger.info("Speech Recognizer initialized")
    
    def recognize_audio(self, audio_file):
        """
        Convert audio file to text using Google Speech Recognition
        
        Args:
            audio_file: Audio file from Flask request
            
        Returns:
            str: Recognized text or None if recognition fails
        """
        temp_filename = None
        wav_filename = None
        
        try:
            # Save uploaded file temporarily with original extension
            file_extension = '.webm'  # Default to webm for browser recordings
            if hasattr(audio_file, 'filename') and audio_file.filename:
                if '.' in audio_file.filename:
                    file_extension = '.' + audio_file.filename.rsplit('.', 1)[1].lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                audio_file.save(temp_file.name)
                temp_filename = temp_file.name
                
            logger.info(f"Saved audio file: {temp_filename}")
            
            # Convert audio to WAV format
            wav_filename = self._convert_to_wav(temp_filename)
            
            if not wav_filename or not os.path.exists(wav_filename):
                logger.error("Failed to convert audio to WAV format")
                return None
            
            # Load audio file for recognition
            with sr.AudioFile(wav_filename) as source:
                logger.info("Loading audio file for recognition...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio data
                audio_data = self.recognizer.record(source)
                logger.info("Audio data recorded successfully")
            
            # Perform speech recognition
            try:
                # Try English first, then Hindi
                languages = ['en-US', 'hi-IN', 'en-IN']
                
                for lang in languages:
                    try:
                        logger.info(f"Trying speech recognition with language: {lang}")
                        text = self.recognizer.recognize_google(
                            audio_data, 
                            language=lang,
                            show_all=False
                        )
                        
                        if text and text.strip():
                            logger.info(f"Speech recognition successful ({lang}): {text[:50]}...")
                            self.last_confidence = 0.95
                            return text.strip()
                            
                    except sr.UnknownValueError:
                        logger.warning(f"Could not understand audio with language {lang}")
                        continue
                    except sr.RequestError as e:
                        logger.error(f"Recognition service error with {lang}: {e}")
                        continue
                
                # If all languages failed, try offline recognition
                logger.info("Trying offline speech recognition...")
                return self._try_offline_recognition(audio_data)
                
            except Exception as e:
                logger.error(f"Speech recognition error: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error in speech recognition: {str(e)}")
            return None
        
        finally:
            # Clean up temporary files
            self._cleanup_temp_files([temp_filename, wav_filename])
    
    def _convert_to_wav(self, input_filename):
        """Convert audio file to WAV format"""
        try:
            logger.info(f"Converting audio file: {input_filename}")
            
            # Try to load audio file - pydub can handle WebM, MP4, etc.
            if input_filename.lower().endswith('.webm'):
                # For WebM files, specify codec
                audio = AudioSegment.from_file(input_filename, format="webm")
            else:
                # Let pydub auto-detect format
                audio = AudioSegment.from_file(input_filename)
            
            logger.info(f"Audio loaded: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
            
            # Convert to WAV with proper settings for speech recognition
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            # Create WAV filename
            base_name = os.path.splitext(input_filename)[0]
            wav_filename = base_name + '_converted.wav'
            
            # Export as WAV
            audio.export(wav_filename, format="wav")
            
            logger.info(f"Audio converted to WAV: {wav_filename}")
            return wav_filename
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            
            # Fallback: try to use the original file
            try:
                if not input_filename.lower().endswith('.wav'):
                    # Create a copy with .wav extension
                    wav_filename = input_filename + '.wav'
                    import shutil
                    shutil.copy2(input_filename, wav_filename)
                    logger.info(f"Created WAV copy: {wav_filename}")
                    return wav_filename
                else:
                    return input_filename
                    
            except Exception as e2:
                logger.error(f"Could not prepare audio file: {e2}")
                return None
    
    def _try_alternative_recognition(self, audio_data):
        """Try alternative speech recognition methods"""
        try:
            # Try with different language settings
            languages = ['en-US', 'hi-IN', 'en-IN']
            
            for lang in languages:
                try:
                    text = self.recognizer.recognize_google(audio_data, language=lang)
                    logger.info(f"Alternative recognition successful with {lang}")
                    self.last_confidence = 0.85
                    return text
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Alternative recognition failed: {e}")
            return None
    
    def _try_offline_recognition(self, audio_data):
        """Try offline speech recognition as fallback"""
        try:
            # Try Sphinx (offline recognition)
            text = self.recognizer.recognize_sphinx(audio_data)
            logger.info("Offline recognition successful")
            self.last_confidence = 0.70
            return text
            
        except sr.UnknownValueError:
            logger.warning("Offline speech recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Offline speech recognition error: {e}")
            return None
    
    def _cleanup_temp_files(self, filenames):
        """Clean up temporary files"""
        for filename in filenames:
            try:
                if filename and os.path.exists(filename):
                    os.unlink(filename)
            except Exception as e:
                logger.warning(f"Could not delete temp file {filename}: {e}")
    
    def get_last_confidence(self):
        """Get confidence score of last recognition"""
        return self.last_confidence
    
    def is_available(self):
        """Check if speech recognition is available"""
        try:
            # Test with a short silence
            with sr.Microphone() as source:
                pass
            return True
        except:
            try:
                # Check if we can at least do file-based recognition
                temp_recognizer = sr.Recognizer()
                return True
            except:
                return False
    
    def set_language(self, language_code):
        """Set the language for speech recognition"""
        self.language = language_code
        logger.info(f"Speech recognition language set to: {language_code}")
    
    def adjust_for_noise(self, noise_duration=1.0):
        """Adjust recognizer settings for noisy environments"""
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 1.0
        logger.info("Adjusted settings for noisy environment")
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return {
            'en-US': 'English (US)',
            'en-IN': 'English (India)', 
            'hi-IN': 'Hindi (India)',
            'es-ES': 'Spanish (Spain)',
            'fr-FR': 'French (France)',
            'de-DE': 'German (Germany)',
            'ja-JP': 'Japanese (Japan)',
            'ko-KR': 'Korean (South Korea)',
            'zh-CN': 'Chinese (Simplified)'
        }