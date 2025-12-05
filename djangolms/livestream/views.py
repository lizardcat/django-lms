from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from djangolms.courses.models import Course, Enrollment
from .models import LiveStream, StreamViewer, StreamRecording, QAQuestion, StreamChat, VideoConference


@login_required
def livestream_list(request):
    """List all livestreams for user's courses"""
    # Get user's courses
    if request.user.role == 'STUDENT':
        enrollments = Enrollment.objects.filter(
            student=request.user,
            status='ENROLLED'
        ).select_related('course')
        user_courses = [e.course for e in enrollments]
    else:
        # Instructors get their teaching courses (including draft courses)
        user_courses = list(Course.objects.filter(instructor=request.user))

    # Get live streams
    live_streams = LiveStream.objects.filter(
        course__in=user_courses,
        status='LIVE'
    ).select_related('course', 'instructor')

    # Get scheduled streams
    scheduled_streams = LiveStream.objects.filter(
        course__in=user_courses,
        status='SCHEDULED',
        scheduled_start__gte=timezone.now()
    ).select_related('course', 'instructor').order_by('scheduled_start')

    # Get past streams with recordings
    past_streams = LiveStream.objects.filter(
        course__in=user_courses,
        status='ENDED'
    ).select_related('course', 'instructor', 'recording').order_by('-actual_end')[:20]

    # Check if user is an instructor
    is_instructor = request.user.role == 'INSTRUCTOR'

    context = {
        'live_streams': live_streams,
        'scheduled_streams': scheduled_streams,
        'past_streams': past_streams,
        'user_courses': user_courses,
        'is_instructor': is_instructor,
    }

    return render(request, 'livestream/livestream_list.html', context)


@login_required
def stream_view(request, stream_id):
    """View a livestream"""
    stream = get_object_or_404(LiveStream, id=stream_id)

    # Check access
    has_access = False

    if request.user.role == 'INSTRUCTOR':
        # Instructors can view their own streams
        if stream.instructor == request.user:
            has_access = True
    else:
        # Students must be enrolled
        if Enrollment.objects.filter(student=request.user, course=stream.course, status='ENROLLED').exists():
            has_access = True

    if not has_access:
        messages.error(request, "You don't have access to this livestream.")
        return redirect('livestream:livestream_list')

    # Get Q&A questions
    qa_questions = QAQuestion.objects.filter(stream=stream).select_related('user', 'answered_by').order_by('-is_pinned', '-upvotes', '-created_at')

    # Get recent chat messages
    chat_messages = StreamChat.objects.filter(
        stream=stream,
        is_deleted=False
    ).select_related('user').order_by('-created_at')[:50]

    chat_messages = list(reversed(chat_messages))

    context = {
        'stream': stream,
        'qa_questions': qa_questions,
        'chat_messages': chat_messages,
        'is_instructor': request.user == stream.instructor,
        'jitsi_domain': settings.JITSI_DOMAIN,
        'jitsi_external_api_url': settings.JITSI_EXTERNAL_API_URL,
    }

    return render(request, 'livestream/stream_view.html', context)


@login_required
def create_stream(request, course_id):
    """Create a new livestream"""
    course = get_object_or_404(Course, id=course_id)

    # Only instructors can create streams
    if course.instructor != request.user:
        messages.error(request, "Only the course instructor can create livestreams.")
        return redirect('courses:course_detail', course_id=course.id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        scheduled_start = request.POST.get('scheduled_start')
        scheduled_end = request.POST.get('scheduled_end')
        allow_chat = request.POST.get('allow_chat') == 'on'
        allow_qa = request.POST.get('allow_qa') == 'on'
        enable_recording = request.POST.get('enable_recording') == 'on'

        # Validate required fields
        if not title:
            messages.error(request, "Title is required.")
            return redirect('livestream:create_stream', course_id=course.id)

        if len(title) > 200:
            messages.error(request, "Title is too long (maximum 200 characters).")
            return redirect('livestream:create_stream', course_id=course.id)

        # Validate dates
        if not scheduled_start or not scheduled_end:
            messages.error(request, "Start and end times are required.")
            return redirect('livestream:create_stream', course_id=course.id)

        try:
            from django.utils.dateparse import parse_datetime

            start_dt = parse_datetime(scheduled_start)
            end_dt = parse_datetime(scheduled_end)

            if not start_dt or not end_dt:
                raise ValueError("Invalid date format")

            # Make datetimes timezone-aware if they're naive
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)

            if end_dt <= start_dt:
                messages.error(request, "End time must be after start time.")
                return redirect('livestream:create_stream', course_id=course.id)

            if start_dt < timezone.now():
                messages.error(request, "Start time cannot be in the past.")
                return redirect('livestream:create_stream', course_id=course.id)
        except (ValueError, AttributeError) as e:
            messages.error(request, "Invalid date format. Please use the datetime picker.")
            return redirect('livestream:create_stream', course_id=course.id)

        # Create Jitsi video conference for actual streaming
        video_conference = VideoConference.objects.create(
            course=course,
            host=request.user,
            title=title,
            description=description,
            scheduled_start=start_dt,
            scheduled_end=end_dt,
            enable_recording=enable_recording,
            restrict_to_course=True,
            max_participants=1000
        )

        # Create livestream linked to the video conference
        stream = LiveStream.objects.create(
            course=course,
            instructor=request.user,
            title=title,
            description=description,
            scheduled_start=start_dt,
            scheduled_end=end_dt,
            allow_chat=allow_chat,
            allow_qa=allow_qa,
            enable_recording=enable_recording,
            video_conference=video_conference
        )

        messages.success(request, f"Livestream '{title}' created successfully! Join via Jitsi Meet when it's time to start.")
        return redirect('livestream:stream_detail', stream_id=stream.id)

    context = {
        'course': course,
    }

    return render(request, 'livestream/create_stream.html', context)


@login_required
def stream_detail(request, stream_id):
    """Stream detail and management page (for instructors)"""
    stream = get_object_or_404(LiveStream, id=stream_id)

    # Only instructor can access this page
    if stream.instructor != request.user:
        messages.error(request, "Access denied.")
        return redirect('livestream:stream_view', stream_id=stream.id)

    # Get viewer stats
    total_viewers = StreamViewer.objects.filter(stream=stream).count()
    current_viewers = StreamViewer.objects.filter(stream=stream, is_currently_watching=True).count()

    # Get Q&A stats
    total_questions = QAQuestion.objects.filter(stream=stream).count()
    unanswered_questions = QAQuestion.objects.filter(stream=stream, is_answered=False).count()

    context = {
        'stream': stream,
        'total_viewers': total_viewers,
        'current_viewers': current_viewers,
        'total_questions': total_questions,
        'unanswered_questions': unanswered_questions,
    }

    return render(request, 'livestream/stream_detail.html', context)


@require_POST
@login_required
def start_stream(request, stream_id):
    """Start a livestream"""
    stream = get_object_or_404(LiveStream, id=stream_id)

    if stream.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if stream.status != 'SCHEDULED':
        return JsonResponse({'error': 'Stream is not scheduled'}, status=400)

    stream.status = 'LIVE'
    stream.actual_start = timezone.now()
    stream.save()

    messages.success(request, "Livestream started!")
    return JsonResponse({'success': True, 'status': 'LIVE'})


@require_POST
@login_required
def end_stream(request, stream_id):
    """End a livestream"""
    stream = get_object_or_404(LiveStream, id=stream_id)

    if stream.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if stream.status != 'LIVE':
        return JsonResponse({'error': 'Stream is not live'}, status=400)

    stream.status = 'ENDED'
    stream.actual_end = timezone.now()
    stream.save()

    # End all active viewers
    StreamViewer.objects.filter(stream=stream, is_currently_watching=True).update(
        is_currently_watching=False,
        left_at=timezone.now()
    )

    messages.success(request, "Livestream ended!")
    return JsonResponse({'success': True, 'status': 'ENDED'})


@require_POST
@login_required
def answer_question(request, question_id):
    """Answer a Q&A question"""
    question = get_object_or_404(QAQuestion, id=question_id)

    # Only instructor can answer
    if question.stream.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    answer_text = request.POST.get('answer', '').strip()

    if not answer_text:
        return JsonResponse({'error': 'Answer cannot be empty'}, status=400)

    question.is_answered = True
    question.answer = answer_text
    question.answered_by = request.user
    question.answered_at = timezone.now()
    question.save()

    return JsonResponse({
        'success': True,
        'answer': answer_text,
        'answered_at': question.answered_at.isoformat()
    })


@require_POST
@login_required
def pin_question(request, question_id):
    """Pin a Q&A question"""
    question = get_object_or_404(QAQuestion, id=question_id)

    # Only instructor can pin
    if question.stream.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    question.is_pinned = not question.is_pinned
    question.save()

    return JsonResponse({'success': True, 'is_pinned': question.is_pinned})


@require_POST
@login_required
def upload_recording(request, stream_id):
    """Upload a recording for a livestream"""
    stream = get_object_or_404(LiveStream, id=stream_id)

    # Only instructor can upload recordings
    if stream.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if 'recording' not in request.FILES:
        return JsonResponse({'error': 'No recording file provided'}, status=400)

    recording_file = request.FILES['recording']

    # Validate file type (should be video)
    allowed_types = ['video/webm', 'video/mp4', 'video/x-matroska']
    if recording_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type. Must be video.'}, status=400)

    # Calculate file size in MB
    file_size_mb = recording_file.size / (1024 * 1024)

    # Create or update recording
    recording, created = StreamRecording.objects.get_or_create(
        stream=stream,
        defaults={
            'title': stream.title,
            'description': stream.description,
            'video_file': recording_file,
            'file_size_mb': round(file_size_mb, 2),
            'is_public': False,
            'processed_at': timezone.now()
        }
    )

    if not created:
        # Update existing recording
        recording.video_file = recording_file
        recording.file_size_mb = round(file_size_mb, 2)
        recording.processed_at = timezone.now()
        recording.save()

    return JsonResponse({
        'success': True,
        'recording_id': recording.id,
        'message': 'Recording uploaded successfully'
    })


@login_required
def recording_view(request, recording_id):
    """View a recorded livestream"""
    recording = get_object_or_404(StreamRecording, id=recording_id)
    stream = recording.stream

    # Check access
    has_access = False

    if recording.is_public:
        has_access = True
    elif request.user.role == 'INSTRUCTOR' and stream.instructor == request.user:
        has_access = True
    elif Enrollment.objects.filter(student=request.user, course=stream.course, status='ENROLLED').exists():
        has_access = True

    if not has_access:
        messages.error(request, "You don't have access to this recording.")
        return redirect('livestream:livestream_list')

    # Increment view count atomically to prevent race conditions
    from django.db.models import F
    StreamRecording.objects.filter(id=recording.id).update(view_count=F('view_count') + 1)
    recording.refresh_from_db()  # Refresh to get updated value

    context = {
        'recording': recording,
        'stream': stream,
    }

    return render(request, 'livestream/recording_view.html', context)


@require_POST
@login_required
def delete_recording(request, recording_id):
    """Delete a recording"""
    recording = get_object_or_404(StreamRecording, id=recording_id)
    stream = recording.stream

    # Only instructor who owns the stream can delete recordings
    if stream.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    try:
        # Delete the video file from storage if it exists
        if recording.video_file:
            recording.video_file.delete(save=False)

        # Delete the recording from database
        recording.delete()

        messages.success(request, "Recording deleted successfully!")
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
