# Django LMS Deployment Guide for Dreamhost VPS

## Prerequisites

Before deploying, ensure you have:
- SSH access to your Dreamhost VPS
- Root or sudo privileges
- Domain name pointed to your VPS IP address

## 1. Initial VPS Setup

### Update system packages
```bash
sudo apt update
sudo apt upgrade -y
```

### Install required system packages
```bash
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib redis-server git supervisor
```

## 2. Database Setup (PostgreSQL)

### Create database and user
```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE django_lms;
CREATE USER django_lms_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE django_lms_user SET client_encoding TO 'utf8';
ALTER ROLE django_lms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_lms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE django_lms TO django_lms_user;
\q
```

## 3. Redis Setup

Redis should start automatically. Verify:
```bash
sudo systemctl status redis-server
sudo systemctl enable redis-server
```

## 4. Application Setup

### Create application directory
```bash
sudo mkdir -p /var/www/django-lms
sudo chown $USER:$USER /var/www/django-lms
cd /var/www/django-lms
```

### Clone repository
```bash
git clone <your-repo-url> .
# Or if you're pushing from local:
# On your local machine: git remote add production user@your-vps-ip:/var/www/django-lms/.git
```

### Create virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

## 5. Environment Configuration

### Create production .env file
```bash
nano /var/www/django-lms/.env
```

Add the following (replace with your actual values):
```env
# Django settings
SECRET_KEY=your_very_long_random_secret_key_here_generate_with_python
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-vps-ip

# Database
DATABASE_URL=postgresql://django_lms_user:your_secure_password_here@localhost:5432/django_lms

# Redis
REDIS_URL=redis://localhost:6379/0

# Email settings (configure with actual SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# AI API Keys (optional - only if using AI features)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Static and media
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/var/www/django-lms/staticfiles
MEDIA_ROOT=/var/www/django-lms/media
```

### Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 6. Update Django Settings for Production

Edit `djangolms/settings.py`:

```python
# Add at the top
import os
from pathlib import Path
import dj_database_url

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_DIR / 'staticfiles')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')

# Database
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600
        )
    }
```

## 7. Run Migrations and Collect Static Files

```bash
cd /var/www/django-lms
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create static files directory
mkdir -p staticfiles media

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

## 8. Configure Gunicorn (WSGI Server)

### Create Gunicorn configuration
```bash
nano /var/www/django-lms/gunicorn_config.py
```

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
accesslog = "/var/www/django-lms/logs/gunicorn-access.log"
errorlog = "/var/www/django-lms/logs/gunicorn-error.log"
loglevel = "info"
```

### Create Daphne configuration for WebSockets (ASGI)
```bash
nano /var/www/django-lms/daphne_config.py
```

```python
# Daphne configuration for ASGI/WebSocket support
# Run with: daphne -b 127.0.0.1 -p 8001 djangolms.asgi:application
```

### Create logs directory
```bash
mkdir -p /var/www/django-lms/logs
```

## 9. Configure Supervisor (Process Management)

### Create Gunicorn supervisor config
```bash
sudo nano /etc/supervisor/conf.d/django-lms-gunicorn.conf
```

```ini
[program:django-lms-gunicorn]
command=/var/www/django-lms/venv/bin/gunicorn djangolms.wsgi:application -c /var/www/django-lms/gunicorn_config.py
directory=/var/www/django-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/django-lms/logs/gunicorn-supervisor.log
```

### Create Daphne supervisor config (for WebSockets)
```bash
sudo nano /etc/supervisor/conf.d/django-lms-daphne.conf
```

```ini
[program:django-lms-daphne]
command=/var/www/django-lms/venv/bin/daphne -b 127.0.0.1 -p 8001 djangolms.asgi:application
directory=/var/www/django-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/django-lms/logs/daphne-supervisor.log
```

### Create Celery worker supervisor config
```bash
sudo nano /etc/supervisor/conf.d/django-lms-celery.conf
```

```ini
[program:django-lms-celery]
command=/var/www/django-lms/venv/bin/celery -A djangolms worker -l info
directory=/var/www/django-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/django-lms/logs/celery-supervisor.log
```

### Update supervisor and start services
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

## 10. Configure Nginx

### Create Nginx site configuration
```bash
sudo nano /etc/nginx/sites-available/django-lms
```

```nginx
upstream django_app {
    server 127.0.0.1:8000;
}

upstream django_asgi {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 100M;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /var/www/django-lms/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/django-lms/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://django_asgi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Django application
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Enable site and restart Nginx
```bash
sudo ln -s /etc/nginx/sites-available/django-lms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 11. SSL Certificate (Let's Encrypt)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Certbot will automatically configure Nginx for HTTPS and set up auto-renewal.

## 12. Set Correct Permissions

```bash
sudo chown -R www-data:www-data /var/www/django-lms
sudo chmod -R 755 /var/www/django-lms
sudo chmod -R 775 /var/www/django-lms/media
sudo chmod -R 775 /var/www/django-lms/logs
```

## 13. Firewall Configuration

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## 14. Create Sample Data (Optional)

```bash
cd /var/www/django-lms
source venv/bin/activate
python manage.py create_sample_data
```

## 15. Monitoring and Maintenance

### View logs
```bash
# Gunicorn logs
tail -f /var/www/django-lms/logs/gunicorn-access.log
tail -f /var/www/django-lms/logs/gunicorn-error.log

# Daphne logs
tail -f /var/www/django-lms/logs/daphne-supervisor.log

# Celery logs
tail -f /var/www/django-lms/logs/celery-supervisor.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart services
```bash
# Restart Django application
sudo supervisorctl restart django-lms-gunicorn
sudo supervisorctl restart django-lms-daphne
sudo supervisorctl restart django-lms-celery

# Restart Nginx
sudo systemctl restart nginx
```

### Update deployment
```bash
cd /var/www/django-lms
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart all
```

## 16. Backup Strategy

### Database backup script
```bash
nano /var/www/django-lms/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/www/django-lms/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U django_lms_user -h localhost django_lms > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

```bash
chmod +x /var/www/django-lms/backup_db.sh
```

### Add to crontab for daily backups
```bash
crontab -e
```

Add:
```
0 2 * * * /var/www/django-lms/backup_db.sh
```

## Troubleshooting

### Check service status
```bash
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### Check if ports are listening
```bash
sudo netstat -tulpn | grep -E '8000|8001'
```

### Test Django configuration
```bash
cd /var/www/django-lms
source venv/bin/activate
python manage.py check --deploy
```

### Common issues

**502 Bad Gateway**: Gunicorn/Daphne not running
- Check supervisor status: `sudo supervisorctl status`
- Check logs in `/var/www/django-lms/logs/`

**Static files not loading**: Run collectstatic
```bash
python manage.py collectstatic --noinput
```

**Database connection errors**: Check PostgreSQL and DATABASE_URL in .env

**WebSocket connection failed**: Check Daphne is running and Nginx WebSocket config

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY generated
- [ ] PostgreSQL password is secure
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SSL certificate installed
- [ ] Firewall configured (ufw)
- [ ] Regular backups scheduled
- [ ] File permissions set correctly
- [ ] Redis protected (bind to localhost)
- [ ] Email credentials secured

## Next Steps

1. Access admin panel: https://your-domain.com/admin/
2. Create instructor accounts
3. Create courses and enroll students
4. Configure email settings for notifications
5. Set up monitoring (optional: Sentry, New Relic)
6. Configure backup strategy
7. Set up staging environment for testing updates

## Production URLs

- **Main site**: https://your-domain.com
- **Admin panel**: https://your-domain.com/admin/
- **API endpoints**: https://your-domain.com/api/
- **WebSocket**: wss://your-domain.com/ws/
