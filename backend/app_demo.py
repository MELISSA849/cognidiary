"""
"""SmartDiary - Minimal Working Server
Compatible with Python 3.14+ 
No NumPy/OpenCV dependencies for this demo version
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import json

app = Flask(__name__, static_folder='../frontend')
CORS(app)

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index_elegant.html')

@app.route('/style_elegant.css')
def serve_css():
    return send_from_directory(app.static_folder, 'style_elegant.css')

@app.route('/script_elegant.js')
def serve_js():
    return send_from_directory(app.static_folder, 'script_elegant.js')

@app.route('/api')
def api_info():
    return jsonify({
        'name': 'SmartDiary API - Demo Mode',
        'version': '2.0.0',
        'status': 'Running in compatibility mode (Python 3.14)',
        'note': 'Mood detection disabled due to NumPy/OpenCV compatibility issues with Python 3.14'
    })

@app.route('/detect_mood', methods=['POST'])
def detect_mood():
    # Simulated response since OpenCV isn't working
    return jsonify({
        'success': True,
        'mood': 'Happy',
        'confidence': 85.0,
        'emotions': {
            'happy': 85.0,
            'calm': 10.0,
            'neutral': 5.0
        },
        'note': 'Demo mode - mood detection simulated'
    })

@app.route('/save_entry', methods=['POST'])
def save_entry():
    try:
        data = request.get_json()
        
        # Create diary_entries directory if it doesn't exist
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        diary_dir = os.path.join(base_dir, 'diary_entries')
        os.makedirs(diary_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        filename = f"entry_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(diary_dir, filename)
        
        # Format entry
        entry_content = f"""{'='*60}
SMARTDIARY ENTRY
{'='*60}
Title: {data.get('title', 'Untitled')}
Date: {timestamp.strftime('%B %d, %Y at %I:%M %p')}
Mood: {data.get('mood', 'Not detected')}
{'='*60}

{data['text']}

{'='*60}
Entry saved automatically by SmartDiary
"""
        
        # Save entry
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(entry_content)
        
        return jsonify({
            'success': True,
            'message': 'Entry saved successfully',
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_entries', methods=['GET'])
def get_entries():
    try:
        import glob
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        diary_dir = os.path.join(base_dir, 'diary_entries')
        entries = []
        pattern = os.path.join(diary_dir, 'entry_*.txt')
        
        for filepath in sorted(glob.glob(pattern), reverse=True):
            filename = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries.append({
                'filename': filename,
                'preview': content[:200] + '...'
            })
        
        return jsonify({
            'success': True,
            'entries': entries,
            'count': len(entries)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0 (Compatibility Mode)',
        'python_version': '3.14+',
        'mode': 'demo'
    })

if __name__ == '__main__':
    os.makedirs('../diary_entries', exist_ok=True)
    
    print("=" * 70)
    print("CogniDiary Backend - Compatibility Mode")
    print("=" * 70)
    print("Server: http://localhost:5000")
    print("Note: Running in demo mode due to Python 3.14 compatibility issues")
    print("Mood detection is simulated - upgrade NumPy/OpenCV for full features")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
