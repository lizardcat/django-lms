# Livestreaming & Chat Implementation Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [What's Been Implemented](#whats-been-implemented)
3. [Setup Instructions](#setup-instructions)
4. [How It Works](#how-it-works)
5. [Features Guide](#features-guide)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## 🎯 Overview

This Django LMS now includes fully functional **real-time chat** and **livestreaming** features with:

- ✅ WebSocket-powered real-time chat
- ✅ Course-based chat rooms
- ✅ Direct messaging
- ✅ Video conferencing via Jitsi Meet
- ✅ Live Q&A during streams
- ✅ Stream recordings
- ✅ Typing indicators & presence tracking
- ✅ Message read receipts

---

## ✨ What's Been Implemented

### Backend (✅ Complete)
- **Models** (`djangolms/chat/models.py` & `djangolms/livestream/models.py`)
  - ChatRoom, Message, UserPresence, Notifications
  - LiveStream, VideoConference, StreamViewer, QAQuestion

- **WebSocket Consumers** (`consumers.py`)
  - `ChatConsumer` - Real-time chat with typing indicators
  - `LiveStreamConsumer` - Livestream chat, Q&A, and viewer tracking

- **Views** (`views.py`)
  - All CRUD operations for chat and livestream
  - Stream management (start/stop/schedule)
  - Q&A moderation

- **URL Routing** (✅ Configured)
  - HTTP routes in `urls.py`
  - WebSocket routes in `routing.py`
  - ASGI configuration complete

### Frontend (✅ Complete)
- **Chat Templates**
  - `chat_home.html` - Chat room listing
  - `chat_room.html` - Real-time chat with WebSocket client

- **Livestream Templates**
  - `livestream_list.html` - Browse live & scheduled streams
  - `stream_view.html` - Watch streams with Jitsi integration
  - `create_stream.html` - Schedule new streams
  - `stream_detail.html` - Instructor control panel
  - `recording_view.html` - Watch recordings

- **JavaScript Features**
  - WebSocket connections with auto-reconnect
  - Jitsi Meet integration
  - Real-time message rendering
  - Typing indicators
  - Q&A upvoting
  - Countdown timers

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Activate your virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install all requirements
pip install -r requirements.txt
```

**Key Dependencies:**
- `channels==4.2.0` - WebSocket support
- `channels-redis==4.2.1` - Redis channel layer
- `daphne==4.1.2` - ASGI server
- `redis==5.2.0` - Redis client

### 2. Install & Start Redis

Redis is **required** for Django Channels to work.

**On Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Windows:**
- Download from https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis:alpine`

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Configure Environment

The `.env` file has been created with default values. Update these:

```bash
# Edit .env file
nano .env  # or use your preferred editor
```

**Important settings:**
```env
# Redis (default should work)
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Keys (optional, for AI features)
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates database tables for:
- Chat rooms and messages
- Livestreams and recordings
- User presence tracking
- Q&A questions

### 5. Create a Superuser (if not already done)

```bash
python manage.py createsuperuser
```

### 6. Create Sample Data (Recommended)

```bash
python manage.py create_sample_data
```

This creates:
- Sample users (students and instructors)
- Sample courses
- Course enrollments

### 7. Start the Development Server

You need to use **Daphne** (ASGI server) instead of the standard Django runserver for WebSocket support:

```bash
# Start with Daphne
daphne -b 0.0.0.0 -p 8000 djangolms.asgi:application
```

Or use the standard runserver (WebSockets may not work):
```bash
python manage.py runserver
```

### 8. Access the Application

- **Main Site:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **Chat:** http://localhost:8000/chat/
- **Livestreams:** http://localhost:8000/livestream/

---

## 🔧 How It Works

### Chat Architecture

```
User Browser (WebSocket Client)
       ↓
   Daphne ASGI Server
       ↓
  Django Channels
       ↓
   Redis Channel Layer
       ↓
  ChatConsumer (WebSocket Handler)
       ↓
   Database Models
```

**Flow:**
1. User opens chat room → WebSocket connection established
2. User types message → Sent via WebSocket
3. Server receives → Saves to database
4. Server broadcasts → All connected users receive message
5. Typing indicators sent in real-time

### Livestream Architecture

**Three Options Implemented:**

#### Option 1: Jitsi Meet (Currently Active) ✅
- **Pros:** Free, no backend needed, works immediately
- **Cons:** Limited customization
- **How it works:**
  - Instructor creates stream
  - Jitsi iframe embedded in stream_view.html
  - Unique room name: `USIULMSStream{id}{key}`
  - Instructor has full controls
  - Students join as viewers

#### Option 2: WebRTC Peer-to-Peer
- **Pros:** No third-party service
- **Cons:** Complex, limited to small groups
- **Code:** Already in `LiveStreamConsumer` (commented)
- **Requires:** STUN/TURN servers for NAT traversal

#### Option 3: Streaming Service
- **Options:** Agora, Twilio, AWS IVS
- **Pros:** Production-ready, scalable
- **Cons:** Requires paid accounts
- **Implementation:** Replace Jitsi iframe with service SDK

---

## 📚 Features Guide

### For Students

#### Chat
1. Navigate to **Chat** from sidebar
2. See all course chat rooms you're enrolled in
3. Click a room to enter
4. Type messages in real-time
5. See who's online
6. See typing indicators

#### Livestreams
1. Navigate to **Livestreams**
2. See **Live Now** section for active streams
3. Click "Join Stream" to watch
4. Participate in live chat
5. Ask questions in Q&A
6. Upvote important questions

### For Instructors

#### Creating a Livestream
1. Go to your course page
2. Click "Create Livestream"
3. Fill in:
   - Title (e.g., "Week 5 Lecture")
   - Description
   - Start/End time
   - Enable chat/Q&A/recording
4. Click "Create Livestream"

#### Managing a Stream
1. Go to **Livestreams** → Your stream
2. Click "Manage"
3. See stream statistics
4. Click "Start Stream" when ready
5. Join the Jitsi meeting
6. Monitor Q&A in sidebar
7. Answer questions during stream
8. Click "End Stream" when done

#### Stream Controls (Jitsi)
As instructor, you have full controls:
- **Microphone/Camera** - Toggle on/off
- **Screen Share** - Share your screen
- **Recording** - Record the session
- **Mute Everyone** - Moderate participants
- **Lobby** - Approve participants

#### Creating Chat Rooms
1. Go to your course
2. Click "Create Chat Room"
3. Students enrolled in course can access

---

## 🔍 Troubleshooting

### WebSockets Not Working

**Symptom:** Chat messages don't send, "Connection error"

**Solutions:**
1. **Check Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Use Daphne, not runserver:**
   ```bash
   daphne -b 0.0.0.0 -p 8000 djangolms.asgi:application
   ```

3. **Check browser console for errors:**
   - Open DevTools (F12)
   - Look for WebSocket errors
   - Should see: `WebSocket connected`

4. **Check firewall:**
   - Ensure port 8000 is open
   - Check for WebSocket blocking

### Jitsi Meet Not Loading

**Symptom:** Black screen, no video conference

**Solutions:**
1. **Check internet connection** - Jitsi requires internet
2. **Check browser permissions** - Allow camera/microphone
3. **Try different browser** - Chrome/Firefox work best
4. **Check console errors** - Look for Jitsi errors

### Migrations Failing

**Symptom:** `No such table` errors

**Solution:**
```bash
python manage.py makemigrations chat livestream
python manage.py migrate
```

### Redis Connection Errors

**Symptom:** `Error 111 connecting to localhost:6379`

**Solutions:**
1. **Start Redis:**
   ```bash
   sudo systemctl start redis  # Linux
   brew services start redis    # Mac
   ```

2. **Check Redis port:**
   ```bash
   redis-cli -p 6379 ping
   ```

3. **Update .env if using different port:**
   ```env
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

### Development Without Redis

If you can't install Redis, use in-memory channel layer (single-server only):

**Edit `djangolms/settings.py`:**
```python
# Comment out Redis config
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         ...
#     }
# }

# Add this instead:
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

**⚠️ Warning:** In-memory layer doesn't work with multiple servers or workers!

---

## 🚀 Production Deployment

### Required Services

1. **PostgreSQL Database**
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/djangolms
   ```

2. **Redis Server**
   ```env
   REDIS_HOST=your-redis-host
   REDIS_PORT=6379
   ```

3. **ASGI Server (Daphne or Uvicorn)**

4. **Reverse Proxy (Nginx)**

### Nginx Configuration

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # HTTP to HTTPS redirect
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Static files
    location /static/ {
        alias /path/to/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /path/to/media/;
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Regular HTTP
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service

**Create `/etc/systemd/system/djangolms.service`:**

```ini
[Unit]
Description=Django LMS ASGI Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/django-lms
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/daphne -b 127.0.0.1 -p 8000 djangolms.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable djangolms
sudo systemctl start djangolms
```

### Production Settings

**Update `.env`:**
```env
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://...
REDIS_HOST=your-redis-host
SITE_URL=https://your-domain.com
```

### Scaling Considerations

**For High Traffic:**

1. **Multiple Daphne Workers:**
   - Run multiple Daphne processes
   - Use supervisor or systemd
   - Load balance with Nginx

2. **Redis Cluster:**
   - Use Redis Sentinel or Cluster
   - For high availability

3. **CDN for Static Files:**
   - Use AWS S3 + CloudFront
   - Or other CDN service

4. **Database Read Replicas:**
   - For heavy read operations
   - Separate read/write databases

---

## 🎓 Using Alternative Streaming Services

### Option 1: Agora.io

```html
<!-- Replace Jitsi in stream_view.html -->
<script src="https://download.agora.io/sdk/release/AgoraRTC_N-4.18.0.js"></script>
<script>
const client = AgoraRTC.createClient({ mode: "live", codec: "vp8" });
await client.join(APP_ID, CHANNEL, TOKEN, uid);
</script>
```

### Option 2: Twilio Video

```html
<script src="https://sdk.twilio.com/js/video/releases/2.27.0/twilio-video.min.js"></script>
<script>
const room = await Twilio.Video.connect(TOKEN, {
    name: 'my-room'
});
</script>
```

### Option 3: AWS IVS (Interactive Video Service)

Best for one-to-many streaming (like Twitch):
- Instructor streams via RTMP
- Students watch HLS/DASH stream
- Very scalable
- Low latency

---

## 📝 Code Architecture

### Key Files

```
djangolms/
├── chat/
│   ├── models.py           # ChatRoom, Message, UserPresence
│   ├── views.py            # HTTP views for chat
│   ├── consumers.py        # WebSocket consumer
│   ├── routing.py          # WebSocket URL routing
│   └── urls.py             # HTTP URL routing
│
├── livestream/
│   ├── models.py           # LiveStream, VideoConference, QA
│   ├── views.py            # HTTP views for streams
│   ├── consumers.py        # WebSocket consumer for streams
│   ├── routing.py          # WebSocket URL routing
│   └── urls.py             # HTTP URL routing
│
├── asgi.py                 # ASGI application config
├── settings.py             # Django settings
└── urls.py                 # Main URL config

templates/
├── chat/
│   ├── chat_home.html      # Chat room listing
│   └── chat_room.html      # Real-time chat UI
│
└── livestream/
    ├── livestream_list.html    # Browse streams
    ├── stream_view.html        # Watch stream (Jitsi)
    ├── create_stream.html      # Create new stream
    ├── stream_detail.html      # Instructor dashboard
    └── recording_view.html     # Watch recordings
```

### WebSocket Message Format

**Chat Messages:**
```json
// Incoming (client → server)
{
    "type": "message",
    "content": "Hello world",
    "reply_to": 123  // optional
}

{
    "type": "typing",
    "is_typing": true
}

// Outgoing (server → client)
{
    "type": "message",
    "message": {
        "id": 456,
        "sender_id": 1,
        "sender_name": "John Doe",
        "content": "Hello world",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

**Livestream Messages:**
```json
// Chat during stream
{
    "type": "chat",
    "message": "Great explanation!"
}

// Q&A question
{
    "type": "qa_question",
    "question": "Can you explain X?"
}

// Upvote question
{
    "type": "upvote",
    "question_id": 789
}

// Viewer count update
{
    "type": "viewer_count",
    "count": 42
}
```

---

## 🎉 Success Checklist

After setup, verify everything works:

- [ ] Redis is running (`redis-cli ping` returns PONG)
- [ ] Migrations applied successfully
- [ ] Server starts with Daphne
- [ ] Can access http://localhost:8000
- [ ] Can log in with superuser
- [ ] Can create a course
- [ ] Can create a chat room
- [ ] Chat messages send in real-time
- [ ] Typing indicators work
- [ ] Can create a livestream
- [ ] Jitsi Meet loads in stream view
- [ ] Can join video conference
- [ ] Stream Q&A works
- [ ] Stream chat works

---

## 📞 Support & Resources

### Documentation
- **Django Channels:** https://channels.readthedocs.io/
- **Jitsi Meet API:** https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe
- **Redis:** https://redis.io/documentation

### Common Issues
- Check the troubleshooting section above
- Review browser console for errors
- Check Django logs for exceptions

### Contributing
- Report bugs via GitHub issues
- Submit pull requests with improvements
- Update documentation as needed

---

## 🎯 Next Steps & Enhancements

### Potential Improvements

1. **Chat Enhancements:**
   - [ ] File attachments
   - [ ] Image uploads
   - [ ] Voice messages
   - [ ] Message reactions/emojis
   - [ ] Search messages
   - [ ] Message threading

2. **Livestream Enhancements:**
   - [ ] Stream scheduling calendar
   - [ ] Email notifications before streams
   - [ ] Automatic recording upload
   - [ ] Stream analytics dashboard
   - [ ] Breakout rooms
   - [ ] Polls during streams

3. **Mobile Optimization:**
   - [ ] Progressive Web App (PWA)
   - [ ] Mobile-optimized layouts
   - [ ] Push notifications

4. **Performance:**
   - [ ] Message pagination
   - [ ] Lazy loading
   - [ ] CDN for media
   - [ ] Database optimization

---

**Last Updated:** December 2024
**Version:** 1.0
**Author:** Alex Raza - USIU-A Capstone Project
