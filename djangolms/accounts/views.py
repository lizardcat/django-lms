from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm


def register_view(request):
    """
    Handle user registration.
    """
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the LMS.')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    """
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """
    Display and edit user profile.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# Admin-only views
def admin_required(user):
    """Check if user is admin (superuser)"""
    return user.is_authenticated and user.is_admin


@user_passes_test(admin_required)
def admin_dashboard(request):
    """
    Admin dashboard with system-wide statistics and management capabilities.
    Only accessible to superusers.
    """
    # Get statistics
    total_users = User.objects.count()
    students = User.objects.filter(role=User.Role.STUDENT).count()
    instructors = User.objects.filter(role=User.Role.INSTRUCTOR).count()
    admins = User.objects.filter(Q(is_superuser=True) | Q(role=User.Role.ADMIN)).count()

    # Recent users (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()

    # Get counts from other apps if they exist
    try:
        from djangolms.courses.models import Course
        total_courses = Course.objects.count()
        active_courses = Course.objects.filter(is_active=True).count()
    except:
        total_courses = 0
        active_courses = 0

    try:
        from djangolms.assignments.models import Assignment
        total_assignments = Assignment.objects.count()
    except:
        total_assignments = 0

    try:
        from djangolms.ai_assistant.models import AIInteraction
        ai_interactions = AIInteraction.objects.count()
        recent_ai_interactions = AIInteraction.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
    except:
        ai_interactions = 0
        recent_ai_interactions = 0

    try:
        from djangolms.livestream.models import LiveStream
        total_streams = LiveStream.objects.count()
        live_streams = LiveStream.objects.filter(status='LIVE').count()
    except:
        total_streams = 0
        live_streams = 0

    context = {
        'total_users': total_users,
        'students': students,
        'instructors': instructors,
        'admins': admins,
        'recent_users': recent_users,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_assignments': total_assignments,
        'ai_interactions': ai_interactions,
        'recent_ai_interactions': recent_ai_interactions,
        'total_streams': total_streams,
        'live_streams': live_streams,
    }

    return render(request, 'accounts/admin_dashboard.html', context)


@user_passes_test(admin_required)
def admin_users(request):
    """
    User management view for admins.
    Shows all users with ability to filter and manage.
    """
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '')

    users = User.objects.all().order_by('-date_joined')

    if role_filter:
        users = users.filter(role=role_filter)

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
        'role_choices': User.Role.choices,
    }

    return render(request, 'accounts/admin_users.html', context)


@user_passes_test(admin_required)
def admin_user_detail(request, user_id):
    """
    View and manage specific user details.
    Admins can change user roles and view detailed information.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_role':
            new_role = request.POST.get('role')
            if new_role in [choice[0] for choice in User.Role.choices]:
                user.role = new_role
                user.save()
                messages.success(request, f'User role updated to {user.get_role_display()}')

        elif action == 'toggle_active':
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f'User has been {status}')

        return redirect('admin_user_detail', user_id=user_id)

    # Get user statistics
    try:
        from djangolms.courses.models import Enrollment
        enrolled_courses = Enrollment.objects.filter(student=user).count()
    except:
        enrolled_courses = 0

    try:
        from djangolms.assignments.models import Submission
        submissions = Submission.objects.filter(student=user).count()
    except:
        submissions = 0

    try:
        from djangolms.ai_assistant.models import AIInteraction
        ai_usage = AIInteraction.objects.filter(user=user).count()
    except:
        ai_usage = 0

    context = {
        'viewed_user': user,
        'enrolled_courses': enrolled_courses,
        'submissions': submissions,
        'ai_usage': ai_usage,
        'role_choices': User.Role.choices,
    }

    return render(request, 'accounts/admin_user_detail.html', context)
