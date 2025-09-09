WIP - Repo for the Django learning management system I'm building for my capstone project for USIU-A.

## Project Architecture Details

### Django Project Structure

```
djangolms/
├── config/                 # Main Django settings
├── apps/
│   ├── accounts/          # User management & authentication
│   ├── courses/           # Course management
│   ├── streaming/         # Livestream functionality
│   ├── recordings/        # Video storage & playback
│   ├── assignments/       # Assignment system
│   ├── grades/           # Gradebook
│   └── chat/             # Real-time messaging
├── static/               # CSS, JS, images
├── templates/            # HTML templates
└── media/               # User uploads

```

### Core Architecture Components

**Microservices approach with these main components:**

- **Web application** (LMS interface)
- **Streaming service** (live video handling)
- **Recording service** (video processing & storage)
- **Real-time communication** (chat, Q&A during streams)
- **Database layer** (user data, courses, recordings)

### Selected Tech Stack (Subject to change)

- **Backend**: Django + Django REST Framework
- **Real-time**: Django Channels + Redis
- **Database**: PostgreSQL
- **Background Tasks**: Celery
- **Video Processing**: FFmpeg
- **Streaming**: WebRTC + Janus WebRTC Gateway
- **Frontend**: Django templates + HTMX or React/Vue.js
