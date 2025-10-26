"""
CogniDiary Backend API
Flask server with endpoints for speech-to-text, mood detection, and diary storage
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Import custom modules
from speech_recognition_module import SpeechRecognizer
from mood_detection_module import MoodDetector
from diary_storage import DiaryStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize modules
speech_recognizer = SpeechRecognizer()
mood_detector = MoodDetector()
diary_storage = DiaryStorage()

@app.route('/', methods=['GET'])
def home():
    """Home endpoint to check if server is running"""
    return jsonify({
        'message': 'CogniDiary Backend API is running!',
        'version': '1.0.0',
        'endpoints': [
            '/speech_to_text [POST]',
            '/detect_mood [POST]', 
            '/save_entry [POST]',
            '/get_entries [GET]'
        ]
    })

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    """Convert audio to text using speech recognition"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Process audio file
        logger.info("Processing audio for speech recognition...")
        text = speech_recognizer.recognize_audio(audio_file)
        
        if text:
            logger.info(f"Speech recognition successful: {text[:50]}...")
            return jsonify({
                'success': True,
                'text': text,
                'confidence': speech_recognizer.get_last_confidence()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not recognize speech in audio'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in speech recognition: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/detect_mood', methods=['POST'])
def detect_mood():
    """Detect mood from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            }), 400
        
        # Process image for mood detection
        logger.info("Processing image for mood detection...")
        mood_result = mood_detector.detect_mood(image_file)
        
        if mood_result['success']:
            logger.info(f"Mood detection successful: {mood_result['mood']}")
            return jsonify({
                'success': True,
                'mood': mood_result['mood'],
                'confidence': mood_result['confidence'],
                'emotions': mood_result.get('emotions', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': mood_result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error in mood detection: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/save_entry', methods=['POST'])
def save_entry():
    """Save diary entry to text file"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['title', 'text', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Save diary entry
        logger.info(f"Saving diary entry: {data['title']}")
        result = diary_storage.save_entry(
            title=data['title'],
            text=data['text'],
            mood=data.get('mood', 'Not detected'),
            timestamp=data['timestamp']
        )
        
        if result['success']:
            logger.info(f"Diary entry saved successfully: {result['filename']}")
            return jsonify({
                'success': True,
                'message': 'Diary entry saved successfully',
                'filename': result['filename']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error saving diary entry: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/get_entries', methods=['GET'])
def get_entries():
    """Get list of all diary entries"""
    try:
        entries = diary_storage.get_all_entries()
        return jsonify({
            'success': True,
            'entries': entries,
            'count': len(entries)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving entries: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'speech_recognition': speech_recognizer.is_available(),
            'mood_detection': mood_detector.is_available(),
            'diary_storage': diary_storage.is_available()
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('diary_entries', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    # Start the Flask development server
    logger.info("Starting CogniDiary Backend API...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )