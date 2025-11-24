"""
CogniDiary Backend API - Lightweight Standalone Version
Optimized Flask server with minimal dependencies
Efficient processing and browser-based features
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Import lightweight modules
from mood_detection_module_lite import MoodDetector
from speech_recognition_module_lite import SpeechRecognizer
from diary_storage import DiaryStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize modules (lazy loading for efficiency)
_mood_detector = None
_speech_recognizer = None
_diary_storage = None

def get_mood_detector():
    """Lazy load mood detector"""
    global _mood_detector
    if _mood_detector is None:
        _mood_detector = MoodDetector()
    return _mood_detector

def get_speech_recognizer():
    """Lazy load speech recognizer"""
    global _speech_recognizer
    if _speech_recognizer is None:
        _speech_recognizer = SpeechRecognizer()
    return _speech_recognizer

def get_diary_storage():
    """Lazy load diary storage"""
    global _diary_storage
    if _diary_storage is None:
        _diary_storage = DiaryStorage()
    return _diary_storage

@app.route('/', methods=['GET'])
def home():
    """Serve the frontend application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'CogniDiary API',
        'version': '2.0.0',
        'description': 'Lightweight standalone smart diary',
        'endpoints': [
            'GET / - Frontend application',
            'GET /api - API information',
            'POST /detect_mood - Mood detection from image',
            'POST /save_entry - Save diary entry',
            'GET /get_entries - Retrieve diary entries',
            'GET /health - Health check'
        ],
        'features': [
            'Browser-based speech recognition',
            'Lightweight mood detection',
            'Local file storage',
            'No heavy dependencies'
        ]
    })

@app.route('/detect_mood', methods=['POST'])
def detect_mood():
    """Detect mood from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
        logger.info("Processing image for mood detection...")
        mood_detector = get_mood_detector()
        mood_result = mood_detector.detect_mood(image_file)
        
        if mood_result['success']:
            logger.info(f"Mood detection successful: {mood_result['mood']}")
            return jsonify(mood_result)
        else:
            return jsonify(mood_result), 400
            
    except Exception as e:
        logger.error(f"Error in mood detection: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/save_entry', methods=['POST'])
def save_entry():
    """Save diary entry to text file"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required_fields = ['title', 'text', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        logger.info(f"Saving diary entry: {data['title']}")
        diary_storage = get_diary_storage()
        result = diary_storage.save_entry(
            title=data['title'],
            text=data['text'],
            mood=data.get('mood', 'Not detected'),
            timestamp=data['timestamp']
        )
        
        if result['success']:
            logger.info(f"Entry saved: {result['filename']}")
            return jsonify({'success': True, 'message': 'Entry saved', 'filename': result['filename']})
        else:
            return jsonify({'success': False, 'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Error saving entry: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/get_entries', methods=['GET'])
def get_entries():
    """Get all diary entries"""
    try:
        diary_storage = get_diary_storage()
        entries = diary_storage.get_all_entries()
        return jsonify({'success': True, 'entries': entries, 'count': len(entries)})
    except Exception as e:
        logger.error(f"Error retrieving entries: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'modules': {
            'mood_detection': 'available',
            'speech_recognition': 'browser-based',
            'diary_storage': 'available'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('../diary_entries', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    # Start server
    logger.info("=" * 60)
    logger.info("CogniDiary Backend API - Lightweight Edition")
    logger.info("=" * 60)
    logger.info("Server: http://localhost:5000")
    logger.info("API Info: http://localhost:5000/api")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
