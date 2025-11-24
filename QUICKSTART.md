# SmartDiary - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
# Windows
start.bat

# macOS/Linux
./start.sh

# Or use Python directly
python start_smartdiary.py
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:5000**

---

## 📖 Feature Guide

### ✏️ Writing an Entry

1. **Type or speak** your thoughts
2. **Capture your mood** (optional)
3. **Click "Save Entry"**

That's it! Your entry is saved locally.

### 🎤 Voice Input

**Chrome/Edge (Recommended):**
1. Click "Start Speaking"
2. Allow microphone access
3. Speak naturally
4. Click "Stop" when done

**Other Browsers:**
Use manual typing

### 📷 Mood Detection

1. Click "Start Camera"
2. Allow camera access
3. Position face in frame
4. Click "Capture"
5. Mood appears automatically

---

## 🔧 Configuration

### Change Port
Edit `backend/app_standalone.py`:
```python
app.run(host='0.0.0.0', port=5000)  # Change port here
```

### Storage Location
Entries saved in: `diary_entries/`

---

## ❓ Common Issues

### Camera Not Working
- ✅ Grant camera permission in browser
- ✅ Check if another app is using camera
- ✅ Refresh the page

### Voice Input Not Working
- ✅ Use Chrome or Edge browser
- ✅ Grant microphone permission
- ✅ Check system microphone settings

### Server Won't Start
- ✅ Ensure port 5000 is free
- ✅ Check Python version (3.8+)
- ✅ Reinstall: `pip install -r requirements.txt --force-reinstall`

---

## 📁 File Structure

```
smartdiary/
├── backend/              # Server code
├── frontend/             # Web interface
├── diary_entries/        # Your entries (auto-created)
├── requirements.txt      # Dependencies
├── start.bat            # Windows startup
├── start.sh             # Linux/Mac startup
└── start_smartdiary.py  # Python startup
```

---

## 🎨 Keyboard Shortcuts

- **Ctrl+S** - Save entry (in form)
- **Ctrl+K** - Clear form
- **Escape** - Stop camera/recording

---

## 💡 Tips & Tricks

### Draft Auto-Save
Your work is automatically saved as a draft every few seconds. Don't worry about losing your thoughts!

### Best Lighting for Mood Detection
- Face a light source
- Avoid backlighting
- Stay 1-3 feet from camera

### Voice Recognition Tips
- Speak clearly and naturally
- Pause for punctuation
- Use quiet environment

---

## 🔒 Privacy

- ✅ All data stored locally
- ✅ No cloud services
- ✅ No tracking
- ✅ Camera/mic access only when requested

---

## 📞 Need Help?

1. Check troubleshooting section above
2. Review README.md for details
3. Check browser console for errors (F12)

---

**Version 2.0 - Lightweight Standalone Edition**

*Made with ❤️ for mindful journaling*
