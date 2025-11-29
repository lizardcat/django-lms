#!/bin/bash

# Django LMS Deployment Script
# This script automates the deployment process for updates

set -e  # Exit on error

echo "Starting Django LMS deployment..."

# Navigate to project directory
cd /var/www/django-lms

# Pull latest changes
echo "Pulling latest code from repository..."
git pull origin main

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --upgrade

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart services
echo "Restarting application services..."
sudo supervisorctl restart django-lms-gunicorn
sudo supervisorctl restart django-lms-daphne
sudo supervisorctl restart django-lms-celery

# Check service status
echo "Checking service status..."
sudo supervisorctl status

echo "Deployment completed successfully!"
echo "Site should be live at your domain."
