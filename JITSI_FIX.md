# Jitsi Authentication Fix

## Problem

When instructors try to start a livestream, Jitsi's public servers (`meet.jit.si`) require authentication via GitHub or Google OAuth. This results in a **403 error** because:

1. The public Jitsi Meet server now requires authentication for creating rooms
2. The OAuth integration fails because the application isn't registered with Jitsi's OAuth providers
3. Users get "403. That's an error. We're sorry, but you do not have access to this page."

## Solution

We've switched from using `meet.jit.si` to `8x8.vc`, which is Jitsi's official domain that works better for embedded use cases and doesn't require authentication for basic usage.

### Changes Made

1. **Added Jitsi configuration to Django settings** (`djangolms/settings.py`):
   ```python
   JITSI_DOMAIN = os.getenv('JITSI_DOMAIN', '8x8.vc')
   JITSI_EXTERNAL_API_URL = os.getenv('JITSI_EXTERNAL_API_URL', f'https://{JITSI_DOMAIN}/external_api.js')
   ```

2. **Updated the livestream view** (`djangolms/livestream/views.py`):
   - Added Jitsi configuration to the context passed to templates
   - Now uses configurable Jitsi domain instead of hardcoded values

3. **Updated the stream view template** (`templates/livestream/stream_view.html`):
   - Changed from `meet.jit.si` to use the configured `{{ jitsi_domain }}`
   - Added additional configuration options to disable authentication prompts:
     - `enableUserRolesBasedOnToken: false`
     - `enableInsecureRoomNameWarning: false`
     - `requireDisplayName: false`

4. **Updated environment configuration files**:
   - Added `JITSI_DOMAIN` to `.env.example`
   - Added `JITSI_DOMAIN` to `.env.production.example`

## How to Use

### Default Configuration (No Changes Needed)

The system now uses `8x8.vc` by default, which should work without any authentication issues.

### Custom Configuration

If you want to use a different Jitsi instance (e.g., self-hosted), update your `.env` file:

```env
# Use a custom Jitsi domain
JITSI_DOMAIN=jitsi.your-domain.com

# Or specify a custom external API URL
JITSI_EXTERNAL_API_URL=https://jitsi.your-domain.com/external_api.js
```

### Self-Hosting Jitsi (Recommended for Production)

For production environments, we recommend self-hosting Jitsi Meet for:
- **Privacy**: Full control over your data
- **Customization**: Complete control over features and branding
- **Reliability**: No dependency on third-party services
- **No Authentication Issues**: You control the authentication requirements

#### Quick Self-Hosting Guide

1. **Install Jitsi on Ubuntu Server**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Jitsi Meet
   wget -qO - https://download.jitsi.org/jitsi-key.gpg.key | sudo apt-key add -
   sudo sh -c "echo 'deb https://download.jitsi.org stable/' > /etc/apt/sources.list.d/jitsi-stable.list"
   sudo apt update
   sudo apt install jitsi-meet
   ```

2. **Configure SSL** (required for camera/microphone access):
   ```bash
   sudo /usr/share/jitsi-meet/scripts/install-letsencrypt-cert.sh
   ```

3. **Update your Django settings**:
   ```env
   JITSI_DOMAIN=jitsi.your-domain.com
   ```

Full guide: https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-quickstart

## Alternative: Using meet.jit.si with JWT Authentication

If you still want to use `meet.jit.si` or need secure authentication, you can implement JWT tokens:

1. Create an account at https://jaas.8x8.vc/ (Jitsi as a Service)
2. Get your API key and App ID
3. Generate JWT tokens server-side
4. Pass the token to the Jitsi configuration

This approach requires additional backend implementation but provides better security and control.

## Testing the Fix

1. **Start the development server**:
   ```bash
   python manage.py runserver
   # or with Daphne for WebSocket support:
   daphne -b 0.0.0.0 -p 8000 djangolms.asgi:application
   ```

2. **Create or join a livestream**:
   - Log in as an instructor
   - Navigate to a course
   - Create a new livestream or go to an existing one
   - Click "Start Stream"

3. **Verify**:
   - The Jitsi interface should load without any authentication prompts
   - No 403 errors should appear
   - Instructors should be able to start broadcasting immediately
   - Students should be able to join the stream

## Troubleshooting

### Issue: Still getting authentication prompts

**Solution**: Clear your browser cache and cookies for the site, then try again.

### Issue: Jitsi not loading at all

**Possible causes**:
1. **Network/Firewall**: Ensure your network allows connections to `8x8.vc`
2. **Browser issues**: Try a different browser (Chrome/Firefox recommended)
3. **HTTPS required**: Some browsers require HTTPS for camera/microphone access

### Issue: Camera/Microphone not working

**Solution**:
- Ensure you're using HTTPS (required for media access in most browsers)
- Check browser permissions for camera/microphone
- Try clicking the camera/microphone icons in the Jitsi interface

### Issue: Want to revert to meet.jit.si

You can revert by setting in your `.env`:
```env
JITSI_DOMAIN=meet.jit.si
```

Note: You may still encounter authentication issues with this domain.

## Additional Resources

- **Jitsi Meet Handbook**: https://jitsi.github.io/handbook/
- **Jitsi API Documentation**: https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe
- **8x8 Video SDK**: https://developers.8x8.com/video-sdk
- **Self-Hosting Guide**: https://jitsi.github.io/handbook/docs/devops-guide/

## Future Enhancements

Consider these improvements for your production deployment:

1. **JWT Authentication**: Implement secure token-based authentication
2. **Recording Storage**: Configure automatic recording storage to your server or S3
3. **TURN Server**: Set up your own TURN server for better NAT traversal
4. **Branding**: Customize the Jitsi interface with your institution's branding
5. **Analytics**: Integrate usage analytics for tracking engagement

## Support

If you encounter any issues with this fix, please:
1. Check the troubleshooting section above
2. Review the Jitsi logs in your browser's developer console
3. Verify your `.env` configuration
4. Test with a different browser

---

**Last Updated**: December 5, 2025
**Author**: Alex Raza
**Version**: 1.0
