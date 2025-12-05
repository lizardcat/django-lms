# 🎥 Jitsi Livestream Integration Guide

## Overview

Your Django LMS now has **real video streaming** capability using Jitsi Meet! When instructors create a livestream, a Jitsi video conference is automatically created and embedded directly in the page.

## ✅ What Was Implemented

### 1. **Automatic Jitsi Room Creation**
- When you create a livestream, a Jitsi video conference is automatically created
- Each livestream gets a unique Jitsi room (e.g., `usiu-lms-a1b2c3d4e5f6`)
- The room is linked to the livestream and reused for the same session

### 2. **Embedded Video Player**
- When the stream goes LIVE, Jitsi Meet embeds directly in the page
- No need to open external windows
- Full video conferencing experience built-in

### 3. **Role-Based Controls**

**Instructors Get:**
- Full control panel
- Screen sharing
- Recording capabilities
- Mute all participants
- Livestreaming to YouTube (if configured)
- Video background blur
- Full device settings

**Students Get:**
- Basic controls (mic, camera)
- Raise hand feature
- Video quality adjustment
- Full screen mode
- Video background blur

### 4. **Features Included**
✅ Video and audio streaming
✅ Screen sharing
✅ Recording (via Jitsi)
✅ Chat integration
✅ Q&A system
✅ Participant management
✅ Mobile support
✅ Auto-start/end times
✅ Countdown timer

## 🚀 How to Use

### For Instructors

#### 1. **Create a Livestream**
```
1. Go to your course
2. Click "Create Livestream"
3. Fill in:
   - Title (e.g., "Week 5 Lecture: Data Structures")
   - Description
   - Start time
   - End time
   - Enable/disable chat, Q&A, recording
4. Click "Create Livestream"
```

A Jitsi room is automatically created and linked!

#### 2. **Start Your Stream**
```
Option A: When it's time to start
1. Go to the livestream page
2. Click "Join Jitsi Meeting" (appears before start time)
3. Your browser opens Jitsi
4. Mark stream as LIVE in the dashboard

Option B: Direct embedding
1. Mark stream as LIVE
2. Students see embedded Jitsi on the page
3. They can join directly
```

#### 3. **During the Stream**
- **Share your screen** - Click the screen share button
- **Record** - Click record button (may require Jitsi account)
- **Answer Q&A** - Use the Q&A tab on the right
- **Manage chat** - Monitor the chat tab
- **Mute participants** - Use mute-all if needed

#### 4. **End the Stream**
```
1. Click "End Stream" button
2. Stream status changes to ENDED
3. Recording link available (if recorded)
```

### For Students

#### 1. **Join a Live Stream**
```
1. Go to Livestreams page
2. See LIVE streams at the top
3. Click "Join Stream"
4. Jitsi player loads automatically
5. Allow camera/mic permissions
6. Start participating!
```

#### 2. **During the Stream**
- **Ask questions** - Use Q&A tab
- **Chat** - Use Chat tab
- **Raise hand** - Use raise hand button
- **Toggle camera/mic** - Control buttons at bottom

#### 3. **Watch Recordings**
```
1. Go to Livestreams page
2. Scroll to "Recordings" section
3. Click "Watch Recording"
4. Video plays (if recording was enabled)
```

## 🔧 Technical Details

### How It Works

1. **LiveStream Model** has a `video_conference` field
2. **VideoConference** automatically created with unique room name
3. **Jitsi Meet** uses the room name to create/join meeting
4. **Template** embeds Jitsi via JavaScript API
5. **WebSockets** handle chat/Q&A in real-time

### Room Naming Convention
```
Format: usiu-lms-{12 random chars}
Example: usiu-lms-a1b2c3d4e5f6

This ensures unique rooms that don't collide
```

### Jitsi Configuration

**Current Setup:**
- Using public Jitsi servers (meet.jit.si)
- Free, no account needed
- No bandwidth costs
- Works globally

**Customization Options:**
```javascript
// In stream_view.html, you can customize:
configOverwrite: {
    startWithAudioMuted: true/false,
    startWithVideoMuted: true/false,
    enableWelcomePage: false,
    prejoinPageEnabled: false,
    // ... more options
}
```

## 🎬 Features Breakdown

### 1. **Video Streaming**
- Real-time video/audio
- Adaptive bitrate (adjusts to connection)
- HD quality when possible
- Mobile-friendly

### 2. **Screen Sharing**
- Share entire screen
- Share specific window
- Share Chrome tab
- Include audio from tab

### 3. **Recording**
- Click to start/stop recording
- Recordings stored by Jitsi
- Download link provided
- Can integrate with your own storage

### 4. **Chat Integration**
- Two chats: Jitsi built-in + LMS chat
- LMS chat persists after stream ends
- Jitsi chat for real-time during stream
- Both visible side-by-side

### 5. **Q&A System**
- Students ask questions
- Upvote important questions
- Instructor answers in real-time
- Persistent Q&A history

## 🔒 Security & Privacy

### Access Control
- Only enrolled students can join
- Instructor verification required
- Course-based restrictions
- Can add password protection

### Privacy Features
```python
# In VideoConference model:
restrict_to_course = True  # Only enrolled students
enable_lobby = False       # Can enable waiting room
require_password = False   # Can require password
```

## ⚙️ Configuration Options

### Enable/Disable Features

**In create_stream form:**
- ✅ Enable live chat
- ✅ Enable Q&A
- ✅ Enable recording

**In Jitsi settings:**
- Screen sharing
- Recording
- Reactions/emojis
- Virtual backgrounds

### Customize Appearance

**Edit `templates/livestream/stream_view.html`:**

```javascript
// Change Jitsi toolbar buttons
TOOLBAR_BUTTONS: [
    'microphone', 'camera', 'desktop',
    'fullscreen', 'hangup', 'recording',
    // Add or remove as needed
]

// Change interface config
SHOW_JITSI_WATERMARK: false  // Hide Jitsi logo
DEFAULT_REMOTE_DISPLAY_NAME: 'Student'
```

## 📊 Monitoring & Analytics

### Available Metrics
- Current viewers count
- Peak viewers
- Total views
- Stream duration
- Q&A engagement
- Chat activity

### Tracking Implementation
```python
# StreamViewer model tracks:
- Who joined
- When they joined
- How long they watched
- Currently watching status
```

## 🌐 Self-Hosting Jitsi (Optional)

For more control, you can host your own Jitsi server:

### Benefits
- Custom branding
- Unlimited recording storage
- Better performance
- Full control over data
- Custom features

### Quick Setup
```bash
# On Ubuntu server:
wget https://download.jitsi.org/jitsi-key.gpg.key
sudo apt-key add jitsi-key.gpg.key
sudo sh -c "echo 'deb https://download.jitsi.org stable/' > /etc/apt/sources.list.d/jitsi-stable.list"
sudo apt update
sudo apt install jitsi-meet
```

Then update domain in template:
```javascript
const domain = 'your-jitsi-domain.com';  // Instead of meet.jit.si
```

## 🚨 Troubleshooting

### Issue: "Jitsi not loading"
**Solution:**
1. Check browser allows camera/mic
2. Clear browser cache
3. Try incognito mode
4. Check console for errors

### Issue: "No video showing"
**Solution:**
1. Check stream status is LIVE
2. Verify video_conference exists
3. Check JavaScript console
4. Ensure Jitsi API loaded

### Issue: "Students can't join"
**Solution:**
1. Verify enrollment status
2. Check course restrictions
3. Confirm stream is LIVE
4. Check Jitsi room name exists

### Issue: "Recording not working"
**Solution:**
1. Requires Jitsi account for public servers
2. Or use self-hosted Jitsi
3. Or integrate third-party recording
4. Check enable_recording is True

## 📝 Migration Instructions

### For Users to Apply Changes

```bash
cd C:\Users\Computer\Desktop\Code Projects\django-lms
git pull origin claude/review-livestream-chat-01W374i18o8bBnmUvKbpo1kH
venv\Scripts\activate
python manage.py migrate
python manage.py runserver
```

The migration adds the `video_conference` field to LiveStream model.

## 🎯 Next Steps

### Recommended Enhancements

1. **Recording Storage**
   - Integrate with AWS S3 or similar
   - Auto-upload recordings
   - Generate playback URLs

2. **Advanced Analytics**
   - Track student engagement
   - Generate attendance reports
   - Measure interaction metrics

3. **Custom Branding**
   - Self-host Jitsi
   - Add school logo
   - Custom color scheme

4. **Mobile App**
   - Native iOS/Android apps
   - Push notifications for streams
   - Offline recording viewing

5. **Integration Features**
   - Calendar sync
   - Email reminders
   - Automated transcripts
   - AI-generated summaries

## 📞 Support

If you encounter issues:

1. Check browser console for errors
2. Verify migrations were run
3. Test with different browsers
4. Check network/firewall settings

## 🎉 Summary

You now have a **fully functional video streaming system** using Jitsi Meet!

**What works:**
✅ Create livestreams with scheduled times
✅ Auto-generate unique Jitsi rooms
✅ Embed video directly in page
✅ Screen sharing and recording
✅ Real-time chat and Q&A
✅ Role-based access controls
✅ Mobile-friendly interface

**No additional setup required** - it works out of the box with public Jitsi servers!

---

**Note:** Using public Jitsi servers is free but has some limitations. For production use with many concurrent users, consider self-hosting Jitsi or using a paid Jitsi service provider.
