from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import calendar as cal
from .models import Event
from djangolms.assignments.models import Assignment


@login_required
def calendar_view(request):
    """
    Main calendar view showing month view by default.
    """
    # Get current date or date from query params
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    # Create a calendar object
    calendar_obj = cal.Calendar(firstweekday=6)  # Sunday as first day
    month_days = calendar_obj.monthdatescalendar(year, month)

    # Get date range for the month (including prev/next month days shown)
    start_date = month_days[0][0]
    end_date = month_days[-1][-1]

    # Query events for this month
    events = Event.objects.filter(
        start_date__date__gte=start_date,
        start_date__date__lte=end_date
    )

    # Query assignments due in this month and convert to events
    assignments = Assignment.objects.filter(
        due_date__date__gte=start_date,
        due_date__date__lte=end_date
    )

    # Filter by user's enrolled courses for students
    if hasattr(request.user, 'role') and request.user.role == 'STUDENT':
        enrollments = request.user.enrollments.all()
        enrolled_course_ids = [e.course_id for e in enrollments]
        events = events.filter(
            Q(course_id__in=enrolled_course_ids) | Q(course__isnull=True)
        )
        assignments = assignments.filter(course_id__in=enrolled_course_ids)

    # Create a dictionary to organize events by date
    events_by_date = {}

    # Add regular events
    for event in events:
        date_key = event.start_date.date()
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append({
            'title': event.title,
            'type': event.event_type,
            'color': event.color,
            'time': event.start_date.strftime('%I:%M %p') if not event.all_day else 'All Day',
            'is_assignment': False,
            'id': event.id,
        })

    # Add assignments as events
    for assignment in assignments:
        date_key = assignment.due_date.date()
        if date_key not in events_by_date:
            events_by_date[date_key] = []

        # Color code by assignment type
        color_map = {
            'HOMEWORK': '#28a745',  # Green
            'QUIZ': '#ffc107',      # Yellow
            'PROJECT': '#17a2b8',   # Cyan
            'EXAM': '#dc3545',      # Red
            'ESSAY': '#6f42c1',     # Purple
        }

        events_by_date[date_key].append({
            'title': f"{assignment.title}",
            'type': 'ASSIGNMENT',
            'color': color_map.get(assignment.assignment_type, '#007bff'),
            'time': assignment.due_date.strftime('%I:%M %p'),
            'is_assignment': True,
            'id': assignment.id,
            'course': assignment.course.code,
        })

    # Calculate previous and next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    context = {
        'month_days': month_days,
        'events_by_date': events_by_date,
        'current_month': cal.month_name[month],
        'current_year': year,
        'current_month_num': month,
        'today': timezone.now().date(),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'events/calendar.html', context)


@login_required
def week_view(request):
    """
    Week view of the calendar.
    """
    # Get the date from query params or use today
    date_str = request.GET.get('date')
    if date_str:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        current_date = timezone.now().date()

    # Get the start of the week (Sunday)
    start_of_week = current_date - timedelta(days=current_date.weekday() + 1)
    if current_date.weekday() == 6:  # If Sunday
        start_of_week = current_date

    # Generate 7 days
    week_days = [start_of_week + timedelta(days=i) for i in range(7)]

    # Query events for this week
    end_of_week = start_of_week + timedelta(days=6)
    events = Event.objects.filter(
        start_date__date__gte=start_of_week,
        start_date__date__lte=end_of_week
    )

    # Query assignments
    assignments = Assignment.objects.filter(
        due_date__date__gte=start_of_week,
        due_date__date__lte=end_of_week
    )

    # Filter by user's courses
    if hasattr(request.user, 'role') and request.user.role == 'STUDENT':
        enrollments = request.user.enrollments.all()
        enrolled_course_ids = [e.course_id for e in enrollments]
        events = events.filter(
            Q(course_id__in=enrolled_course_ids) | Q(course__isnull=True)
        )
        assignments = assignments.filter(course_id__in=enrolled_course_ids)

    # Organize events by date
    events_by_date = {}
    for event in events:
        date_key = event.start_date.date()
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    for assignment in assignments:
        date_key = assignment.due_date.date()
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(assignment)

    context = {
        'week_days': week_days,
        'events_by_date': events_by_date,
        'current_date': current_date,
        'today': timezone.now().date(),
    }

    return render(request, 'events/week_view.html', context)


@login_required
def day_view(request):
    """
    Single day view of the calendar.
    """
    # Get the date from query params or use today
    date_str = request.GET.get('date')
    if date_str:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        current_date = timezone.now().date()

    # Query events for this day
    events = Event.objects.filter(start_date__date=current_date)

    # Query assignments
    assignments = Assignment.objects.filter(due_date__date=current_date)

    # Filter by user's courses
    if hasattr(request.user, 'role') and request.user.role == 'STUDENT':
        enrollments = request.user.enrollments.all()
        enrolled_course_ids = [e.course_id for e in enrollments]
        events = events.filter(
            Q(course_id__in=enrolled_course_ids) | Q(course__isnull=True)
        )
        assignments = assignments.filter(course_id__in=enrolled_course_ids)

    # Combine and sort by time
    all_items = []
    for event in events:
        all_items.append({
            'type': 'event',
            'time': event.start_date,
            'object': event
        })

    for assignment in assignments:
        all_items.append({
            'type': 'assignment',
            'time': assignment.due_date,
            'object': assignment
        })

    all_items.sort(key=lambda x: x['time'])

    context = {
        'current_date': current_date,
        'items': all_items,
        'today': timezone.now().date(),
    }

    return render(request, 'events/day_view.html', context)


@login_required
def event_detail(request, event_id):
    """
    Detail view for a single event.
    """
    from django.shortcuts import get_object_or_404

    event = get_object_or_404(Event, id=event_id)

    # Check if user has permission to view this event
    if hasattr(request.user, 'role') and request.user.role == 'STUDENT':
        if event.course:
            # Check if student is enrolled in the course
            is_enrolled = request.user.enrollments.filter(course=event.course).exists()
            if not is_enrolled:
                from django.contrib import messages
                messages.error(request, "You don't have permission to view this event.")
                return redirect('events:calendar')

    context = {
        'event': event,
    }

    return render(request, 'events/event_detail.html', context)
