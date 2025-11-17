# Django LMS - AI-Powered Learning Management System

A comprehensive Django-based Learning Management System with AI assistance, real-time chat, and livestreaming capabilities. Built for USIU-A capstone project.

## ✨ Features

### 🎓 Core LMS Features
- **User Management**: Role-based access control (Students, Instructors, Admins)
- **Course Management**: Create, publish, and manage courses with enrollment system
- **Assignments**: Multiple assignment types (Homework, Quiz, Project, Exam, Essay)
- **Grading System**: Weighted categories, grade scales, automatic calculations
- **Calendar**: Event management with multiple views (Month, Week, Day)
- **Notifications**: System-wide notifications and course announcements

### 🤖 AI-Powered Features
**For Students:**
- Quiz hints and explanations
- Answer review before submission
- Concept clarification
- Personalized study recommendations
- Post-submission feedback

**For Teachers:**
- AI-powered grading assistance with confidence scores
- Automated feedback generation
- Student performance analytics
- Learning gap identification
- Struggling student detection
- Bulk grading support

### 💬 Real-Time Chat
- Course-based chat rooms
- Direct messaging between users
- Group chats
- Message read receipts
- Typing indicators
- User presence tracking
- File sharing support

### 📹 Livestreaming
- Live video streaming with WebRTC
- Interactive Q&A during streams
- Live chat during streams
- Stream recording
- Viewer analytics (current, peak, total views)
- Watch time tracking
- Question upvoting and pinning

## 🏗️ Project Structure

```
djangolms/
├── djangolms/
│   ├── accounts/          # User management & authentication
│   ├── courses/           # Course management
│   ├── assignments/       # Assignment submission & tracking
│   ├── grades/            # Grading system
│   ├── events/            # Calendar & event management
│   ├── notifications/     # Announcements & notifications
│   ├── ai_assistant/      # AI-powered assistance
│   ├── chat/              # Real-time chat functionality
│   ├── livestream/        # Livestreaming & WebRTC
│   ├── settings.py        # Django configuration
│   ├── urls.py            # URL routing
│   ├── asgi.py            # ASGI config for Channels
│   └── celery.py          # Background task configuration
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── media/                 # User uploads
├── requirements.txt       # Python dependencies
└── manage.py              # Django management script
```

## 🛠️ Tech Stack

**Backend:**
- Django 5.1.4
- Django REST Framework 3.15.2
- Django Channels 4.2.0 (WebSockets)
- Celery 5.4.0 (Background tasks)

**AI Integration:**
- Anthropic Claude API (claude-3-5-sonnet-20241022)
- OpenAI API support

**Real-time & Streaming:**
- Django Channels + Redis
- WebRTC for peer-to-peer streaming
- WebSocket for chat and live updates

**Database:**
- SQLite (Development)
- PostgreSQL (Production-ready)

**Frontend:**
- Django Templates
- JavaScript (WebSocket clients, WebRTC)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Redis (for Channels and Celery)
- PostgreSQL (optional, for production)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd django-lms
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys and configuration
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run Redis** (in a separate terminal)
```bash
redis-server
```

8. **Run Celery** (in a separate terminal)
```bash
celery -A djangolms worker -l info
```

9. **Run the development server**
```bash
python manage.py runserver
```

or with Daphne (for WebSocket support):
```bash
daphne -b 0.0.0.0 -p 8000 djangolms.asgi:application
```

10. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## 📝 Configuration

### AI API Keys
Add your API keys to `.env`:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
```

### Redis Configuration
```
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Channel Layers
For development without Redis, update `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

## 🎯 Key URLs

- `/accounts/` - User authentication
- `/courses/` - Course management
- `/assignments/` - Assignments
- `/grades/` - Gradebook
- `/calendar/` - Event calendar
- `/ai/` - AI assistant features
- `/chat/` - Real-time chat
- `/livestream/` - Livestreaming

## 📊 Database Models

### AI Assistant
- `AIInteraction` - Track all AI interactions
- `AIGradingSuggestion` - AI grading suggestions
- `StudentAnalytics` - Performance analytics
- `QuizAssistanceSession` - Quiz help sessions

### Chat
- `ChatRoom` - Chat rooms (course, direct, group)
- `Message` - Chat messages
- `MessageReadReceipt` - Read tracking
- `UserPresence` - Online status
- `ChatNotification` - Unread message notifications

### Livestream
- `LiveStream` - Streaming sessions
- `StreamViewer` - Viewer tracking
- `StreamRecording` - Recorded streams
- `QAQuestion` - Q&A during streams
- `QuestionUpvote` - Question voting
- `StreamChat` - Stream chat messages

## 🔒 Security Notes

- Never commit `.env` file or API keys
- Use environment variables for sensitive data
- Configure `ALLOWED_HOSTS` for production
- Set `DEBUG = False` in production
- Use strong `SECRET_KEY`

## 🤝 Contributing

This is a capstone project. Contributions and feedback are welcome!

## 📄 License

[Specify your license here]

## 👨‍💻 Author

Alex Raza - USIU-A Capstone Project
