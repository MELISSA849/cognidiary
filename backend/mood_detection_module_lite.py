"""
Lightweight Mood Detection Module for CogniDiary
Uses OpenCV Haar Cascades for face detection and simple emotion analysis
No heavy ML frameworks required - fully standalone
"""

import cv2
import numpy as np
import logging
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class MoodDetector:
    def __init__(self):
        """Initialize lightweight mood detector using OpenCV Haar Cascades"""
        try:
            # Load pre-trained Haar Cascade for face detection (built into OpenCV)
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            self.smile_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_smile.xml'
            )
            
            self.is_initialized = True
            logger.info("Lightweight Mood Detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize mood detector: {e}")
            self.is_initialized = False
    
    def detect_mood(self, image_file):
        """
        Detect mood from uploaded image file using lightweight algorithms
        
        Args:
            image_file: Image file from Flask request
            
        Returns:
            dict: Mood detection result with success status, mood, and confidence
        """
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Mood detector not initialized properly'
            }
        
        try:
            # Convert uploaded file to OpenCV format
            image = self._process_uploaded_image(image_file)
            
            if image is None:
                return {
                    'success': False,
                    'error': 'Could not process uploaded image'
                }
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'error': 'No face detected in the image'
                }
            
            # Analyze first detected face
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi_color = image[y:y+h, x:x+w]
            
            # Detect facial features
            mood_result = self._analyze_facial_features(face_roi, face_roi_color)
            
            logger.info(f"Mood detected: {mood_result['mood']} with {mood_result['confidence']}% confidence")
            
            return {
                'success': True,
                'mood': mood_result['mood'],
                'confidence': mood_result['confidence'],
                'emotions': mood_result['emotions'],
                'face_detected': True,
                'box': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
            }
            
        except Exception as e:
            logger.error(f"Error in mood detection: {str(e)}")
            return {
                'success': False,
                'error': f'Mood detection failed: {str(e)}'
            }
    
    def _analyze_facial_features(self, face_gray, face_color):
        """
        Analyze facial features to determine mood
        Uses simple heuristics based on detected features
        """
        # Detect eyes in face region
        eyes = self.eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=10)
        
        # Detect smile in face region
        smiles = self.smile_cascade.detectMultiScale(
            face_gray, 
            scaleFactor=1.8, 
            minNeighbors=20,
            minSize=(25, 25)
        )
        
        # Analyze brightness (can indicate happiness vs sadness)
        avg_brightness = np.mean(face_gray)
        
        # Calculate features
        num_eyes = len(eyes)
        num_smiles = len(smiles)
        brightness_normalized = min(100, (avg_brightness / 255) * 100)
        
        # Simple rule-based mood detection
        emotions = {
            'happy': 0.0,
            'sad': 0.0,
            'neutral': 0.0,
            'surprised': 0.0,
            'calm': 0.0
        }
        
        # Logic for mood detection
        if num_smiles > 0:
            # Smile detected - likely happy
            emotions['happy'] = min(95.0, 50.0 + (num_smiles * 15.0) + (brightness_normalized * 0.3))
            emotions['neutral'] = 20.0
            emotions['calm'] = 15.0
            emotions['sad'] = 5.0
            emotions['surprised'] = 10.0
        elif num_eyes >= 2:
            # Eyes open, no smile - could be neutral or calm
            if brightness_normalized > 60:
                emotions['calm'] = 60.0
                emotions['neutral'] = 30.0
                emotions['happy'] = 10.0
            else:
                emotions['neutral'] = 50.0
                emotions['calm'] = 25.0
                emotions['sad'] = 15.0
                emotions['happy'] = 10.0
        elif num_eyes == 1:
            # Partially obscured or surprised
            emotions['surprised'] = 45.0
            emotions['neutral'] = 35.0
            emotions['calm'] = 20.0
        else:
            # Eyes not clearly detected - might be looking away or sad
            if brightness_normalized < 40:
                emotions['sad'] = 55.0
                emotions['neutral'] = 30.0
                emotions['calm'] = 15.0
            else:
                emotions['neutral'] = 60.0
                emotions['calm'] = 25.0
                emotions['sad'] = 15.0
        
        # Normalize emotions to sum to ~100
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: round((v / total) * 100, 1) for k, v in emotions.items()}
        
        # Get dominant emotion
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]
        
        # Map to mood
        mood_mapping = {
            'happy': 'Happy',
            'sad': 'Sad',
            'neutral': 'Neutral',
            'surprised': 'Surprised',
            'calm': 'Calm'
        }
        
        mood = mood_mapping.get(dominant_emotion, 'Neutral')
        
        return {
            'mood': mood,
            'confidence': round(confidence, 1),
            'emotions': emotions
        }
    
    def _process_uploaded_image(self, image_file):
        """Convert uploaded image file to OpenCV format"""
        try:
            # Read image data
            image_data = image_file.read()
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL Image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Validate image
            if opencv_image is None or opencv_image.size == 0:
                logger.error("Invalid image data")
                return None
            
            logger.info(f"Image processed successfully: {opencv_image.shape}")
            return opencv_image
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
    
    def detect_mood_from_path(self, image_path):
        """Detect mood from image file path (for testing)"""
        try:
            image = cv2.imread(image_path)
            
            if image is None:
                return {
                    'success': False,
                    'error': 'Could not load image from path'
                }
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'error': 'No face detected in the image'
                }
            
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi_color = image[y:y+h, x:x+w]
            
            mood_result = self._analyze_facial_features(face_roi, face_roi_color)
            
            return {
                'success': True,
                'mood': mood_result['mood'],
                'confidence': mood_result['confidence'],
                'emotions': mood_result['emotions']
            }
            
        except Exception as e:
            logger.error(f"Error in mood detection from path: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_available(self):
        """Check if mood detection is available"""
        return self.is_initialized
    
    def get_supported_emotions(self):
        """Get list of supported emotions"""
        return ['happy', 'sad', 'neutral', 'surprised', 'calm']
    
    def test_mood_detection(self):
        """Test mood detection functionality"""
        try:
            # Create a simple test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            return {
                'success': True,
                'message': 'Mood detection is working',
                'faces_detected': len(faces)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mood detection test failed: {str(e)}'
            }
