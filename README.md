# 📝 SmartDiary - Intelligent Diary Application

SmartDiary is an intelligent diary application that combines speech-to-text functionality with mood detection through facial recognition. Users can create diary entries using voice input, and the application automatically detects their mood through camera analysis.

## ✨ Features

- **🎤 Speech-to-Text**: Browser-based speech recognition for instant text conversion
- **📷 Mood Detection**: AI-powered facial emotion analysis to detect current mood
- **📝 Smart Diary Entries**: Save entries with timestamps, titles, and detected moods
- **💾 Text File Storage**: All entries are saved as readable .txt files with structured format
- **🌐 Web Interface**: Modern, responsive web application with beautiful UI
- **🔍 Search & Filter**: Find entries by mood, date, or content
- **🌍 Multi-language Support**: Supports English and Hindi speech recognition
- **⚡ Real-time Processing**: Instant mood detection and speech-to-text conversion

## 🏗️ Project Structure

```
smartdiary/
├── frontend/                 # Web application frontend
│   ├── index.html           # Main HTML interface
│   ├── style.css            # Styling and layout
│   └── script.js            # JavaScript functionality
├── backend/                 # Python backend API
│   ├── app.py              # Flask web server
│   ├── speech_recognition_module.py  # Speech-to-text processing
│   ├── mood_detection_module.py      # Facial emotion recognition
│   └── diary_storage.py             # File storage management
├── diary_entries/           # Stored diary entries (auto-created)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser with camera and microphone support
- FFmpeg (for audio processing)

### Installation

1. **Clone or download the project**
   ```bash
   cd smartdiary
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **System Requirements**

   **Windows:**
   - Modern browser (Chrome, Edge recommended)
   - Python 3.8+ with pip
   - No additional system dependencies required!

   **Ubuntu/Debian (optional for advanced features):**
   ```bash
   sudo apt-get update
   sudo apt-get install libopencv-dev python3-opencv
   ```

   **macOS:**
   - Modern browser (Chrome, Safari, Edge)
   - Python 3.8+ installed via Homebrew or official installer

### Running the Application

1. **Start the Python backend**
   ```bash
   cd backend
   python app.py
   ```
   The API server will start on `http://localhost:5000`

2. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or serve it using a local web server:
   ```bash
   cd frontend
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

3. **Grant permissions**
   - Allow camera access for mood detection
   - Allow microphone access for speech-to-text

## 🎯 How to Use

### Recording Speech
1. Click "Start Recording" button
2. Speak your diary entry clearly
3. Click "Stop Recording" when finished
4. The text will automatically appear in the diary entry field

### Mood Detection
1. Click "Start Camera" to activate your webcam
2. Position your face in the camera view
3. Click "Capture Mood" to analyze your current emotion
4. The detected mood will be displayed and added to your entry

### Saving Entries
1. Add a title (optional)
2. Write or record your diary content
3. Capture your mood (optional)
4. Click "Save Entry" to store it as a .txt file

### Viewing Entries
- Diary entries are saved in the `diary_entries/` folder
- Each entry is a readable text file with timestamp and metadata
- Files are named with date and time: `entry_YYYYMMDD_HHMMSS.txt`

## 🔧 Configuration

### Speech Recognition Languages
The app uses browser-based speech recognition. To change the language, edit `frontend/script.js`:
```javascript
// Change this line for different languages
this.recognition.lang = 'en-US'; // English (US)
// this.recognition.lang = 'hi-IN'; // Hindi (India)
// this.recognition.lang = 'en-IN'; // English (India)
```

**Supported Languages:**
- `en-US` - English (United States)
- `hi-IN` - Hindi (India)  
- `en-IN` - English (India)
- `es-ES` - Spanish (Spain)
- `fr-FR` - French (France)
- And many more...

### Mood Detection Sensitivity
Adjust confidence threshold in `mood_detection_module.py`:
```python
self.confidence_threshold = 0.3  # Lower = more sensitive, Higher = more accurate
```

## 📁 File Structure Details

### Frontend Files
- **index.html**: Main user interface with camera preview, speech controls, and diary form
- **style.css**: Modern styling with responsive design and animations
- **script.js**: Handles camera access, audio recording, and API communication

### Backend Files
- **app.py**: Flask web server with REST API endpoints
- **speech_recognition_module.py**: Audio processing and speech-to-text conversion
- **mood_detection_module.py**: Facial emotion recognition using computer vision
- **diary_storage.py**: File management for saving and retrieving diary entries

## 🌐 API Endpoints

The backend provides the following REST API endpoints:

- `POST /speech_to_text` - Convert audio to text
- `POST /detect_mood` - Analyze facial emotions from image
- `POST /save_entry` - Save diary entry to text file
- `GET /get_entries` - Retrieve list of all entries
- `GET /health` - Check system status

## 🔍 Troubleshooting

### Common Issues

**Camera not working:**
- Check browser permissions
- Ensure camera is not being used by another application
- Try refreshing the page

**Microphone not working:**
- Check browser permissions
- Test microphone in other applications
- Install pyaudio: `pip install pyaudio`

**Speech recognition fails:**
- Ensure you're using a modern browser (Chrome, Edge, Safari)
- Check microphone permissions in browser settings
- Speak clearly and avoid background noise
- Try refreshing the page if recognition stops working

**Mood detection not working:**
- Ensure good lighting for face detection
- Position face clearly in camera view
- Check if OpenCV and TensorFlow are properly installed

**Backend server errors:**
- Check Python dependencies are installed
- Ensure Flask server is running on port 5000
- Check console logs for detailed error messages

### Dependencies Issues

**If mood detection fails:**
```bash
pip uninstall opencv-python fer
pip install opencv-python==4.8.1.78 fer==22.5.1
```

**If backend won't start:**
```bash
pip install flask flask-cors pillow numpy
```

**Speech recognition uses browser API, so no additional dependencies needed!**

## 🔒 Privacy & Security

- **100% Local Processing**: All data stays on your machine
- **No External APIs**: Speech recognition uses browser's built-in capabilities
- **Secure Storage**: Diary entries are stored as plain text files on your computer
- **Permission-Based**: Camera and microphone access only when you allow it
- **No Data Collection**: Your personal information never leaves your device

## 🤝 Contributing

Feel free to contribute to SmartDiary by:
- Reporting bugs
- Suggesting new features
- Improving documentation
- Adding support for more languages
- Enhancing mood detection accuracy

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Browser Speech Recognition API** for real-time speech-to-text
- **FER (Facial Emotion Recognition)** library for AI-powered mood detection
- **OpenCV** for computer vision and image processing
- **Flask** for the robust web API framework
- **TensorFlow** for deep learning-based emotion recognition

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify browser permissions for camera and microphone access

---

**Happy journaling with SmartDiary! 📖✨**