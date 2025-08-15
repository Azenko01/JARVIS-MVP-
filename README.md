# 🤖 JARVIS MVP (Desktop AI Assistant)
This is the beta version of the program
**Author:** Oleksandr Azenko
**Version:** MVP v1
**Language:** Python 3.8+

## 📋 Project Description

JARVIS is a personal voice assistant in the style of J.A.R.V.I.S. from the "Iron Man" movie. The assistant runs on a computer, accepts voice commands in Ukrainian and English, performs system tasks, speaks responses, and learns from the user.

## ✨ Key Features

### 🎤 Voice Control

* ✅ Recognition of Ukrainian and English speech
* ✅ Voice responses with a soft female voice
* ✅ Activation phrase: "Hello, Jarvis"
* ✅ Modes: voice and text output

### 🧠 Intelligent Functions

* ✅ Learning new commands in real time
* ✅ Saving interaction history
* ✅ Expandable knowledge base
* ✅ GPT integration for complex queries

### 🔧 System Commands

* ✅ Open and close applications
* ✅ System control (shutdown, restart)
* ✅ Web search and navigation
* ✅ Weather information
* ✅ Visual screen analysis

### 📱 Additional Features

* ✅ Graphical interface (Dashboard)
* ✅ Note-taking
* ✅ Screenshot creation
* ✅ On-screen code analysis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd JARVIS_AI

# Install Python packages
pip install -r requirements.txt
```

### 2. Additional System Dependencies

**Windows:**

```bash
# Install Tesseract OCR for text recognition
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Microphone setup:**

* Make sure the microphone is working
* Grant permission to use the microphone

### 3. Configuration

Create a `.env` file in the project root:

```env
# API keys (optional)
OPENAI_API_KEY=your_openai_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here

# Voice settings
VOICE_LANGUAGE=uk-UA
VOICE_RATE=150
VOICE_VOLUME=0.8

# Default city for weather
DEFAULT_CITY=Kyiv
```

### 4. Launch

```bash
# Run main assistant
python main.py

# Run graphical interface
python gui/dashboard.py
```

## 🗣️ Example Commands

### Basic Commands

```
"Hello, Jarvis"               # Activation
"Open YouTube"                 # Open websites
"Launch Chrome"                # Run applications
"Close all windows"            # Close windows
"What’s the weather?"          # Weather info
"Search for borscht recipe"    # Web search
"What’s on the screen?"        # Screen analysis
"Play music"                   # Launch music app
```

### Learning Commands

```
"Jarvis, learn a new command"
"Remember this PDF"
"Update your knowledge"
"Write in notebook: note text"
```

### System Commands

```
"Shut down computer"          # With confirmation
"Restart system"              # With confirmation
"Sleep mode"                   # Hibernate
"Lock computer"                # Lock screen
```

### Work Modes

```
"Write on the screen"          # Text output
"Speak with voice"              # Voice output
"Stop"                          # Exit
```

## 📁 Project Structure

```
JARVIS_AI/
├── main.py                     # Main launch
├── config.py                   # Configuration
├── voice/                      # Voice modules
│   ├── listener.py             # Speech recognition
│   └── speaker.py              # Speech synthesis
├── memory/                     # Memory & learning
│   ├── memory.db               # SQLite database
│   ├── knowledge_base/         # Knowledge base
│   │   ├── pdf_data.json       # PDF knowledge
│   │   └── notes.txt           # User notes
│   └── learner.py              # Learning logic
├── plugins/                    # Command plugins
│   ├── weather.py              # Weather
│   ├── open_apps.py            # App control
│   ├── search_web.py           # Web search
│   ├── shutdown.py             # System commands
│   └── visual_assistant.py     # Visual analysis
├── gui/                        # Graphical interface
│   └── dashboard.py            # Dashboard
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## 🔧 Settings

### Voice Settings

In `config.py` you can change:

* `VOICE_RATE` – speech speed (50-300)
* `VOICE_VOLUME` – volume (0.0-1.0)
* `VOICE_LANGUAGE` – interface language

### Security

Dangerous commands are disabled by default:

* Disk formatting
* Deleting system files
* Forced shutdown without confirmation

### API Integrations

**OpenWeatherMap (Weather):**

1. Register at [https://openweathermap.org/](https://openweathermap.org/)
2. Get a free API key
3. Add it to `.env` file

**OpenAI (Advanced Features):**

1. Register at [https://platform.openai.com/](https://platform.openai.com/)
2. Get an API key
3. Add it to `.env` file

## 🎯 Usage

### First Launch

1. Run `python main.py`
2. Wait for the message "JARVIS is ready"
3. Say "Hello, Jarvis" to activate
4. Give a command, e.g., "Open YouTube"

### Learning New Commands

```
You: "Hello, Jarvis"  
JARVIS: "Yes, I’m listening."  

You: "Learn a new command"  
JARVIS: "I’m listening. Name the command and describe its action."  

You: "When I say 'open Telegram', launch Telegram.exe"  
JARVIS: "Command learned! I now know how to execute it."
```

### Graphical Interface

Dashboard provides:

* 📜 Full interaction history
* 📊 Usage statistics
* ⚡ Custom command management
* ⚙️ Voice and system settings
* 🎛️ JARVIS control panel

## 🔍 Troubleshooting

### Voice Issues

**Microphone not working:**

```bash
# Check microphone list
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Poor recognition:**

* Speak clearly and not too fast
* Reduce background noise
* Check microphone settings

### App Issues

**App not opening:**

* Check if the app is installed
* Add app path to `plugins/open_apps.py`

**Permission errors:**

* Run as administrator (Windows)
* Grant necessary permissions (macOS/Linux)

### Database Issues

**Database corrupted:**

```bash
# Delete database file (will lose history)
rm memory/memory.db

# Restart JARVIS to create a new database
python main.py
```

## 🚧 Future Improvements

### Version 1.1

* [ ] Telegram bot integration
* [ ] Voice commands over network
* [ ] Advanced PDF processing
* [ ] Automatic internet knowledge updates

### Version 1.2

* [ ] Community plugin support
* [ ] IDE integration (VS Code, PyCharm)
* [ ] Voice emotion recognition
* [ ] Personalized responses

### Version 2.0

* [ ] Full learning mode like GPTs
* [ ] Web interface
* [ ] Mobile app
* [ ] Cloud sync

## 🤝 Contribution

Contributions welcome:

* 🐛 Bug reports
* 💡 Feature suggestions
* 🔧 Pull requests
* 📖 Documentation improvements

### How to Contribute:

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Create a Pull Request

## 📄 License

MIT License – free to use for personal and commercial projects.

## 📞 Support

* 📧 Email: \[your email]
* 💬 Issues: \[GitHub Issues]
* 📱 Telegram: \[your Telegram]

## 🙏 Acknowledgements

* OpenAI for GPT API
* Google for Speech Recognition API
* Python community for amazing libraries
* Marvel fans for inspiration 😄

---

**"Sometimes you gotta run before you can walk."** – Tony Stark

🤖 **JARVIS MVP v1** – Your personal AI assistant is ready!

## 🆕 New Commands in MVP v1.1

### 🧠 Learning & Updates

```
"Jarvis, update yourself"         # Update from GitHub + knowledge base
"Remember this PDF"               # Learn from PDF via GPT
"Learn a new command"              # Interactive learning
```

### 💻 Programmer Assistant

```
"Analyze code"                     # Code quality analysis
"Check code"                        # Error checking
"Format code"                       # Auto-formatting
"Run code"                          # Execute current file
"Create Python file"                # New file from template
"Insert function template"          # Code templates
```

### 🎯 Improved Activation

```
"Hello, Jarvis"                    # Activation (more accurate now)
"Write on the screen"               # Text mode
"Speak with voice"                  # Voice mode
```

## 🔧 New Features

### 🤖 Personalized Responses

JARVIS now addresses you by name and uses different conversation styles:

* "Listening to you, Oleksandr"
* "Alright, opening Visual Studio Code"
* "Updating my Python knowledge"

### 📚 Learning from PDF

* Automatic extraction of knowledge from PDF files
* GPT integration for structuring information
* Saved in knowledge base for later use

### 🔄 Auto-Update

* Update code from GitHub repository
* Download new plugins
* Expand knowledge base from the internet

### 💻 IDE Integration

* Real-time code analysis
* Automatic formatting
* Insert code templates
* Code improvement suggestions
