"""
URL configuration for djangolms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view
from djangolms.courses.search_views import global_search, search_courses, search_quizzes

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('djangolms.accounts.urls')),
    path('courses/', include('djangolms.courses.urls')),
    path('assignments/', include('djangolms.assignments.urls')),
    path('grades/', include('djangolms.grades.urls')),
    path('calendar/', include('djangolms.events.urls')),
    path('', include('djangolms.notifications.urls')),
    # New features
    path('ai/', include('djangolms.ai_assistant.urls')),
    path('chat/', include('djangolms.chat.urls')),
    path('livestream/', include('djangolms.livestream.urls')),
    # Search
    path('search/', global_search, name='global_search'),
    path('search/courses/', search_courses, name='search_courses'),
    path('search/quizzes/', search_quizzes, name='search_quizzes'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
