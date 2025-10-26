"""
Mood Detection Module for CogniDiary
Handles facial emotion recognition and mood analysis
"""

import cv2
import numpy as np
import logging
from fer import FER
import tempfile
import os
from PIL import Image
import io

logger = logging.getLogger(__name__)

class MoodDetector:
    def __init__(self):
        """Initialize the mood detector with FER (Facial Emotion Recognition)"""
        try:
            # Initialize the emotion detector without MTCNN to avoid TensorFlow issues
            self.emotion_detector = FER(mtcnn=False)
            self.is_initialized = True
            logger.info("Mood Detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize mood detector: {e}")
            self.is_initialized = False
            
        # Emotion to mood mapping
        self.emotion_to_mood = {
            'happy': 'Happy',
            'sad': 'Sad', 
            'angry': 'Angry',
            'fear': 'Anxious',
            'surprise': 'Surprised',
            'disgust': 'Disgusted',
            'neutral': 'Calm'
        }
        
        # Confidence threshold for mood detection
        self.confidence_threshold = 0.3
    
    def detect_mood(self, image_file):
        """
        Detect mood from uploaded image file
        
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
            
            # Detect emotions in the image
            emotions = self.emotion_detector.detect_emotions(image)
            
            if not emotions:
                return {
                    'success': False,
                    'error': 'No face detected in the image'
                }
            
            # Get the dominant emotion from the first detected face
            dominant_emotion_data = emotions[0]
            emotions_dict = dominant_emotion_data['emotions']
            
            # Find the emotion with highest confidence
            dominant_emotion = max(emotions_dict, key=emotions_dict.get)
            confidence = emotions_dict[dominant_emotion]
            
            # Convert confidence to percentage
            confidence_percent = round(confidence * 100, 1)
            
            # Check if confidence is above threshold
            if confidence < self.confidence_threshold:
                return {
                    'success': False,
                    'error': f'Low confidence in emotion detection ({confidence_percent}%)'
                }
            
            # Map emotion to mood
            mood = self.emotion_to_mood.get(dominant_emotion, 'Unknown')
            
            logger.info(f"Mood detected: {mood} with {confidence_percent}% confidence")
            
            return {
                'success': True,
                'mood': mood,
                'confidence': confidence_percent,
                'emotions': {k: round(v * 100, 1) for k, v in emotions_dict.items()},
                'face_detected': True,
                'box': dominant_emotion_data['box']  # Face bounding box coordinates
            }
            
        except Exception as e:
            logger.error(f"Error in mood detection: {str(e)}")
            return {
                'success': False,
                'error': f'Mood detection failed: {str(e)}'
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
        """
        Detect mood from image file path (for testing)
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Mood detection result
        """
        try:
            image = cv2.imread(image_path)
            
            if image is None:
                return {
                    'success': False,
                    'error': 'Could not load image from path'
                }
            
            # Detect emotions
            emotions = self.emotion_detector.detect_emotions(image)
            
            if not emotions:
                return {
                    'success': False,
                    'error': 'No face detected in the image'
                }
            
            # Process results similar to detect_mood method
            dominant_emotion_data = emotions[0]
            emotions_dict = dominant_emotion_data['emotions']
            dominant_emotion = max(emotions_dict, key=emotions_dict.get)
            confidence = emotions_dict[dominant_emotion]
            
            mood = self.emotion_to_mood.get(dominant_emotion, 'Unknown')
            
            return {
                'success': True,
                'mood': mood,
                'confidence': round(confidence * 100, 1),
                'emotions': {k: round(v * 100, 1) for k, v in emotions_dict.items()}
            }
            
        except Exception as e:
            logger.error(f"Error in mood detection from path: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_multiple_faces(self, image_file):
        """
        Analyze mood for multiple faces in an image
        
        Args:
            image_file: Image file from Flask request
            
        Returns:
            dict: Results for all detected faces
        """
        try:
            image = self._process_uploaded_image(image_file)
            
            if image is None:
                return {
                    'success': False,
                    'error': 'Could not process uploaded image'
                }
            
            emotions = self.emotion_detector.detect_emotions(image)
            
            if not emotions:
                return {
                    'success': False,
                    'error': 'No faces detected in the image'
                }
            
            # Process all detected faces
            face_results = []
            for i, face_data in enumerate(emotions):
                emotions_dict = face_data['emotions']
                dominant_emotion = max(emotions_dict, key=emotions_dict.get)
                confidence = emotions_dict[dominant_emotion]
                mood = self.emotion_to_mood.get(dominant_emotion, 'Unknown')
                
                face_results.append({
                    'face_id': i + 1,
                    'mood': mood,
                    'confidence': round(confidence * 100, 1),
                    'emotions': {k: round(v * 100, 1) for k, v in emotions_dict.items()},
                    'box': face_data['box']
                })
            
            return {
                'success': True,
                'faces_count': len(face_results),
                'faces': face_results
            }
            
        except Exception as e:
            logger.error(f"Error in multiple face analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_mood_statistics(self, moods_list):
        """
        Analyze mood patterns from a list of detected moods
        
        Args:
            moods_list: List of mood strings
            
        Returns:
            dict: Mood statistics and patterns
        """
        try:
            if not moods_list:
                return {
                    'success': False,
                    'error': 'No moods provided'
                }
            
            # Count mood frequencies
            mood_counts = {}
            for mood in moods_list:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Calculate percentages
            total_moods = len(moods_list)
            mood_percentages = {mood: (count / total_moods) * 100 
                              for mood, count in mood_counts.items()}
            
            # Find dominant mood
            dominant_mood = max(mood_counts, key=mood_counts.get)
            
            return {
                'success': True,
                'total_entries': total_moods,
                'mood_counts': mood_counts,
                'mood_percentages': {k: round(v, 1) for k, v in mood_percentages.items()},
                'dominant_mood': dominant_mood,
                'mood_variety': len(mood_counts)
            }
            
        except Exception as e:
            logger.error(f"Error in mood statistics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_available(self):
        """Check if mood detection is available"""
        return self.is_initialized
    
    def get_supported_emotions(self):
        """Get list of supported emotions"""
        return list(self.emotion_to_mood.keys())
    
    def set_confidence_threshold(self, threshold):
        """Set minimum confidence threshold for mood detection"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            logger.info(f"Confidence threshold set to: {threshold}")
        else:
            logger.warning("Invalid confidence threshold. Must be between 0.0 and 1.0")
    
    def test_mood_detection(self):
        """Test mood detection functionality"""
        try:
            # Create a simple test image (just for testing availability)
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            emotions = self.emotion_detector.detect_emotions(test_image)
            
            return {
                'success': True,
                'message': 'Mood detection is working',
                'faces_detected': len(emotions) if emotions else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mood detection test failed: {str(e)}'
            }