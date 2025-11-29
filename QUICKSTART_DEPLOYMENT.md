# Quick Start Deployment Guide

This is a condensed version of the full deployment guide for getting the Django LMS running on Dreamhost VPS quickly.

## Prerequisites

- Dreamhost VPS with SSH access
- Domain name pointed to VPS
- Root/sudo access

## Quick Setup Steps

### 1. Initial System Setup (5 minutes)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    nginx postgresql postgresql-contrib redis-server git supervisor
```

### 2. Database Setup (2 minutes)

```bash
sudo -u postgres psql -c "CREATE DATABASE django_lms;"
sudo -u postgres psql -c "CREATE USER django_lms_user WITH PASSWORD 'ChangeThisPassword123!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE django_lms TO django_lms_user;"
```

### 3. Deploy Application (5 minutes)

```bash
# Create directory
sudo mkdir -p /var/www/django-lms
sudo chown $USER:$USER /var/www/django-lms
cd /var/www/django-lms

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment (3 minutes)

```bash
# Copy production env template
cp .env.production.example .env

# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env file
nano .env
```

**Required .env settings:**
```env
SECRET_KEY=<paste-generated-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://django_lms_user:ChangeThisPassword123!@localhost:5432/django_lms

# Email (use Gmail for quick setup)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Initialize Django (3 minutes)

```bash
# Create directories
mkdir -p logs staticfiles media

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Create sample data (optional)
python manage.py create_sample_data
```

### 6. Configure Supervisor (5 minutes)

Copy and paste these three configuration files:

**Gunicorn:**
```bash
sudo tee /etc/supervisor/conf.d/django-lms-gunicorn.conf > /dev/null <<EOF
[program:django-lms-gunicorn]
command=/var/www/django-lms/venv/bin/gunicorn djangolms.wsgi:application -c /var/www/django-lms/gunicorn_config.py
directory=/var/www/django-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/django-lms/logs/gunicorn-supervisor.log
EOF
```

**Daphne (WebSockets):**
```bash
sudo tee /etc/supervisor/conf.d/django-lms-daphne.conf > /dev/null <<EOF
[program:django-lms-daphne]
command=/var/www/django-lms/venv/bin/daphne -b 127.0.0.1 -p 8001 djangolms.asgi:application
directory=/var/www/django-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/django-lms/logs/daphne-supervisor.log
EOF
```

**Celery:**
```bash
sudo tee /etc/supervisor/conf.d/django-lms-celery.conf > /dev/null <<EOF
[program:django-lms-celery]
command=/var/www/django-lms/venv/bin/celery -A djangolms worker -l info
directory=/var/www/django-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/django-lms/logs/celery-supervisor.log
EOF
```

**Start services:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

### 7. Configure Nginx (5 minutes)

```bash
sudo tee /etc/nginx/sites-available/django-lms > /dev/null <<'EOF'
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

    location /static/ {
        alias /var/www/django-lms/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/django-lms/media/;
        expires 7d;
    }

    location /ws/ {
        proxy_pass http://django_asgi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

**Replace `your-domain.com` with your actual domain:**
```bash
sudo sed -i 's/your-domain.com/actual-domain.com/g' /etc/nginx/sites-available/django-lms
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/django-lms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL Certificate (2 minutes)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 9. Set Permissions (1 minute)

```bash
sudo chown -R www-data:www-data /var/www/django-lms
sudo chmod -R 755 /var/www/django-lms
sudo chmod -R 775 /var/www/django-lms/media
sudo chmod -R 775 /var/www/django-lms/logs
```

### 10. Configure Firewall (1 minute)

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## Verification

1. Visit `https://your-domain.com` - Should see landing page
2. Visit `https://your-domain.com/admin/` - Should see admin login
3. Check services: `sudo supervisorctl status` - All should be RUNNING

## Common Commands

```bash
# View logs
tail -f /var/www/django-lms/logs/gunicorn-error.log
tail -f /var/www/django-lms/logs/daphne-supervisor.log

# Restart services
sudo supervisorctl restart all

# Update deployment
cd /var/www/django-lms
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart all
```

## Troubleshooting

**502 Bad Gateway:**
```bash
sudo supervisorctl status  # Check if services are running
tail -f /var/www/django-lms/logs/gunicorn-error.log
```

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
sudo supervisorctl restart django-lms-gunicorn
```

**Database errors:**
```bash
sudo systemctl status postgresql
# Check DATABASE_URL in .env file
```

## Next Steps

1. Create instructor accounts in admin panel
2. Configure email settings for production
3. Set up automated backups
4. Monitor logs for errors
5. Configure domain DNS properly

For full documentation, see `DEPLOYMENT.md`
