// CogniDiary JavaScript Frontend
class CogniDiary {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.videoElement = document.getElementById('videoElement');
        this.canvasElement = document.getElementById('canvasElement');
        this.currentMood = '';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupCanvas();
    }

    setupEventListeners() {
        // Camera controls
        document.getElementById('startCamera').addEventListener('click', () => this.startCamera());
        document.getElementById('stopCamera').addEventListener('click', () => this.stopCamera());
        document.getElementById('capturePhoto').addEventListener('click', () => this.captureAndAnalyzeMood());
        
        // Speech controls
        document.getElementById('startRecording').addEventListener('click', () => this.startRecording());
        document.getElementById('stopRecording').addEventListener('click', () => this.stopRecording());
        
        // Form controls
        document.getElementById('diaryForm').addEventListener('submit', (e) => this.saveDiaryEntry(e));
        document.getElementById('clearEntry').addEventListener('click', () => this.clearForm());
    }

    setupCanvas() {
        const canvas = this.canvasElement;
        const video = this.videoElement;
        canvas.width = 400;
        canvas.height = 300;
    }

    // Camera Functions
    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 400, height: 300 }, 
                audio: false 
            });
            
            this.videoElement.srcObject = this.stream;
            this.videoElement.classList.add('active');
            
            document.getElementById('startCamera').disabled = true;
            document.getElementById('stopCamera').disabled = false;
            document.getElementById('capturePhoto').disabled = false;
            
            this.showStatus('Camera started successfully!', 'success');
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showStatus('Error accessing camera. Please check permissions.', 'error');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.videoElement.srcObject = null;
            this.videoElement.classList.remove('active');
            
            document.getElementById('startCamera').disabled = false;
            document.getElementById('stopCamera').disabled = true;
            document.getElementById('capturePhoto').disabled = true;
            
            this.showStatus('Camera stopped', 'info');
        }
    }

    async captureAndAnalyzeMood() {
        if (!this.stream) {
            this.showStatus('Please start the camera first', 'error');
            return;
        }

        try {
            // Capture frame from video
            const canvas = this.canvasElement;
            const context = canvas.getContext('2d');
            context.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
            
            // Convert to blob
            canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('image', blob, 'mood_capture.jpg');
                
                this.showMoodResult('Analyzing mood...', false);
                
                try {
                    const response = await fetch('http://localhost:5000/detect_mood', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        this.currentMood = result.mood;
                        this.showMoodResult(`Detected Mood: ${result.mood} (${result.confidence}% confidence)`, false);
                        document.getElementById('detectedMood').value = result.mood;
                    } else {
                        this.showMoodResult('Error: ' + result.error, true);
                    }
                } catch (error) {
                    console.error('Error analyzing mood:', error);
                    this.showMoodResult('Error connecting to mood detection service', true);
                }
            }, 'image/jpeg', 0.8);
            
        } catch (error) {
            console.error('Error capturing photo:', error);
            this.showStatus('Error capturing photo', 'error');
        }
    }

    showMoodResult(message, isError = false) {
        const moodResult = document.getElementById('moodResult');
        moodResult.textContent = message;
        moodResult.className = isError ? 'mood-result error' : 'mood-result';
    }

    // Speech Recognition Functions
    async startRecording() {
        // Try browser native speech recognition first
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.startBrowserSpeechRecognition();
        } else {
            // Fallback to audio recording
            this.startAudioRecording();
        }
    }

    startBrowserSpeechRecognition() {
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US'; // You can change this to 'hi-IN' for Hindi
            
            this.recognition.onstart = () => {
                document.getElementById('startRecording').disabled = true;
                document.getElementById('stopRecording').disabled = false;
                this.showRecordingStatus('🔴 Recording... Speak now!', 'recording');
            };
            
            this.recognition.onresult = (event) => {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                
                if (finalTranscript) {
                    const currentText = document.getElementById('entryText').value;
                    const newText = currentText ? currentText + ' ' + finalTranscript : finalTranscript;
                    document.getElementById('entryText').value = newText;
                    
                    this.showRecordingStatus('✅ Text added to diary entry!', '');
                    this.showStatus('Speech converted to text successfully!', 'success');
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showRecordingStatus('❌ Error in speech recognition', '');
                this.showStatus('Speech recognition error: ' + event.error, 'error');
                this.resetRecordingButtons();
            };
            
            this.recognition.onend = () => {
                this.resetRecordingButtons();
            };
            
            this.recognition.start();
            
        } catch (error) {
            console.error('Error starting browser speech recognition:', error);
            this.showStatus('Browser speech recognition not available. Trying audio recording...', 'info');
            this.startAudioRecording();
        }
    }

    async startAudioRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            // Try to use WAV format if supported, otherwise use default
            const options = { mimeType: 'audio/wav' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm';
            }
            
            this.mediaRecorder = new MediaRecorder(stream, options);
            this.audioChunks = [];
            
            console.log('Recording with MIME type:', this.mediaRecorder.mimeType);
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudioRecording();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            document.getElementById('startRecording').disabled = true;
            document.getElementById('stopRecording').disabled = false;
            
            this.showRecordingStatus('🔴 Recording... Click stop when finished', 'recording');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showStatus('Error accessing microphone. Please check permissions.', 'error');
        }
    }

    stopRecording() {
        if (this.recognition) {
            // Stop browser speech recognition
            this.recognition.stop();
            this.recognition = null;
            this.resetRecordingButtons();
        } else if (this.mediaRecorder && this.isRecording) {
            // Stop audio recording
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Stop all audio tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            this.showRecordingStatus('⏳ Processing audio...', 'processing');
        }
    }

    resetRecordingButtons() {
        document.getElementById('startRecording').disabled = false;
        document.getElementById('stopRecording').disabled = true;
        this.showRecordingStatus('', '');
    }

    async processAudioRecording() {
        try {
            // Get the MIME type that was actually used
            const mimeType = this.mediaRecorder.mimeType;
            console.log('Processing audio with MIME type:', mimeType);
            
            // Create audio blob with the actual MIME type
            const audioBlob = new Blob(this.audioChunks, { type: mimeType });
            const formData = new FormData();
            
            // Set filename based on MIME type
            let filename = 'recording.webm';
            if (mimeType.includes('wav')) {
                filename = 'recording.wav';
            } else if (mimeType.includes('mp4')) {
                filename = 'recording.mp4';
            } else if (mimeType.includes('ogg')) {
                filename = 'recording.ogg';
            }
            
            formData.append('audio', audioBlob, filename);
            
            console.log('Sending audio blob:', audioBlob.size, 'bytes, type:', mimeType);
            
            const response = await fetch('http://localhost:5000/speech_to_text', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            console.log('Speech recognition result:', result);
            
            if (result.success) {
                const currentText = document.getElementById('entryText').value;
                const newText = currentText ? currentText + ' ' + result.text : result.text;
                document.getElementById('entryText').value = newText;
                
                this.showRecordingStatus('✅ Text added to diary entry!', '');
                this.showStatus('Speech converted to text successfully!', 'success');
            } else {
                this.showRecordingStatus('❌ Error processing audio', '');
                this.showStatus('Error: ' + (result.error || 'Unknown error'), 'error');
            }
            
        } catch (error) {
            console.error('Error processing audio:', error);
            this.showRecordingStatus('❌ Error processing audio', '');
            this.showStatus('Error processing audio: ' + error.message, 'error');
        }
    }

    showRecordingStatus(message, className) {
        const statusElement = document.getElementById('recordingStatus');
        statusElement.textContent = message;
        statusElement.className = 'recording-status ' + className;
    }

    // Diary Functions
    async saveDiaryEntry(event) {
        event.preventDefault();
        
        const title = document.getElementById('entryTitle').value.trim();
        const text = document.getElementById('entryText').value.trim();
        const mood = document.getElementById('detectedMood').value.trim();
        
        if (!text) {
            this.showStatus('Please write something in your diary entry', 'error');
            return;
        }
        
        const entryData = {
            title: title || 'Untitled Entry',
            text: text,
            mood: mood || 'Not detected',
            timestamp: new Date().toISOString()
        };
        
        try {
            const response = await fetch('http://localhost:5000/save_entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entryData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showStatus('Diary entry saved successfully!', 'success');
                this.clearForm();
            } else {
                this.showStatus('Error saving entry: ' + result.error, 'error');
            }
            
        } catch (error) {
            console.error('Error saving entry:', error);
            this.showStatus('Error connecting to server', 'error');
        }
    }

    clearForm() {
        document.getElementById('entryTitle').value = '';
        document.getElementById('entryText').value = '';
        document.getElementById('detectedMood').value = '';
        this.currentMood = '';
        this.showMoodResult('', false);
        this.showRecordingStatus('', '');
        this.showStatus('Form cleared', 'info');
    }

    // Utility Functions
    showStatus(message, type) {
        const statusElement = document.getElementById('statusMessage');
        statusElement.textContent = message;
        statusElement.className = `status-message ${type} show`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusElement.classList.remove('show');
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CogniDiary();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}