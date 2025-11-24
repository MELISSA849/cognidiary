// SmartDiary - Elegant & Efficient Frontend
// Optimized for performance and user experience

class SmartDiary {
    constructor() {
        this.API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:5000'
            : '';
        
        // State management
        this.state = {
            cameraActive: false,
            recordingActive: false,
            currentMood: '',
            mediaStream: null,
            recognition: null
        };
        
        // DOM elements cache
        this.elements = {};
        
        // Initialize
        this.init();
    }

    init() {
        this.cacheElements();
        this.setupEventListeners();
        this.setupWordCount();
        console.log('📝 SmartDiary initialized');
    }

    cacheElements() {
        const ids = [
            'videoElement', 'canvasElement', 'cameraOverlay',
            'startCamera', 'stopCamera', 'capturePhoto',
            'moodResult', 'moodBadge', 'detectedMood',
            'startRecording', 'stopRecording', 'voiceStatus',
            'diaryForm', 'entryTitle', 'entryText',
            'clearEntry', 'wordCount', 'toastContainer'
        ];
        
        ids.forEach(id => {
            this.elements[id] = document.getElementById(id);
        });
        
        this.elements.soundWave = document.querySelector('.sound-wave');
    }

    setupEventListeners() {
        // Camera controls
        this.elements.startCamera?.addEventListener('click', () => this.startCamera());
        this.elements.stopCamera?.addEventListener('click', () => this.stopCamera());
        this.elements.capturePhoto?.addEventListener('click', () => this.captureAndAnalyzeMood());
        this.elements.cameraOverlay?.addEventListener('click', () => this.startCamera());
        
        // Voice controls
        this.elements.startRecording?.addEventListener('click', () => this.startRecording());
        this.elements.stopRecording?.addEventListener('click', () => this.stopRecording());
        
        // Form controls
        this.elements.diaryForm?.addEventListener('submit', (e) => this.saveDiaryEntry(e));
        this.elements.clearEntry?.addEventListener('click', () => this.clearForm());
        
        // Auto-save draft (debounced)
        this.elements.entryText?.addEventListener('input', this.debounce(() => {
            this.updateWordCount();
            this.saveDraft();
        }, 500));
        
        this.elements.entryTitle?.addEventListener('input', this.debounce(() => {
            this.saveDraft();
        }, 500));
    }

    setupWordCount() {
        this.updateWordCount();
    }

    updateWordCount() {
        const text = this.elements.entryText?.value || '';
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        const count = text.trim() ? words.length : 0;
        
        if (this.elements.wordCount) {
            this.elements.wordCount.textContent = `${count} word${count !== 1 ? 's' : ''}`;
        }
    }

    // === Camera Functions ===
    async startCamera() {
        try {
            this.state.mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' },
                audio: false
            });
            
            this.elements.videoElement.srcObject = this.state.mediaStream;
            this.elements.videoElement.classList.add('active');
            this.elements.cameraOverlay.classList.add('hidden');
            
            this.elements.startCamera.disabled = true;
            this.elements.stopCamera.disabled = false;
            this.elements.capturePhoto.disabled = false;
            
            this.state.cameraActive = true;
            this.showToast('Camera started successfully', 'success');
        } catch (error) {
            console.error('Camera error:', error);
            this.showToast('Cannot access camera. Please check permissions.', 'error');
        }
    }

    stopCamera() {
        if (this.state.mediaStream) {
            this.state.mediaStream.getTracks().forEach(track => track.stop());
            this.elements.videoElement.srcObject = null;
            this.elements.videoElement.classList.remove('active');
            this.elements.cameraOverlay.classList.remove('hidden');
            
            this.elements.startCamera.disabled = false;
            this.elements.stopCamera.disabled = true;
            this.elements.capturePhoto.disabled = true;
            
            this.state.cameraActive = false;
            this.state.mediaStream = null;
        }
    }

    async captureAndAnalyzeMood() {
        if (!this.state.cameraActive) {
            this.showToast('Please start the camera first', 'error');
            return;
        }

        try {
            // Capture frame from video
            const canvas = this.elements.canvasElement;
            canvas.width = this.elements.videoElement.videoWidth;
            canvas.height = this.elements.videoElement.videoHeight;
            
            const context = canvas.getContext('2d');
            context.drawImage(this.elements.videoElement, 0, 0);
            
            // Convert to blob
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));
            
            // Send to server
            this.showMoodResult('Analyzing your mood...', false);
            
            const formData = new FormData();
            formData.append('image', blob, 'mood_capture.jpg');
            
            const response = await fetch(`${this.API_BASE}/detect_mood`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.state.currentMood = result.mood;
                this.showMoodResult(
                    `${this.getMoodEmoji(result.mood)} ${result.mood} (${result.confidence}% confidence)`,
                    false
                );
                this.elements.detectedMood.textContent = result.mood;
                this.showToast(`Mood detected: ${result.mood}`, 'success');
            } else {
                this.showMoodResult(`❌ ${result.error}`, true);
                this.showToast('Mood detection failed', 'error');
            }
            
        } catch (error) {
            console.error('Mood analysis error:', error);
            this.showMoodResult('Error analyzing mood', true);
            this.showToast('Connection error', 'error');
        }
    }

    showMoodResult(message, isError) {
        this.elements.moodResult.textContent = message;
        this.elements.moodResult.className = isError ? 'mood-result error' : 'mood-result';
    }

    getMoodEmoji(mood) {
        const emojis = {
            'Happy': '😊',
            'Sad': '😢',
            'Angry': '😠',
            'Anxious': '😰',
            'Surprised': '😲',
            'Calm': '😌',
            'Neutral': '😐',
            'Disgusted': '😖'
        };
        return emojis[mood] || '😐';
    }

    // === Speech Recognition ===
    async startRecording() {
        // Try browser native speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.startBrowserSpeechRecognition();
        } else {
            this.showToast('Speech recognition not supported in this browser', 'error');
        }
    }

    startBrowserSpeechRecognition() {
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.state.recognition = new SpeechRecognition();
            
            this.state.recognition.continuous = true;
            this.state.recognition.interimResults = false;
            this.state.recognition.lang = 'en-US';
            
            this.state.recognition.onstart = () => {
                this.state.recordingActive = true;
                this.elements.startRecording.disabled = true;
                this.elements.stopRecording.disabled = false;
                this.elements.voiceStatus.textContent = '🎤 Listening...';
                this.elements.soundWave.classList.add('active');
            };
            
            this.state.recognition.onresult = (event) => {
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + ' ';
                    }
                }
                
                if (finalTranscript) {
                    const currentText = this.elements.entryText.value;
                    const newText = currentText ? currentText + ' ' + finalTranscript.trim() : finalTranscript.trim();
                    this.elements.entryText.value = newText;
                    this.updateWordCount();
                    this.elements.voiceStatus.textContent = '✅ Text added!';
                }
            };
            
            this.state.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                
                // Handle specific errors
                if (event.error === 'no-speech') {
                    this.showToast('No speech detected. Please speak into the microphone.', 'warning');
                    // Don't reset - let user try speaking again
                    return;
                } else if (event.error === 'not-allowed') {
                    this.showToast('Microphone access denied. Please allow microphone permissions.', 'error');
                } else if (event.error === 'network') {
                    this.showToast('Network error. Speech recognition requires internet connection.', 'error');
                } else {
                    this.showToast(`Speech error: ${event.error}`, 'error');
                }
                this.resetRecording();
            };
            
            this.state.recognition.onend = () => {
                // If manually stopped, don't restart
                if (!this.state.recordingActive) {
                    this.resetRecording();
                    return;
                }
                
                // Auto-restart if still recording (continuous mode)
                try {
                    this.state.recognition.start();
                } catch (e) {
                    console.log('Recognition ended:', e);
                    this.resetRecording();
                }
            };
            
            this.state.recognition.start();
            
        } catch (error) {
            console.error('Speech recognition error:', error);
            this.showToast('Speech recognition failed', 'error');
        }
    }

    stopRecording() {
        this.state.recordingActive = false; // Set flag before stopping
        if (this.state.recognition) {
            try {
                this.state.recognition.stop();
            } catch (e) {
                console.log('Stop error:', e);
            }
        }
        this.resetRecording();
    }

    resetRecording() {
        this.state.recordingActive = false;
        this.state.recognition = null;
        this.elements.startRecording.disabled = false;
        this.elements.stopRecording.disabled = true;
        this.elements.voiceStatus.textContent = 'Ready to listen';
        this.elements.soundWave.classList.remove('active');
    }

    // === Diary Functions ===
    async saveDiaryEntry(event) {
        event.preventDefault();
        
        const title = this.elements.entryTitle.value.trim();
        const text = this.elements.entryText.value.trim();
        const mood = this.state.currentMood || 'Not detected';
        
        if (!text) {
            this.showToast('Please write something first', 'error');
            return;
        }
        
        const entryData = {
            title: title || 'Untitled Entry',
            text: text,
            mood: mood,
            timestamp: new Date().toISOString()
        };
        
        try {
            this.showToast('Saving entry...', 'info');
            
            const response = await fetch(`${this.API_BASE}/save_entry`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entryData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('✨ Entry saved successfully!', 'success');
                this.clearForm();
                this.clearDraft();
            } else {
                this.showToast(`Error: ${result.error}`, 'error');
            }
            
        } catch (error) {
            console.error('Save error:', error);
            this.showToast('Connection error. Please try again.', 'error');
        }
    }

    clearForm() {
        this.elements.entryTitle.value = '';
        this.elements.entryText.value = '';
        this.elements.detectedMood.textContent = 'Not detected yet';
        this.state.currentMood = '';
        this.showMoodResult('', false);
        this.updateWordCount();
    }

    // === Draft Management ===
    saveDraft() {
        const draft = {
            title: this.elements.entryTitle.value,
            text: this.elements.entryText.value,
            mood: this.state.currentMood,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('smartdiary_draft', JSON.stringify(draft));
    }

    loadDraft() {
        try {
            const draft = JSON.parse(localStorage.getItem('smartdiary_draft'));
            if (draft) {
                this.elements.entryTitle.value = draft.title || '';
                this.elements.entryText.value = draft.text || '';
                this.state.currentMood = draft.mood || '';
                if (this.state.currentMood) {
                    this.elements.detectedMood.textContent = this.state.currentMood;
                }
                this.updateWordCount();
                this.showToast('Draft restored', 'info');
            }
        } catch (error) {
            console.error('Draft load error:', error);
        }
    }

    clearDraft() {
        localStorage.removeItem('smartdiary_draft');
    }

    // === Toast Notifications ===
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.elements.toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // === Utility Functions ===
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.smartDiary = new SmartDiary();
    
    // Check for draft on load
    if (localStorage.getItem('smartdiary_draft')) {
        setTimeout(() => {
            if (confirm('You have an unsaved draft. Would you like to restore it?')) {
                window.smartDiary.loadDraft();
            } else {
                window.smartDiary.clearDraft();
            }
        }, 1000);
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.smartDiary?.state.mediaStream) {
        window.smartDiary.stopCamera();
    }
    if (window.smartDiary?.state.recognition) {
        window.smartDiary.stopRecording();
    }
});
